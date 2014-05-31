import pathlib
import contextlib

from mako.lookup import TemplateLookup

from galerka.app import application
from galerka.util import make_tempdir


@contextlib.contextmanager
def galerka_app_context(app, *, debug=False):
    with make_tempdir(prefix='galerka-tmp.') as tempdir:
        thisfile = pathlib.Path(__file__)
        template_dir = thisfile.with_name('templates')
        mako = TemplateLookup(
            directories=[str(thisfile.with_name('templates'))],
            module_directory=str(tempdir / 'mako_templates'),
            input_encoding='utf-8',
            output_encoding='utf-8',
            filesystem_checks=debug,
            strict_undefined=True,
        )

        environ_values = {
            'galerka.debug': debug,
            'galerka.tempdir': tempdir,
            'galerka.mako': mako
        }

        def middleware(environ, start_response):
            environ.update(environ_values)
            return app(environ, start_response)

        yield middleware
