import asyncio

from asyncio_redis import Pool, Connection
from werkzeug.urls import url_parse
from werkzeug.utils import cached_property

from galerka.util import asyncached


def get_redis_args(url):
    """Parses Redis connection arguments out of a URL string

    redis://[db-number[:password]@]host:port[?option=value][#prefix]

    Returns (args, poolsize, prefix), where args can be passed directly
    to a redis Connection
    """
    url = url_parse(url)
    if url.path and url.path != '/':
        raise ValueError("Bad redis URL: can't contain path")
    db_number = int(url.username or 0)
    password = url.password or None
    host = url.host or 'localhost'
    port = url.port or 6379
    prefix = url.fragment
    if not prefix.endswith(':'):
        prefix = prefix + ':'
    options = url.decode_query()
    poolsize = options.pop('poolsize', 20)
    if options:
        raise ValueError('Extra Redis options: %s' % ', '.join(options))
    return dict(
        host=host,
        port=port,
        password=password,
        db=db_number,
        auto_reconnect=True,
    ), poolsize, prefix


class RedisMixin:
    @asyncached
    def redis_connection(self):
        args, poolsize, prefix = self.environ['galerka.redis-args']
        return (yield from Pool.create(poolsize=poolsize, **args))

    @cached_property
    def redix_prefix(self):
        return self.environ['galerka.redis-args'][2]

    @asyncio.coroutine
    def redis_subscribe(self):
        args, poolsize, prefix = self.environ['galerka.redis-args']
        conn = yield from Connection.create(**args)
        subscriber = yield from connection.start_subscribe()
        return subscriber

    @cached_property
    def redis(self):
        return RedisProxy(self)


class RedisProxy:
    def __init__(self, request):
        self.request = request
        self.prefix = request.redix_prefix

    @property
    def conn(self):
        return self.request.redis_connection

    def lrange(self, key, start=0, stop=-1):
        conn = yield from self.conn
        reply = conn.lrange(self.prefix + key, start, stop)
        return (yield from reply)

    def lpush(self, key, values):
        conn = yield from self.conn
        reply = conn.lpush(self.prefix + key, values)
        return (yield from reply)

    # TODO: Proxy all the others
