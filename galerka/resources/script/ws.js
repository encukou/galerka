define(['lib/mootools', 'module', 'debug', 'date-display'], function (mootools, module, debug, date_display) {
    "use strict";
    var sock,
        sock_open = false,
        subscribed_elements = {},
        last_sub_index = 0;
    function on_open(event) {
        debug.log('websocket open');
        sock_open = true;
        subscribed_elements = {};
        $(document.body).getElements('[data-ws-channel]').each(function (el) {
            var first_child = el.getFirst('[data-stamp]'),
                data = {},
                sub_index = last_sub_index;
            last_sub_index += 1;
            subscribed_elements[sub_index] = el;
            data.method = 'subscribe';
            data.channel = el.getProperty('data-ws-channel');
            data.index = sub_index;
            data['content-type'] = 'text/html';
            if (first_child) {
                data.last_stamp = first_child.getProperty('data-stamp');
            }
            sock.send(JSON.encode(data));
        });
    }
    function on_close(event) {
        debug.log('websocket close');
        sock = null;
        sock_open = false;
    }
    function on_error(event) {
        debug.log('websocket error');
        sock = null;
        sock_open = false;
    }
    function on_message(event) {
        var data = JSON.decode(event.data),
            parent_element,
            temp_container;
        debug.log('websocket message');
        debug.log(data);
        if (data.action === 'push') {
            parent_element = subscribed_elements[data.index];
            temp_container = new Element('div');
            temp_container.set('html', data.content);
            date_display.update(temp_container);
            temp_container.getChildren().each(function (new_element) {
                new_element.addClass('ws-loaded');
                new_element.inject(parent_element, 'top');
            });
        }
    }
    function start() {
        if (WebSocket === undefined) { return; }
        sock = new WebSocket(module.config().endpoint);
        sock.onmessage = on_message;
        sock.onopen = on_open;
        sock.onclose = on_close;
        sock.onerror = on_error;
    }
    function submit(params) {
        var path = params.path,
            data = params.data,
            on_success = params.on_success,
            on_failure = params.on_failure;
        if (sock_open) {
            on_failure();
        } else {
            try {
                sock.send(JSON.encode({
                    method: 'POST',
                    path: path,
                    data: data,
                }));
                on_success();
            } catch (e) {
                on_failure(e);
            }
        }
    }
    start();
    return {
        submit: submit
    };
});
