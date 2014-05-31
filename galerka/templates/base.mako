<!DOCTYPE html>
<html xmlns="http://www.w3.org/1999/xhtml" xml:lang="en">
<head>
  <meta http-equiv="Content-Type" content="text/html;charset=UTF-8"/>
  <title>${(yield from this.title) or ''}${' - ' if (yield from this.title) else ''}${request.environ['galerka.site-title']}</title>
  <link rel="shortcut icon" href="$ {static_url('favicon.png')}" />
  <link rel="stylesheet" href="$ {static_url('css')}" type="text/css" media="screen" charset="utf-8" />
</head>
<body class="galerka no-js">
    <header>
        <div class="title" title="Galerie"><a href="${''}">&nbsp;</a></div>
    </header>
    <section id="content">
        <nav class="hierarchy">
            <ul>
                <!-- TODO hierarchy -->
            </ul>
        </nav>
        <h1>
            % if hasattr(this, 'page_title'):
                ${(yield from this.page_title)}
            % else:
                ${(yield from this.title) or request.environ['galerka.site-title']}
            % endif
        <h1>
        <!-- TODO body -->
    </section>
    <hr>
    <footer>
        <section id="usernav">
            <!-- TODO login -->
            <!-- TODO mgmt -->
            <!-- TODO shoutbox -->
        </section>
        <section id="sitenav">
            <!-- TODO search -->
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
