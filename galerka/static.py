import shutil

import scss


def create_static_dir(fromdir, todir, *, debug):
    if todir.exists():
        shutil.rmtree(str(todir))
    todir.mkdir()

    shutil.copyfile(str(fromdir / 'favicon.png'), str(todir / 'favicon.png'))
    copy_dir(fromdir / 'background', todir / 'background')

    create_css(fromdir, todir, debug=debug)

    print('Static files done')


def copy_dir(fromdir, todir):
    todir.mkdir()
    for path in fromdir.iterdir():
        print('{} → {}'.format(path.name, todir))
        shutil.copyfile(
            str(path),
            str(todir / path.relative_to(fromdir))
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
