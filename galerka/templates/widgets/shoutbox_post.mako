<section>
    <h${header_level} class="date-header">
        ${h.format_date(message.time, format=date_format)}
        % if message.author:
            <span class="head-text">${message.author}</span>
        % else:
            <span class="head-text">Systémová zpráva</span>
        % endif
    </h${header_level}>
    <div class="message markdown">${message.body}</div>
</section>
