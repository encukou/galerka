import asyncio
from inspect import isclass

import pprintpp
from werkzeug.wrappers import Request, Response
from werkzeug.routing import Map, Rule
from werkzeug.exceptions import HTTPException, NotFound
from werkzeug.utils import call_maybe_yield

from galerka.view import TitlePage, TestPage


@asyncio.coroutine
def test_page(request):
    yield from asyncio.sleep(2)
    return Response('Oh, hi there!')


def error_404(request):
    # TODO
    return Response('Chyba 404: nenalezeno',
                    mimetype='text/plain',
                    status=404)


url_map = Map(
    [
        Rule('/', endpoint=TitlePage, methods=['GET']),
        Rule('/test', endpoint=TestPage, methods=['GET']),
    ],
    redirect_defaults=True,
)


@asyncio.coroutine
def application(environ, start_response):
    if environ['galerka.debug']:
        print('Handling request')
        pprintpp.pprint(environ)
    adapter = url_map.bind_to_environ(environ)
    try:
        endpoint, values = adapter.match()
        is_response = False
    except NotFound:
        endpoint = error_404
        values = {}
        is_response = False
    except HTTPException as e:
        response = e
        endpoint = None
    request = Request(environ)
    if endpoint:
        if getattr(endpoint, '_galerka_view', False):
            view = endpoint(request, **values)
            response = yield from view.rendered_page
        else:
            response = yield from call_maybe_yield(endpoint, request, **values)
    return response(environ, start_response)
