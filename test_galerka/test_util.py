import asyncio
import functools

from galerka.util import asyncached


def synchronize(func):
    coro = asyncio.coroutine(func)

    @functools.wraps(func)
    def run():
        return asyncio.get_event_loop().run_until_complete(coro())

    return run


class AsyncachedTestClass:
    def __init__(self, log):
        self.log = log

    @asyncached
    def prop(self):
        self.log.append('computing')
        yield from asyncio.sleep(0.001)
        return 'value'


@synchronize
def test_asyncached():
    log = []
    obj = AsyncachedTestClass(log)
    assert (yield from obj.prop) == 'value'
    assert log == ['computing']
    assert (yield from obj.prop) == 'value'
    assert log == ['computing']
