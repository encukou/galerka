import asyncio
import markdown
import textwrap
import json
import datetime
import time

from werkzeug.wrappers import Response
from werkzeug.exceptions import BadRequest
from markupsafe import Markup

from galerka.view import GalerkaView
from galerka.views.index import TitlePage
from galerka.util import asyncached


class ShoutboxMessage:
    def __init__(self, time, author, body):
        self.time = time
        self.author = author
        self.body = body

    @classmethod
    def from_dict(cls, dict):
        return cls(
            time=datetime.datetime.utcfromtimestamp(dict['timestamp']),
            author=dict['author-name'],
            body=dict['body'],
        )


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
        return self._render_posts(2, 20, 'date')

    @asyncached
    def rendered_sidebar_posts(self):
        return self._render_posts(3, 5, 'compact')

    def _render_posts(self, header_level, number=5, date_format='compact'):
        template = self.get_template('widgets/shoutbox_post.mako')
        result = []
        posts = yield from self.request.redis.zrange('shoutbox', -number, -1)
        for post in reversed(list(posts)):
            (post, score) = yield from post
            message = ShoutboxMessage.from_dict(json.loads(post))
            result.append((yield from template.render_async(
                message=message,
                date_format=date_format,
                header_level=header_level,
            )))
        return Markup(''.join(result))

    @asyncio.coroutine
    def do_post(self):
        try:
            body = self.request.form['content']
        except KeyError:
            raise BadRequest('Post content required')
        if body.strip():
            timestamp = time.time()
            data = json.dumps({
                'timestamp': timestamp,
                'author': None,
                'author-name': self.request.environ['REMOTE_ADDR'],
                'author-url': None,
                'body': body,
            })
            yield from self.request.redis.zadd('shoutbox', {data: timestamp})
        return self.request.args.get('redirect', self.root.url)
