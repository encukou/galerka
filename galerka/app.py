from werkzeug.wrappers import Request, Response
from werkzeug.routing import Map, Rule
from werkzeug.exceptions import HTTPException, NotFound


def title_page(request):
    return Response('Hello World!')


def error_404(request):
    # TODO
    return Response('Chyba 404: nenalezeno',
                    mimetype='text/plain',
                    status=404)


url_map = Map(
    [
        Rule('/', endpoint=title_page, methods=['GET']),
    ],
    strict_slashes=True,
    redirect_defaults=True,
)


def application(environ, start_response):
    adapter = url_map.bind_to_environ(environ)
    try:
        endpoint, values = adapter.match()
    except NotFound:
        endpoint = error_404
        values = {}
    except HTTPException as e:
        endpoint = e
        values = {}
    request = Request(environ)
    response = endpoint(request, **values)
    return response(environ, start_response)
