"""A community galerka site

Usage:
  galerka [options]

Options:
  -h, --help                Show help
  --hostname=[HOSTNAME]     Hostname to tun on [default: localhost]
  -p, --port=[NUM]          Port to listen on [default: 4000]
  -d, --debug               Enable debugging

"""

import sys
from asyncio import coroutine

from werkzeug.serving import run_simple
import docopt

from galerka.app import application


def set_debug(app):
    def middleware(environ, start_response):
        environ['galerka.debug'] = True
        return app(environ, start_response)
    return middleware


def main(options):
    debug = options['--debug']

    app = application

    if debug:
        app = set_debug(app)

    run_simple(
        hostname=options['--hostname'],
        port=int(options['--port']),
        application=app,
        use_reloader=debug,
        use_debugger=debug,
    )

main(docopt.docopt(__doc__))
