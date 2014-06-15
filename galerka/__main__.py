"""A community galerka site

Usage:
  galerka [options]

Options:
  -h, --help                Show help
  --hostname=HOSTNAME       Hostname to run on [default: localhost]
  -p, --port=NUM            Port to listen on [default: 4000]
  -d, --debug               Enable debugging
  --redis-url=URL           Redis URL [default: redis://localhost:6379/#galerka]
  --postgres-dsn=DSN        Postgres DSN [default: dbname=galerka user=galerka]
  --postgres-prefix=PREFIX  Postgres table name prefix [default: galerka_]

The Redis URL can be in the form:
    redis://[db-number[:password]@]host:port[?option=value][#prefix]
    A ':' will be appended toi the prefix if it's not already there
    Options are:
        poolsize: Connections to allocate [default: 20]
"""

from werkzeug.serving import run_simple
import docopt

from galerka.app import application
from galerka.middleware import galerka_app_context


def main(options):
    print(options)

    debug = options['--debug']

    context = galerka_app_context(
        application,
        redis_url=options['--redis-url'],
        postgres_dsn=options['--postgres-dsn'],
        postgres_prefix=options['--postgres-prefix'],
        debug=debug,
    )

    with context as app:
        run_simple(
            hostname=options['--hostname'],
            port=int(options['--port']),
            application=app,
            use_reloader=debug,
            use_debugger=debug,
            extra_files=app.extra_files,
        )

main(docopt.docopt(__doc__))
