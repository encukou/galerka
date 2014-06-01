import asyncio
from inspect import isclass
import traceback

import pprintpp
from werkzeug.wrappers import Request, Response
from werkzeug.routing import Map, Rule
from werkzeug.exceptions import HTTPException, NotFound
from werkzeug.utils import redirect

from galerka.redis import RedisMixin


@asyncio.coroutine
def error_404(request):
    # TODO
    return Response('Chyba 404: nenalezeno',
                    mimetype='text/plain',
                    status=404)


class GalerkaRequest(Request, RedisMixin):
    pass


@asyncio.coroutine
def application(environ, start_response):
    if environ['galerka.debug']:
        print('Handling request')
        pprintpp.pprint(environ)
    request = GalerkaRequest(environ)
    root = environ['galerka.root_class'](None, '', request=request)
    pathinfo = environ['PATH_INFO'].rstrip('/').split('/')
    try:
        view = (yield from root.traverse(pathinfo))
    except (LookupError, NotFound):
        traceback.print_exc()
        response = yield from error_404(request)
    except HTTPException as e:
        return e
    else:
        environ['galerka.view'] = view
        method = environ['REQUEST_METHOD']
        if environ['PATH_INFO'] != view.path and method == 'GET':
            new_url = '%s?%s' % (view.url, environ['QUERY_STRING'])
            response = redirect(new_url)
        else:
            response = yield from view.get_response(method)
    return response(environ, start_response)
