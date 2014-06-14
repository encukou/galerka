/* Dynamic fuzzy date display */

define(['lib/mootools'], function () {
    "use strict";
    function complex_formatter(value, str1, str5) {
        value = Math.round(value);
        if (value < 5) {
            return str1.replace(/%d/i, value);
        }
        return str5.replace(/%d/i, value);
    }
    function neighbor_formatter(then, now, unit, future,
                                past_str, future_str) {
        var relative = new Date(now);
        if (future) {
            relative.increment(unit, 1);
            if (then.get(unit) === relative.get(unit)) {
                return future_str;
            }
        } else {
            relative.decrement(unit, 1);
            if (then.get(unit) === relative.get(unit)) {
                return past_str;
            }
        }
        return false;
    }
    function format_long(then, now) {
        var s = now.diff(then, 'second'),
            future = s > 0,
            sec = Math.abs(s),
            min = sec / 60,
            hr = min / 60,
            dy = hr / 24,
            wk = dy / 7,
            mon = dy / 30.5,
            yr = mon / 12,
            result,
            simple,
            complex;
        if (future) {
            simple = function (past, future) { return future; };
            complex = function (num, past, f1, f5) {
                return complex_formatter(num, f1, f5);
            };
        } else {
            simple = function (past, future) { return past; };
            complex = function (num, past, f1, f5) {
                return complex_formatter(num, past, past);
            };
        }
        if (sec < 45) {
            return simple("před chvilkou", "za chvilku");
        }
        if (sec < 90) {
            return simple("před minutou", "za minutu");
        }
        if (min < 10) {
            return complex(min, "před %d minutami", "za %d minuty",
                           "za %d minut");
        }
        if (min < 20) {
            return simple("před čtvrt hodinou", "za čtvrt hodiny");
        }
        if (min < 45) {
            return simple("před půl hodinou", "za půl hodiny");
        }
        if (min < 90) {
            return simple("před hodinou", "za hodinu");
        }
        if (hr < 20) {
            return complex(hr, "před %d hodinami",
                           "za %d hodiny", "za %d hodin");
        }
        if (dy < 2) {
            result = neighbor_formatter(then, now, 'day', future,
                                        'včera', 'zítra');
            if (result) { return result; }
        }
        if (hr < 42) {
            return simple("před 1 dnem", "za 1 den");
        }
        if (dy < 6) {
            return complex(dy, "před %d dny", "za %d dny", "za %d dní");
        }
        if (Math.round(wk) <= 1) {
            return simple("před týdnem", "za týden");
        }
        if (wk < 3.5) {
            return complex(wk, "před %d týdny", "za %d týdny", "za %d týdnů");
        }
        if (mon < 2) {
            result = neighbor_formatter(then, now, 'month', future,
                                        'minulý měsíc', 'příští měsíc');
            if (result) { return result; }
        }
        if (dy < 45) {
            return simple("před měsícem", "za měsíc");
        }
        if (mon < 14) {
            return complex(mon, "před %d měsíci",
                           "za %d měsíce", "za %d měsíců");
        }
        if (yr < 2) {
            result = neighbor_formatter(then, now, 'year', future,
                                        'loni', 'příští rok');
            if (result) { return result; }
        }
        if (yr < 1.5) {
            return simple("před rokem", "za rok");
        }
        return complex(yr, "před %d lety", "za %d roky", "za %d let");
    }
    function pad2(n) {
        if (n < 10) { return '0' + n.toString(); }
        return n;
    }
    function format_short(then, now) {
        var s = now.diff(then, 'second'),
            sec = Math.abs(s),
            min = sec / 60,
            hr = min / 60,
            dy = hr / 24,
            yesterday,
            tomorrow,
            month_day;
        if (dy < 2) {
            if (then.get('date') === now.get('date')) {
                return then.get('hours') + ':' + pad2(then.get('minutes'));
            }
            yesterday = new Date(now);
            yesterday.decrement('day', 1);
            if (then.get('date') === yesterday.get('date')) { return 'včera'; }
            tomorrow = new Date(now);
            tomorrow.increment('day', 1);
            if (then.get('date') === tomorrow.get('date')) { return 'zítra'; }
        }
        month_day = then.get('date') + '. ' + (then.get('month') + 1) + '.';
        if (then.get('year') === now.get('year')) { return month_day; }
        return month_day + ' ' + then.get('year');
    }
    function format(then, now, fmt) {
        if (fmt === 'compact') {
            return format_short(then, now);
        }
        return format_long(then, now);
    }
    function update(element, now) {
        if (element === undefined) {
            element = document.id(document);
        }
        if (now === undefined) {
            now = new Date();
        }
        element.getElements('time').each(function (el) {
            var then = new Date(el.getProperty('datetime')),
                fmt = el.getProperty('data-dateformat');
            el.set('text', format(then, now, fmt));
        });
    }
    function start() {
        update();
        update.periodical(60000);
    }
    return {
        start: start,
        format: format,
        update: update,
    };
});
