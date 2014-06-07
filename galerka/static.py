import shutil
import hashlib
import json

import scss
import jsmin


def json_compact(value):
    return json.dumps(value, separators=(',', ':'))


def transplant_path(path, fromdir, todir):
    return todir / path.relative_to(fromdir)


def create_static_dir(fromdir, todir, *, debug):
    if todir.exists():
        shutil.rmtree(str(todir))
    todir.mkdir()

    shutil.copyfile(str(fromdir / 'favicon.png'), str(todir / 'favicon.png'))
    copy_dir(fromdir / 'background', todir / 'background')

    create_css(fromdir, todir, debug=debug)

    create_js(fromdir / 'script', todir / 'script', debug=debug)

    print('Static files done')


def copy_dir(fromdir, todir):
    todir.mkdir()
    for path in fromdir.iterdir():
        print('{} → {}'.format(path.name, todir))
        shutil.copyfile(
            str(path),
            str(transplant_path(path, fromdir, todir))
        )


def create_css(fromdir, todir, *, debug):
    print('Compiling CSS')
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
    with (todir / 'style.css').open('w') as cssfile:
        source_file = css_source_path / 'root.scss'
        cssfile.write(scss_compiler.compile(scss_file=str(source_file)))


def create_js(fromdir, todir, *, debug):
    print('Compiling JS')
    conf_values = {
        'paths': {},
    }
    for item in _create_js_dir(fromdir, todir, debug, fromdir, todir):
        if item['minified']:
            fmt = ('{i[sha]} {i[source]} → {i[dest]}: '
                   '{i[source_len]:,} → {i[dest_len]:,}b')
        else:
            fmt = '{i[sha]} {i[dest]}: {i[dest_len]:,}b'
        print(fmt.format(i=item))
        conf_values['paths'][str(item['mod_name'])] = item['rel_url']
    with (todir / 'require.conf.js').open('w') as conf_file:
        for key, value in conf_values.items():
            conf_file.write('require[%s]=%s;\n' % (json_compact(key),
                                                   json_compact(value)))
        with (todir / 'lib' / 'require.js').open() as require_file:
            conf_file.write(require_file.read())


def _create_js_dir(fromdir, todir, debug, fromroot, toroot):
    todir.mkdir()
    for source in sorted(fromdir.iterdir()):
        if source.name.startswith('.'):
            # hidden file
            pass
        elif source.is_dir():
            yield from _create_js_dir(
                source,
                transplant_path(source, fromdir, todir),
                debug, fromroot, toroot
            )
        elif '.js' in source.suffixes:
            base_name = source.name.split('.', 2)[0]
            dest = todir / (base_name + '.js')
            src_relative = source.relative_to(fromroot)
            dest_relative = dest.relative_to(toroot)
            mod_name = dest_relative.with_name(base_name)
            with source.open() as srcfile, dest.open('a') as destfile:
                js = srcfile.read()
                source_len = len(js)
                if '.min' not in source.suffixes and not debug:
                    js = jsmin.jsmin(js)
                    minified = True
                else:
                    minified = False
                sha = hashlib.sha1(js.encode('utf-8')).hexdigest()
                destfile.write(js)
                yield {
                    'source': src_relative,
                    'dest': dest_relative,
                    'sha': sha,
                    'source_len': source_len,
                    'dest_len': len(js),
                    'minified': minified,
                    'mod_name': mod_name,
                    'rel_url': '%s?%s' % (dest_relative, sha),
                }
