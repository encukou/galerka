import shutil

import scss
import jsmin


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


def create_js(fromdir, todir, *, debug, _rootdir=None):
    if _rootdir is None:
        print('Compiling JS')
        _rootdir = fromdir
    todir.mkdir()
    for source in sorted(fromdir.iterdir()):
        if source.name.startswith('.'):
            # hidden file
            pass
        elif source.is_dir():
            create_js(source, transplant_path(source, fromdir, todir),
                      debug=debug,
                      _rootdir=_rootdir)
        elif '.js' in source.suffixes:
            dest = todir / (source.name.split('.', 2)[0] + '.js')
            with source.open() as srcfile, dest.open('a') as destfile:
                relpath = source.relative_to(_rootdir)
                js = srcfile.read()
                if '.min' not in source.suffixes and not debug:
                    source_len = len(js)
                    js = jsmin.jsmin(js)
                    print('{0}: {1:,} → {2:,}b'.format(
                        relpath, source_len, len(js)))
                else:
                    print('{0}: {1:,}b'.format(relpath, len(js)))
                destfile.write(js)
