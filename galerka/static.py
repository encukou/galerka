import shutil
import hashlib
import json
import pathlib
import itertools

import scss
import jsmin


class StaticBase:
    def __init__(self, path):
        self.path = path


class StaticDir(StaticBase):
    minified = False

    def rel_url(self, base):
        return self.path.relative_to(base)

    def __repr__(self):
        fmt = '<{s.__module__}.{s.__class__.__qualname__}>'
        return fmt.format(s=self)


class StaticFile(StaticBase):
    def __init__(self, path, *,
                 sha=None,
                 size=None,
                 source=None,
                 source_size=None
                 ):
        super().__init__(path)
        self._sha = sha
        self._size = size
        self.source = source
        self._source_size = source_size

    def __repr__(self):
        fmt = '<{s.__module__}.{s.__class__.__qualname__} {s.sha}>'
        return fmt.format(s=self)

    def _get_file_stats(self):
        with self.path.open('rb') as file:
            contents = file.read()
            self._sha = hashlib.sha1(contents).hexdigest()
            self._size = len(contents)

    @property
    def sha(self):
        if self._sha is None:
            self._get_file_stats()
        return self._sha

    @property
    def size(self):
        if self._size is None:
            self._size = self.source.stat().size
        return self._size

    @property
    def source_size(self):
        if self._source_size is None:
            self._get_source_stats()
        return self._source_size

    @property
    def minified(self):
        return self.source and self.source_size != self.size


class JSFile(StaticFile):
    def __init__(self, *args, module_name, **kwargs):
        super().__init__(*args, **kwargs)
        self.module_name = module_name

    def rel_url(self, base):
        return '%s?%s' % (self.path.relative_to(base), self.sha)


def json_compact(value):
    return json.dumps(value, separators=(',', ':'), sort_keys=True)


def transplant_path(path, fromdir, todir):
    return todir / path.relative_to(fromdir)


def create_static_dir(fromdir, todir, *, debug):
    return {str(item.path.relative_to(todir)): item
            for item in generate_static_dir(fromdir, todir, debug=debug)}


def generate_static_dir(fromdir, todir, *, debug):
    if todir.exists():
        shutil.rmtree(str(todir))

    items = itertools.chain(
        mkdir(todir),
        copy_dir(fromdir / 'background', todir / 'background'),
        create_css(fromdir, todir, debug=debug),
        create_js(fromdir, todir, debug=debug),
        copy_file(fromdir / 'favicon.png', todir / 'favicon.png'),
        copy_file(fromdir / 'style/qunit.css', todir / 'qunit.css'),
    )

    for item in items:
        relpath = item.path.relative_to(todir)
        srcpath = None
        if isinstance(item, StaticFile):
            sha = item.sha
            if item.minified:
                fmt = ('{i.sha} {srcpath} → {relpath}: '
                       '{i.source_size:,} → {i.size:,}b')
                srcpath = item.source.relative_to(fromdir)
            else:
                fmt = '{i.sha} {relpath}: {i.size:,}b'
        else:
            fmt = ' ' * 40 + ' {relpath}'
        print(fmt.format(i=item, relpath=relpath, srcpath=srcpath))
        yield item


def mkdir(dest):
    dest.mkdir()
    yield StaticDir(dest)


def copy_file(src, dest):
    shutil.copyfile(str(src), str(dest))
    yield StaticFile(dest)


def copy_dir(fromdir, todir):
    yield from mkdir(todir)
    for path in fromdir.iterdir():
        dest_path = transplant_path(path, fromdir, todir)
        yield from copy_file(path, dest_path)


def create_css(fromdir, todir, *, debug):
    css_source_path = fromdir / 'style'
    if debug:
        scss_style = 'expanded'
    else:
        scss_style = 'compressed'
    scss_compiler = scss.Scss(
        search_paths=[str(css_source_path)],
        scss_opts={
            'debug_info': debug,
            'warn_unused': True,
            'style': scss_style,
        },
    )
    dest_filename = todir / 'style.css'
    with (dest_filename).open('w') as cssfile:
        source_file = css_source_path / 'root.scss'
        cssfile.write(scss_compiler.compile(scss_file=str(source_file)))
    yield StaticFile(dest_filename)


def create_js(fromdir, todir, *, debug):
    conf_values = {
        'paths': {},
        'shim': {
            'lib/mootools': {'exports': '$'},
            'lib/qunit': {'exports': 'QUnit'},
        }
    }
    basefrom = fromdir / 'script'
    basepath = todir / 'script'
    for item in _create_js_dir(basefrom, basepath, debug, basepath):
        yield item
        try:
            module_name = item.module_name
        except AttributeError:
            pass
        else:
            conf_values['paths'][module_name] = item.rel_url(basepath)

    conf_module_name = 'require.conf'
    conf_path = basepath / (conf_module_name + '.js')
    with conf_path.open('w') as conf_file:
        for key, value in conf_values.items():
            conf_file.write('require[%s]=%s;\n' % (json_compact(key),
                                                   json_compact(value)))
        with (basepath / 'lib' / 'require.js').open() as require_file:
            conf_file.write(require_file.read())

    yield JSFile(conf_path, module_name=conf_module_name)


def _create_js_dir(fromdir, todir, debug, basepath):
    yield from mkdir(todir)
    for source in sorted(fromdir.iterdir()):
        if source.name.startswith('.'):
            # hidden file
            pass
        elif source.is_dir():
            yield from _create_js_dir(
                source,
                transplant_path(source, fromdir, todir),
                debug, basepath,
            )
        elif '.js' in source.suffixes:
            base_name = source.name.split('.', 2)[0]
            dest = todir / (base_name + '.js')
            dest_relative = dest.relative_to(basepath)
            mod_name = str(dest_relative.with_name(base_name))
            with source.open() as srcfile, dest.open('a') as destfile:
                js = srcfile.read()
                source_size = len(js)
                if '.min' not in source.suffixes and not debug:
                    js = jsmin.jsmin(js)
                    minified = True
                else:
                    minified = False
                sha = hashlib.sha1(js.encode('utf-8')).hexdigest()
                destfile.write(js)
                yield JSFile(
                    dest,
                    sha=sha,
                    size=len(js),
                    source=source,
                    source_size=source_size,
                    module_name=mod_name,
                )
