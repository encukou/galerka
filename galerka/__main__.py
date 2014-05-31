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

from werkzeug.serving import run_simple
import docopt

from galerka.app import application


def main(options):
    debug = options['--debug']

    run_simple(
        hostname=options['--hostname'],
        port=int(options['--port']),
        application=application,
        use_reloader=debug,
        use_debugger=debug,
    )

main(docopt.docopt(__doc__))
