import markdown
import textwrap
import json

from markupsafe import Markup

from galerka.view import GalerkaView
from galerka.views.index import TitlePage
from galerka.util import asyncached


class ShoutboxMessage:
    def __init__(self, time, author, body):
        self.time = time
        self.author = author
        self.body = body


@TitlePage.child('shoutbox')
class ShoutboxPage(GalerkaView):
    @asyncached
    def title(self):
        return 'Shoutbox'

    @asyncached
    def rendered_page(self):
        return (yield from self.render_template('base.mako'))

    @asyncached
    def rendered_contents(self):
        return self._render_posts(2)

    def _render_posts(self, header_level):
        template = self.get_template('widgets/shoutbox_post.mako')
        result = []
        for post in (yield from self.request.redis.lrange('shoutbox', 0, 5)):
            post = yield from post
            message = ShoutboxMessage('(time)', '(author)', post)
            result.append((yield from template.render_async(message=message)))
        return Markup(''.join(result))

    @asyncached
    def rendered_sidebar_posts(self):
        return self._render_posts(3)
