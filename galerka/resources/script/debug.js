define(['module'], function (module) {
    "use strict";
    var log;
    if (module.config().on && window.console && window.console.log) {
        log = window.console.log;
    } else {
        log = function (item) { return; };
    }
    return {
        log: log
    };
});
