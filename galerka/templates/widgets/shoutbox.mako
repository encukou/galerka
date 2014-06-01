<details open id="shoutbox">
    <summary>Shoutbox</summary>

    <form action="${(yield from this.root['shoutbox']).href(redirect=this.url)}"
          method="POST"
          id="shoutbox-form"
          enctype="multipart/form-data"
          accept-charset="utf-8">
    <fieldset>
        <input type="text" name="content" id="text">
        <input type="hidden" name="csrft" value="$ {request.csrf_token}"></button>
        <button type="submit" name="submit" value="submit">&gt;</button>
    </fieldset>
    </form>

    <div>
        ${(yield from (yield from this.root['shoutbox']).rendered_sidebar_posts)}
    </div>
    <footer>
        <a href="${(yield from this.root['shoutbox']).url}">Historie Shoutboxu</a>
    </footer>
</details>
