import asyncio
import json
import datetime
import time
import traceback

from werkzeug.exceptions import BadRequest
from markupsafe import Markup
import asyncio_redis

from galerka.view import GalerkaView
from galerka.views.index import TitlePage
from galerka.util import asyncached


class CollisionError(Exception):
    '''Message timestamp collision'''


class ShoutboxMessage:
    def __init__(self, stamp, time, author, body):
        self.stamp = stamp
        self.time = time
        self.author = author
        self.body = body

    @classmethod
    def from_dict(cls, dict):
        return cls(
            stamp=dict['timestamp'],
            time=datetime.datetime.utcfromtimestamp(float(dict['timestamp'])),
            author=dict['author-name'],
            body=dict['body'],
        )


@TitlePage.child('shoutbox')
class ShoutboxPage(GalerkaView):
    @asyncached
    def title(self):
        return 'Kecadlo'

    @asyncached
    def rendered_page(self):
        return (yield from self.render_template('base.mako'))

    @asyncached
    def rendered_contents(self):
        return self._render_posts(2, 20, 'interval')

    @asyncached
    def rendered_sidebar_posts(self):
        return self._render_posts(3, 5, 'compact')

    def _render_post(self, post, header_level, date_format='compact'):
        message = ShoutboxMessage.from_dict(post)
        template = self.get_template('widgets/shoutbox_post.mako')
        post_html = yield from template.render_async(
            message=message,
            date_format=date_format,
            header_level=header_level,
        )
        return post_html

    def _render_posts(self, header_level, number=5, date_format='compact'):
        redis = yield from self.request.redis
        result = []
        start_div = Markup(
            '<div data-ws-channel="{}?header-level={}&amp;date-format={}">')
        result.append(start_div.format(
            self.path, header_level, date_format))
        posts = yield from redis.zrange(self.redis_key, -number, -1)
        for post_entry in reversed(list(posts)):
            post, score = yield from post_entry
            rendered = yield from self._render_post(
                json.loads(post),
                date_format=date_format,
                header_level=header_level
            )
            result.append(rendered)
        result.append(Markup('</div>'))
        return Markup(''.join(result))

    @asyncio.coroutine
    def do_post(self):
        try:
            body = self.request.form['content']
        except KeyError:
            raise BadRequest('Post content required')
        if body.strip():
            redis = yield from self.request.redis
            while True:
                try:
                    timestamp = time.time()
                    data = json.dumps({
                        'timestamp': str(timestamp),
                        'author': None,
                        'author-name': self.request.environ['REMOTE_ADDR'],
                        'body': body,
                    })
                    t = yield from redis.multi(watch=[self.redis_key])
                    num_dupes = yield from redis.zcount(
                        self.redis_key,
                        asyncio_redis.ZScoreBoundary(timestamp,
                                                     exclude_boundary=False),
                        asyncio_redis.ZScoreBoundary('+inf'),
                    )
                    if num_dupes:
                        raise CollisionError
                    yield from t.zadd(self.redis_key, {data: timestamp})
                    yield from t.publish(self.redis_key, data)
                    yield from t.exec()
                    self._start_trim_task(redis)
                except (asyncio_redis.TransactionError, CollisionError) as e:
                    print('Blocked!', repr(body), type(e))
                    yield from asyncio.sleep(1)
                    continue
                else:
                    print('Added!', data)
                    break
            status = '201 Created'
        else:
            data = json.dumps({
                'error': {
                    'body': 'must not be empty',
                },
            })
            status = '400 Bad Request'
        return status, data, self.request.args.get('redirect', self.root.url)

    def _start_trim_task(self, redis):
        """Starts a task to trim the chat history to a week"""
        week = 3600 * 24 * 7
        task = asyncio.Task(redis.zremrangebyscore(
            self.redis_key,
            asyncio_redis.ZScoreBoundary('-inf'),
            asyncio_redis.ZScoreBoundary(time.time() - week),
        ))

    @asyncio.coroutine
    def ws_subscribe(self, send, last_stamp=None, options=None):
        @asyncio.coroutine
        def send_reply(jsonstr):
            data = json.loads(jsonstr)

            if data['timestamp'] in seen_stamps:
                # eliminate duplicates
                return
            else:
                # we are past duplicates
                seen_stamps.clear()

            rendered = yield from self._render_post(
                data,
                header_level=options.get('header-level', 3),
                date_format=options.get('date-format', 'compact'),
            )
            send(content=rendered)
            return data['timestamp']

        seen_stamps = {last_stamp}
        if options is None:
            options = {}
        try:
            send(action='start')

            redis = yield from self.request.redis
            connection = yield from self.request.redis_single_connection()
            subscriber = yield from connection.start_subscribe()

            if last_stamp:
                last_stamp = float(last_stamp)
                items = yield from redis.zrangebyscore(
                    self.redis_key,
                    asyncio_redis.ZScoreBoundary(last_stamp,
                                                 exclude_boundary=True),
                    asyncio_redis.ZScoreBoundary('+inf'),
                )
                for post_entry in items:
                    post, score = yield from post_entry
                    yield from send_reply(post)
                    seen_stamps.add(score)

            try:
                yield from subscriber.subscribe([self.redis_key])
                while True:
                    pubsubreply = yield from subscriber.next_published()
                    yield from send_reply(pubsubreply.value)
            finally:
                connection.close()
        except asyncio.CancelledError:
            pass
        except Exception:
            traceback.print_exc()
            raise
        finally:
            send(action='end')
