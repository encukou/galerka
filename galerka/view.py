import asyncio

from werkzeug.wrappers import Response
from werkzeug.utils import cached_property
from werkzeug.urls import Href
from markupsafe import Markup
import markdown
import textwrap

from galerka.util import asyncached


class Root:
    parent = None
    lineage = ()

    def __init__(self, request, root_class):
        self.root_class = root_class
        self.request = request
        self.url = request.url_root
        self.href = Href(request.url_root)

    @asyncio.coroutine
    def traverse(self, pathinfo):
        if pathinfo[:1] != ['']:
            raise LookupError('Attempt to traverse above app root')
        return (yield from self.root_class(self, '').traverse(pathinfo[1:]))


class View:
    def __init__(self, parent, url_fragment, *, request=None):
        print(self, parent)
        self.parent = parent
        self.request = parent.request
        if getattr(self, 'url_fragment', None) is None:
            self.url_fragment = url_fragment

    @classmethod
    def _get_root(cls, request):
        return Root(request, cls)

    @asyncio.coroutine
    def traverse(self, pathinfo):
        if not pathinfo:
            return self
        url_fragment = pathinfo[0]
        if url_fragment == '..':
            return self.parent
        elif url_fragment == '.':
            return self
        elif url_fragment in getattr(self, 'child_classes', {}):
            child = self.child_classes[url_fragment](self, url_fragment)
        else:
            child = (yield from self.get_child(url_fragment))
        return (yield from child.traverse(pathinfo[1:]))

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
        return self.parent.lineage + (self, )

    @cached_property
    def url(self):
        return self.root.href(self.path)

    @cached_property
    def root(self):
        return self.lineage[0].parent

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


class GalerkaView(View):
    @asyncached
    def rendered_hierarchy(self):
        result = []
        for page in self.lineage:
            result.append(Markup('<li><a href="{}">{}</a></li>').format(
                page.url,
                (yield from page.title),
            ))
        return Markup('').join(result)

    @asyncio.coroutine
    def render_template(self, name, mimetype='text/html'):
        template = self.request.environ['galerka.mako'].get_template(name)
        result = yield from template.render_async(
            this=self,
            request=self.request,
            static_url=self.root.href.static,
        )
        return Response(result, mimetype=mimetype)


class TitlePage(GalerkaView):
    @asyncached
    def title(self):
        return self.request.environ['galerka.site-title']

    @asyncached
    def parent(self):
        return None

    @asyncached
    def rendered_page(self):
        return (yield from self.render_template('base.mako'))

    @asyncached
    def rendered_contents(self):
        return 'Hello World'


@TitlePage.child('test')
class TestPage(GalerkaView):
    @asyncached
    def title(self):
        return 'Testovací  stránka'

    @asyncached
    def parent(self):
        return TitlePage(self.request)

    @asyncached
    def rendered_page(self):
        return (yield from self.render_template('base.mako'))

    @asyncached
    def rendered_contents(self):
        return Markup(markdown.markdown(textwrap.dedent('''
            Styling test.

            # h1
            ## h2
            ### h3
            #### h4
            ##### h5
            ###### h6

            > a long
            > blockquote

            * a list
            * that's unordered

            and

            1. now one
            2. that's ordered

            and

            <dl>
                <dt>a term</dt>
                <dd>with its definition</dd>
            </dl>

            ---

            (that was an <abbr title="horizontal rule">hr</abbr>)

                here's a code block

            we have `inline code` too

            [This here](http://example.com/) is a *link*,
            You **should not** click it.

            <table>
                <thead>
                    <tr><th>A table</th><th>cell or two</th></tr>
                </thead>
                <tbody>
                    <tr><td>And more</td><td>in second row</td></tr>
                </tbody>
            </table>

            H<sub>2</sub>SO<sub>4</sub>; E=mc<sup>2</sup>

            That would be all.

            <div class="signature">Sincerely, me</div>
        ''')))
