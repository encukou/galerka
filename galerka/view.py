import asyncio

from werkzeug.wrappers import Response
from markupsafe import Markup
import markdown
import textwrap

from galerka.util import asyncached


class View:
    _galerka_view = True

    @asyncached
    def url(self):
        return '/'  # TODO

    def __init__(self, request):
        self.request = request

    @asyncached
    def lineage(self):
        result = []
        page = self
        while page:
            result.append(page)
            page = (yield from page.parent)
        return result

    @asyncached
    def rendered_hierarchy(self):
        result = []
        for page in reversed((yield from self.lineage)):
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
            static_url=lambda a: '/static/' + a,
        )
        return Response(result, mimetype=mimetype)


class TitlePage(View):
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


class TestPage(View):
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
