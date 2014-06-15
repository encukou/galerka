import asyncio

from werkzeug.utils import call_maybe_yield, cached_property
import aiopg
from aiopg.sa import create_engine
import psycopg2

from galerka.util import asyncached


def postgres_middleware(app):
    @asyncio.coroutine
    def add_postgres(environ, start_response):
        connection = SQLConnection(environ['galerka.postgres.get_pool'])
        environ['galerka.postgres.connection'] = connection
        try:
            result = yield from call_maybe_yield(app, environ, start_response)
            return result
        except:
            yield from connection.rollback()
            raise
        else:
            yield from connection.commit()
        finally:
            yield from connection.close()
    return add_postgres


class SQLConnection:
    def __init__(self, get_pool):
        self.get_pool = get_pool
        self.connection = None

    @asyncached
    def pool(self):
        return (yield from self.get_pool())

    @asyncio.coroutine
    def execute(self, *args, **kwargs):
        if not self.connection:
            pool = yield from self.pool
            self.connection = yield from pool.acquire()
            yield from self._execute('BEGIN')
        result = yield from self._execute(*args, **kwargs)
        return result

    @asyncio.coroutine
    def _execute(self, *args, **kwargs):
        cursor = yield from self.connection.cursor()
        try:
            yield from cursor.execute(*args, **kwargs)
            if cursor.description is not None:
                return (yield from cursor.fetchall())
        finally:
            cursor.close()

    @asyncio.coroutine
    def commit(self):
        if self.connection:
            yield from self.execute('COMMIT')

    @asyncio.coroutine
    def rollback(self):
        if self.connection:
            yield from self.execute('ROLLBACK')

    @asyncio.coroutine
    def close(self):
        if self.connection:
            (yield from self.pool).release(self.connection)


def postgres_pool_factory(dsn, create_tables=None):
    pool = asyncio.Task(aiopg.create_pool(dsn))

    @asyncio.coroutine
    def get_pool():
        return (yield from pool)

    return get_pool


class PostgresMixin:
    def execute_sql(self, *args, **k):
        return self.environ['galerka.postgres.connection'].execute(*args, **k)

    @cached_property
    def sql_tables(self, *args, **k):
        return self.environ['galerka.postgres.tables']
