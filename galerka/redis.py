import asyncio

from asyncio_redis import Pool, Connection, TransactionError
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
    def redis(self):
        args, poolsize, prefix = self.environ['galerka.redis-args']
        return (yield from Pool.create(poolsize=poolsize, **args))

    @cached_property
    def redis_prefix(self):
        return self.environ['galerka.redis-args'][2]

    @asyncio.coroutine
    def redis_subscribe(self):
        args, poolsize, prefix = self.environ['galerka.redis-args']
        conn = yield from Connection.create(**args)
        subscriber = yield from connection.start_subscribe()
        return subscriber
