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
from galerka.middleware import galerka_app_context


def main(options):
    debug = options['--debug']

    with galerka_app_context(application, debug=debug) as app:
        run_simple(
            hostname=options['--hostname'],
            port=int(options['--port']),
            application=app,
            use_reloader=debug,
            use_debugger=debug,
            extra_files=app.extra_files,
        )

main(docopt.docopt(__doc__))
