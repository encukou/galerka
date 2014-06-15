import asyncio

from werkzeug.utils import call_maybe_yield, cached_property
import aiopg
from aiopg.sa import create_engine, dialect
import psycopg2
from sqlalchemy.schema import CreateTable
from sqlalchemy.sql import ClauseElement

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
        self.transaction = None

    @asyncached
    def pool(self):
        return (yield from self.get_pool())

    @asyncio.coroutine
    def execute(self, query, *multiparams, **params):
        if not self.connection:
            pool = yield from self.pool
            self.connection = yield from pool.acquire()
            self.transaction = yield from self.connection.begin()
        if isinstance(query, ClauseElement):
            print(query.compile(dialect=dialect))
        else:
            print(repr(query), multiparams, params)
        result = yield from self.connection.execute(query,
                                                    *multiparams,
                                                    **params)
        return result

    @asyncio.coroutine
    def commit(self):
        if self.transaction:
            yield from self.transaction.commit()

    @asyncio.coroutine
    def rollback(self):
        if self.transaction:
            yield from self.transaction.rollback()

    @asyncio.coroutine
    def close(self):
        if self.connection:
            yield from self.connection.close()


def postgres_pool_factory(dsn, tables):
    @asyncio.coroutine
    def get_pool():
        pool = yield from create_engine(dsn)

        connection = yield from pool.acquire()
        try:
            result = yield from connection.execute(
                'SELECT tablename FROM pg_tables '
                'WHERE schemaname=%s', ('public', ))
            existing_table_names = {name[0] for name in result}
            print('Existing tables:', existing_table_names)

            for name, table in tables.metadata.tables.items():
                if name not in existing_table_names:
                    create_statement = CreateTable(table)
                    print(create_statement.compile(dialect=dialect))
                    yield from connection.execute(create_statement)
        finally:
            connection.close()

        return pool
    pool_future = asyncio.Task(get_pool())

    @asyncio.coroutine
    def get_pool():
        return (yield from pool_future)

    return get_pool


class PostgresMixin:
    def execute_sql(self, *args, **k):
        return self.environ['galerka.postgres.connection'].execute(*args, **k)

    @cached_property
    def sql_tables(self, *args, **k):
        return self.environ['galerka.postgres.tables']
