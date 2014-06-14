<details open id="shoutbox">
    <summary>${(yield from (yield from this.root['shoutbox']).title)}</summary>

    <form action="${(yield from this.root['shoutbox']).href(redirect=this.url)}"
          method="POST"
          id="shoutbox-form"
          data-async-submit-img="${static_url('loading/loading-spinning-bubbles.svg')}"
          enctype="multipart/form-data"
          accept-charset="utf-8">
    <fieldset>
        <input type="text" name="content" id="text">
        <input type="hidden" name="csrft" value="$ {request.csrf_token}">
        <span class="ajax-sender">
            <button type="submit" name="submit" value="submit">&gt;</button>
        </span>
    </fieldset>
    </form>

    <div>
        ${(yield from (yield from this.root['shoutbox']).rendered_sidebar_posts)}
    </div>
    <footer>
        <a href="${(yield from this.root['shoutbox']).url}">Historie Shoutboxu</a>
    </footer>
</details>

<%"""preload form submit spinner"""%>
<img src="${static_url('loading/loading-spinning-bubbles.svg')}"
     width="1px" height="1px" style="position: absolute; right:-1000px">
