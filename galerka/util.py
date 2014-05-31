import tempfile
import shutil
import contextlib
import pathlib
import asyncio


@contextlib.contextmanager
def make_tempdir(suffix='', prefix='tmp', dir=None):
    dirname = tempfile.mkdtemp(suffix=suffix, prefix=prefix, dir=dir)
    try:
        yield pathlib.Path(dirname)
    finally:
        shutil.rmtree(dirname)


class AsyncGetter:
    """Returns the given value when yielded from"""
    def __init__(self, value):
        self.value = value

    def __iter__(self):
        return self

    def __next__(self):
        raise StopIteration(self.value)


class asyncached:
    """Decorator to creade a cached coroutine "property"

    When first yielded from, the value will be computed using the decorated
    coroutine.

    When yielded from after that, will always return the value returned before.
    """
    def __init__(self, func):
        self._name = func.__name__
        self._func = asyncio.coroutine(func)

    def __get__(self, instance, cls=None):
        if not instance:
            return self
        else:
            return self._coro(instance)

    def _coro(self, instance):
        @asyncio.coroutine
        def coro():
            result = yield from self._func(instance)
            setattr(instance, self._name, AsyncGetter(result))
            return result
        return coro()
