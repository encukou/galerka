import markdown
import textwrap

from markupsafe import Markup

from galerka.view import GalerkaView
from galerka.views.index import TitlePage
from galerka.util import asyncached


@TitlePage.child('test')
class TestPage(GalerkaView):
    @asyncached
    def title(self):
        return 'Testovací  stránka'

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
