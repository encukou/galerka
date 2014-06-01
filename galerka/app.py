import asyncio
from inspect import isclass
import traceback

import pprintpp
from werkzeug.wrappers import Request, Response
from werkzeug.routing import Map, Rule
from werkzeug.exceptions import HTTPException, NotFound
from werkzeug.utils import redirect

from galerka.view import TitlePage

root_view_class = TitlePage


@asyncio.coroutine
def error_404(request):
    # TODO
    return Response('Chyba 404: nenalezeno',
                    mimetype='text/plain',
                    status=404)


@asyncio.coroutine
def application(environ, start_response):
    if environ['galerka.debug']:
        print('Handling request')
        pprintpp.pprint(environ)
    request = Request(environ)
    root = root_view_class._get_root(request)
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
        if environ['PATH_INFO'] != view.path:
            new_url = '%s?%s' % (view.url, environ['QUERY_STRING'])
            response = redirect(new_url)
        else:
            response = yield from view.rendered_page
    return response(environ, start_response)
