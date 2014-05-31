import asyncio

from werkzeug.wrappers import Response

from galerka.util import asyncached

class View:
    _galerka_view = True

    def __init__(self, request):
        self.request = request

    @asyncio.coroutine
    def render_template(self, name, mimetype='text/html'):
        template = self.request.environ['galerka.mako'].get_template(name)
        result = yield from template.render_async(
            this=self,
            request=self.request,
        )
        return Response(result, mimetype=mimetype)


class TitlePage(View):
    @asyncached
    def title(self):
        return None

    @asyncio.coroutine
    def render(self):
        return (yield from self.render_template('base.mako'))
