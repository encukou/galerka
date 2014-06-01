<section>
    <h3 class="date-header">
        <time>${message.time}</time>
        % if message.author:
            <span class="head-text">${message.author}</span>
        % else:
            <span class="head-text">Systémová zpráva</span>
        % endif
    </h3>
    <div class="message markdown">${message.body}</div>
</section>
