import tempfile
import shutil
import contextlib
import pathlib


@contextlib.contextmanager
def make_tempdir(suffix='', prefix='tmp', dir=None):
    dirname = tempfile.mkdtemp(suffix=suffix, prefix=prefix, dir=dir)
    try:
        yield pathlib.Path(dirname)
    finally:
        shutil.rmtree(dirname)
