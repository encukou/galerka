import asyncio
import json

import aiohttp
from aiohttp import websocket
from aiohttp.errors import HttpBadRequest
from werkzeug.exceptions import BadRequest

from galerka.view import View
from galerka.views.index import TitlePage
from galerka.util import asyncached


class WebsocketClose(Exception):
    def __init__(self, code, message=b''):
        super().__init__("{} {}".format(code, message))
        self.code = code
        self.message = message


class WebsocketBadRequest(WebsocketClose):
    def __init__(self, error, **extra):
        super().__init__(
            code=1008,  # Policy Violation (RFC 6455 11.7)
            message=json.dumps(dict(error=error, **extra)),
        )


@TitlePage.child('ws')
class WebsocketServer(View):
    @asyncached
    def GET(self):
        def response(environ, start_response):
            reader = self.request.environ['async.reader']
            writer = self.request.environ['async.writer']
            req_headers = [(k.upper(), v)
                           for k, v in self.request.headers.items()]
            try:
                shake_result = websocket.do_handshake('GET',
                                                      req_headers, writer)
            except HttpBadRequest:
                error = BadRequest('websocket upgrade expected')
                return error(environ, start_response)
            status, headers, parser, writer = shake_result
            write = start_response('%s Switching Protocols' % status, headers)
            datastream = reader.set_parser(parser)
            end_future = asyncio.Future()
            asyncio.Task(self._task(datastream, writer, end_future))
            return [end_future]
        return response

    @asyncio.coroutine
    def _task(self, datastream, writer, end_future):
        def _close(code, message=b''):
            print('WS: close', code, message)
            writer.close(code=code, message=message)
            end_future.set_result(b'')

        unsubscribe_functions = {}
        try:
            while True:
                try:
                    msg = yield from datastream.read()
                except aiohttp.EofStream:
                    print('WS: dropped connection')
                    end_future.set_result(b'')
                    return

                print('WS:', msg)

                if msg.tp == websocket.MSG_PING:
                    writer.pong()
                elif msg.tp == websocket.MSG_TEXT:
                    try:
                        request = json.loads(msg.data)
                    except ValueError:
                        raise WebsocketBadRequest('bad JSON', request=msg.data)
                    method = request.get('method')
                    if method == 'subscribe':
                        index, unsub = yield from self.subscribe(request,
                                                                 writer)
                        if index in unsubscribe_functions:
                            unsubscribe_functions[index]()
                        unsubscribe_functions[index] = unsub
                    else:
                        raise WebsocketBadRequest('unknown method',
                                                  method=method)
                elif msg.tp == websocket.MSG_CLOSE:
                    raise WebsocketClose(
                        code=1000,  # Normal Closure (RFC 6455 11.7)
                        message=json.dumps({
                            'close': 'bye',
                        }),
                    )
        except WebsocketClose as e:
            _close(code=e.code, message=e.message)
        except Exception:
            _close(code=1011)
            # 1011: Internal Server Error (RFC 6455 11.7)
            raise
        else:
            _close(code=1011)
            # 1011: Internal Server Error (RFC 6455 11.7)
        finally:
            for func in unsubscribe_functions:
                func()

    @asyncio.coroutine
    def subscribe(self, request, writer):
        content_type = request.get('content-type')
        if content_type != 'text/html':
            raise WebsocketBadRequest('unknown content type',
                                      **{'content-type': content_type})
        channel = request.get('channel')
        index = request.get('index')
        if not channel:
            raise WebsocketBadRequest('no channel specified', index=index)
        try:
            view = yield from self.root[channel]
        except LookupError:
            raise WebsocketBadRequest('no such channel',
                                      index=index, channel=channel)
        try:
            sub = view.ws_subscribe
        except AttributeError:
            raise WebsocketBadRequest('not a channel',
                                      index=index, channel=channel)
        last_stamp = request.get('last_stamp')

        def send(**data):
            data.setdefault('action', 'push')
            data['index'] = index
            data['channel'] = channel
            writer.send(json.dumps(data))

        task = asyncio.Task(view.ws_subscribe(send, last_stamp))
        return index, task.cancel
