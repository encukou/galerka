import asyncio
import pkgutil
import sys

from werkzeug.wrappers import Response
from werkzeug.utils import cached_property
from werkzeug.urls import Href
from werkzeug.exceptions import MethodNotAllowed
from markupsafe import Markup

from galerka.util import asyncached, AsyncGetter


class View:
    def __init__(self, parent, url_fragment, *, request=None):
        self.parent = parent
        self.request = request or parent.request
        if getattr(self, 'url_fragment', None) is None:
            assert isinstance(url_fragment, str)
            self.url_fragment = url_fragment

    @asyncio.coroutine
    def traverse(self, pathinfo):
        if not pathinfo:
            return self
        url_fragment = pathinfo[0]
        if url_fragment == '..':
            if self.parent:
                child = self.parent
            else:
                child = self
        elif url_fragment == '.' or not url_fragment:
            child = self
        elif url_fragment in getattr(self, 'child_classes', {}):
            child = self.child_classes[url_fragment](self, url_fragment)
        else:
            child = (yield from self.get_child(url_fragment))
        return (yield from child.traverse(pathinfo[1:]))

    def __getitem__(self, *path):
        pathinfo = []
        for fragment in path:
            if isinstance(fragment, str):
                pathinfo.extend(fragment.split('/'))
            else:
                pathinfo.append(fragment)
        return self.traverse(pathinfo)

    @asyncio.coroutine
    def get_child(self, url_fragment):
        raise LookupError(url_fragment)

    @cached_property
    def path(self):
        path = '/'.join(parent.url_fragment for parent in self.lineage)
        if not path:
            return '/'
        else:
            return path

    @cached_property
    def lineage(self):
        parent = self.parent
        if parent:
            parent_lineage = parent.lineage
        else:
            parent_lineage = ()
        return parent_lineage + (self, )

    @cached_property
    def url(self):
        return self.root.href(self.path)

    @cached_property
    def href(self):
        if self.parent:
            return getattr(self.parent.href, self.url_fragment)
        else:
            return Href(self.request.url_root)

    def static_url(self, path):
        static_files = self.request.environ['galerka.static_files']
        item = static_files[path]
        try:
            sha = item.sha
        except AttributeError:
            return self.root.href.static(path)
        else:
            return '%s?%s' % (self.root.href.static(path), sha)

    @cached_property
    def root(self):
        return self.lineage[0]

    @classmethod
    def child(cls, name):
        def decorator(child):
            try:
                child_classes = cls.child_classes
            except AttributeError:
                child_classes = cls.child_classes = {}
            child_classes[name] = child
            return child
        return decorator

    @cached_property
    def allowed_methods(self):
        methods = ('GET', 'HEAD', 'POST', 'PUT', 'DELETE', 'TRACE', 'OPTIONS')
        return [m for m in methods if getattr(self, m, None)]

    def get_response(self, method):
        method = method.upper()
        if method in self.allowed_methods:
            return getattr(self, method)
        else:
            return AsyncGetter(MethodNotAllowed(self.allowed_methods))

    @cached_property
    def HEAD(self):
        return self.GET

    @asyncached
    def OPTIONS(self):
        return Response('', headers={'Allow': ', '.join(self.allowed_methods)})

    @classmethod
    def _load_all_views(cls):
        for pkg in cls.view_packages:
            walk = pkgutil.walk_packages(pkg.__path__, pkg.__name__ + '.')
            for loader, name, is_pkg in walk:
                if name not in sys.modules:
                    module = loader.find_module(name).load_module(name)
                    yield module


class GalerkaView(View):
    @cached_property
    def GET(self):
        try:
            rendered_page = self.rendered_page
        except AttributeError:
            return None
        else:
            @asyncio.coroutine
            def get():
                rendered = yield from rendered_page
                return Response(rendered, mimetype='text/html')
            return get()

    @property
    def POST(self):
        try:
            do_post = self.do_post
        except AttributeError:
            return None
        else:
            @asyncio.coroutine
            def post():
                url = yield from do_post()
                content = Markup('''
                    <head>
                        <title>OK</title>
                    </head>
                    <body>
                        <h1>OK</h1>
                        <p>→ <a href="{}">{}</a></p>
                    </body>
                ''').format(Markup(url), url)
                return Response(content, 303, mimetype='text/html',
                                headers={'Location': url})
            return post()

    @asyncached
    def rendered_hierarchy(self):
        result = []
        for page in self.lineage:
            result.append(Markup('<li><a href="{}">{}</a></li>').format(
                page.url,
                (yield from page.title),
            ))
        return Markup('').join(result)

    def get_template(self, name):
        return self.request.environ['galerka.mako'].get_template(name)

    @asyncio.coroutine
    def render_template(self, name):
        template = self.get_template(name)
        result = yield from template.render_async(
            this=self,
            request=self.request,
            static_url=self.static_url,
            redis=self.request.redis,
        )
        return result
