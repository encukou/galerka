define(['lib/domReady', 'lib/mootools'], function (domready) {
    "use strict";
    function form_to_object(form, seed) {
        var obj = seed;
        if (obj === undefined) { obj = {}; }
        form.getElements('input, select, textarea').each(function (el) {
            var type = el.type,
                value;
            if (!el.name || el.disabled || type === 'submit' ||
                    type === 'reset' || type === 'file' ||
                    type === 'image') { return; }

            if (el.get('tag') === 'select') {
                value = el.getSelected().map(function (opt) {
                    return document.id(opt).get('value');
                });
            } else if ((type === 'radio' || type === 'checkbox') &&
                    !el.checked) {
                value = null;
            } else {
                value = el.get('value');
            }
            obj[el.name] = value;
        });
        return obj;
    }

    domready(function () {
        var el = document.id('shoutbox');
        function intercept_form_change(event, form) {
            var submit_button = form.getElement('button[type=submit]'),
                submit_replacement = new Element('img', {
                    src: form.getProperty('data-async-submit-img')
                }),
                request;
            function undo() {
                console.log('restore form');
                submit_button.setStyle('display', 'inline');
                submit_replacement.dispose();
            }
            function submit_http() {
                console.log('submit normally');
                undo();
                el.removeEvent('submit:relay(form)', intercept_form_change);
                console.log(form);
                form.fireEvent('submit');
            }
            try {
                event.preventDefault();
                submit_replacement.inject(submit_button, 'after');
                submit_button.setStyle('display', 'none');
                request = new Request.JSON({
                    url: form.getProperty('action'),
                    method: 'POST',
                    noCache: true,
                    data: form_to_object(form),
                    headers: {accept: 'application/json'}
                });
                request.addEvents({
                    cancel: submit_http,
                    success: undo,
                    failure: submit_http,
                });
                request.send();
                return false;
            } catch (e) {
                submit_http();
            }
        }
        el.addEvent('submit:relay(form)', intercept_form_change);
    });
});
