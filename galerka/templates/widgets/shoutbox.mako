<details open id="shoutbox">
    <summary>Shoutbox</summary>
    <div>
        ${(yield from (yield from this.root['shoutbox']).rendered_sidebar_posts)}
    </div>
    <footer>
        <a href="${(yield from this.root['shoutbox']).url}">Historie Shoutboxu</a>
    </footer>
</details>
