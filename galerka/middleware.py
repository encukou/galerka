import pathlib
import contextlib
import os

from mako.lookup import TemplateLookup
from werkzeug.wsgi import SharedDataMiddleware
from werkzeug.debug import DebuggedApplication
import markupsafe

from galerka.app import application
from galerka.static import create_static_dir
from galerka.util import make_tempdir


@contextlib.contextmanager
def galerka_app_context(app, *, debug=False):
    with make_tempdir(prefix='galerka-tmp.') as tempdir:
        root = pathlib.Path(__file__).parent
        template_dir = root / 'templates'
        mako = TemplateLookup(
            directories=[str(root / 'templates')],
            module_directory=str(tempdir / 'mako_templates'),
            input_encoding='utf-8',
            output_encoding='utf-8',
            filesystem_checks=debug,
            strict_undefined=True,
            imports=['from markupsafe import escape'],
            default_filters=['escape'],
        )

        static_dir = tempdir / 'static'
        create_static_dir(root / 'resources', static_dir, debug=debug)
        app = SharedDataMiddleware(app, {'/static': str(static_dir)})

        environ_values = {
            'galerka.debug': debug,
            'galerka.tempdir': tempdir,
            'galerka.mako': mako,
            'galerka.site-title': 'Galerie',
        }

        def application(environ, start_response):
            environ.update(environ_values)
            return app(environ, start_response)

        extra_files = []
        for dirpath, dirnames, filenames in os.walk(str(root / 'resources')):
            for filename in dirnames + filenames:
                if not filename.startswith('.'):
                    extra_files.append(os.path.join(dirpath, filename))
        application.extra_files = extra_files

        yield application
