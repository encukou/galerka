<!DOCTYPE html>
<html xmlns="http://www.w3.org/1999/xhtml" xml:lang="en">
<head>
    <meta http-equiv="Content-Type" content="text/html;charset=UTF-8"/>
    <title>
        % if (yield from this.title) != request.environ['galerka.site-title']:
            ${(yield from this.title)} -
        % endif
    ${request.environ['galerka.site-title']}
    </title>
    <link rel="shortcut icon" href="${static_url('favicon.png')}" />
    % for style in this.styles:
        <link rel="stylesheet" href="${static_url(style)}"
            type="text/css" media="screen" charset="utf-8" />
    % endfor
    <script>${h.js_export(
        require={
            'baseUrl': static_url('script'),
            'deps': sorted(this.javascripts),
        },
    )}</script>
    <script src="${static_url('script/require.conf.js')}"
            async="async"></script>
</head>
<body class="galerka no-js">
    <header>
        <div id="site-title" title="Galerie">
            <a href="/">&nbsp;</a>
        </div>
    </header>
    <section id="content">
        <nav id="hierarchy">
            <ul>
                ${(yield from this.rendered_hierarchy)}
            </ul>
        </nav>
        <h1>
            % if hasattr(this, 'page_title'):
                ${(yield from this.page_title)}
            % else:
                ${(yield from this.title) or request.environ['galerka.site-title']}
            % endif
        </h1>
        ${(yield from this.rendered_contents)}
    </section>
    <hr>
    <footer>
        <section id="usernav">
            <details open id="login">
                <h2>Login</h2>
                <!-- TODO login -->
            </details>
            <!-- TODO mgmt -->
            <%include file="widgets/shoutbox.mako" />
        </section>
        <section id="sitenav">
            <details open id="search">
                <h2>Hledání</h2>
                <!-- TODO search -->
            </details>
            <!-- TODO userlist -->
            <!-- TODO gallery -->
            <!-- TODO count -->
        </section>
        <section id="links">
            <!-- TODO links -->
        </section>
    </footer>
</body>
</html>
