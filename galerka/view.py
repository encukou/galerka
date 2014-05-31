import asyncio

from werkzeug.wrappers import Response
from markupsafe import Markup
import markdown
import textwrap

from galerka.util import asyncached, AsyncGetter


class Root:
    parent = None
    lineage = AsyncGetter([])

    def __init__(self, request, root_class):
        self.root_class = root_class
        self.request = request

    @asyncio.coroutine
    def traverse(self, pathinfo):
        if pathinfo[:1] != ['']:
            raise LookupError('Attempt to traverse above app root')
        return (yield from self.root_class(self, '').traverse(pathinfo[1:]))


class View:
    def __init__(self, parent, url_fragment, *, request=None):
        self.parent = parent
        self.request = parent.request
        if getattr(self, 'url_fragment', None) is None:
            self.url_fragment = AsyncGetter(url_fragment)

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

    @asyncached
    def path(self):
        result = yield from [(yield from parent.url_fragment)
                             for parent in (yield from self.lineage)]
        path = '/'.join(result)
        if not path:
            return '/'
        else:
            return path

    @asyncached
    def url(self):
        return (yield from self.path)

    @asyncached
    def lineage(self):
        return (yield from self.parent.lineage) + [self]

    @asyncached
    def root(self):
        return (yield from self.lineage)[-1].parent

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
        for page in (yield from self.lineage):
            result.append(Markup('<li><a href="{}">{}</a></li>').format(
                (yield from page.url),
                (yield from page.title),
            ))
        return Markup('').join(result)

    @asyncio.coroutine
    def render_template(self, name, mimetype='text/html'):
        template = self.request.environ['galerka.mako'].get_template(name)
        result = yield from template.render_async(
            this=self,
            request=self.request,
            static_url=self.request.environ['galerka.static-url'],
            root=(yield from self.root),
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
    def url(self):
        return '/test'

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
