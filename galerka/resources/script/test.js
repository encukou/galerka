require(
    [
        'lib/domReady', 'lib/qunit',
        'test/test-date-display',
    ],
    function (domready, QUnit, test_date_display) {
        "use strict";
        require('lib/mootools');
        QUnit.config.autostart = false;
        QUnit.load();
        domready(function () {
            test_date_display.run();
            QUnit.config.autostart = true;
            QUnit.start();
        });
    }
);
