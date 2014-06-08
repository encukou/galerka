require(['date-display', 'lib/domReady'], function (date_display, domready) {
    "use strict";
    domready(function () {
        date_display.start();
    });
});

require(['shoutbox']);
