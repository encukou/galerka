from galerka import views
from galerka.view import GalerkaView
from galerka.util import asyncached


class TitlePage(GalerkaView):
    view_packages = [views]

    @asyncached
    def title(self):
        return self.request.environ['galerka.site-title']

    @asyncached
    def rendered_contents(self):
        return 'Hello World'  # TODO
