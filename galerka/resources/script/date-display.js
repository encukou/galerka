/* Dynamic fuzzy date display */

define(['lib/mootools'], function() {
    "use strict";
    function complex_formatter(value, str1, str5) {
        value = Math.round(value);
        if (value < 5) return str1.replace(/%d/i, value);
        return str5.replace(/%d/i, value);
    }
    function neighbor_formatter(date, unit, future, past_str, future_str) {
        var relative = new Date();
        if (future) {
            relative.increment(unit, 1);
            if (date.get(unit) == relative.get(unit)) return future_str;
        } else {
            relative.decrement(unit, 1);
            if (date.get(unit) == relative.get(unit)) return past_str;
        }
        return false;
    }
    function format_long(s, date) {
        var simple, complex;
        var future = s > 0;
        if (future) {
            simple = function(past, future) {return future;};
            complex = function(num, past, f1, f5) {return complex_formatter(num, f1, f2);};
        }else{
            simple = function(past, future) {return past;};
            complex = function(num, past, f1, f5) {return complex_formatter(num, past, past);};
        }
        var sec = Math.abs(s)
        if (sec < 45) return simple("před chvilkou", "za chvilku");
        if (sec < 90) return simple("před minutou", "za minutu");
        var min = sec / 60;
        if (min < 10) return complex(min, "před %d minutami", "za %d minuty", "za %d minut");
        if (min < 20) return simple("před čtvrt hodinou", "za čtvrt hodiny");
        if (min < 45) return simple("před půl hodinou", "za půl hodiny");
        if (min < 90) return simple("před hodinou", "za hodinu");
        var hr = min / 60;
        if (hr < 20) return complex(hr, "před %d hodinami", "za %d hodiny", "za %d hodin");
        var dy = hr / 24;
        if (dy < 2) {
            var result = neighbor_formatter(date, 'day', future, 'včera', 'zítra');
            if (result) return result;
        }
        if (hr < 42) return simple("před 1 dnem", "za 1 den");
        if (dy < 6) return complex(dy, "před %d dny", "za %d dny", "za %d dní");
        if (dy < 8) return simple("před týdnem", "za týden");
        var wk = dy / 7;
        if (wk < 3.5) return complex(wk, "před %s týdny", "za %s týdny", "za %s týdnů");
        var mon = dy / 30.5;
        if (mon < 2) {
            var result = neighbor_formatter(date, 'month', future, 'minulý měsíc', 'příští měsíc');
            if (result) return result;
        }
        if (dy < 45) return simple("před měsícem", "za měsíc");
        if (mon < 14) return complex(mon, "před %d měsíci", "za %d měsíce", "za %d měsíců");
        var yr = mon / 12;
        if (yr < 2) {
            var result = neighbor_formatter(date, 'month', future, 'loni', 'příští rok');
            if (result) return result;
        }
        if (yr < 1.5) return simple("před rokem", "za rok");
        return complex(yr, "před %d lety", "za %d roky", "za %d let");
    }
    function pad2(n) {
        if (n < 10) return '0' + ('' + n);
        return n;
    }
    function format_short(s, date) {
        var sec = Math.abs(s)
        var min = sec / 60;
        var hr = min / 60;
        var dy = hr / 24;
        var today = new Date();
        if (dy < 2) {
            if ((hr < 4) || (date.get('date') == today.get('date'))) {
                return date.get('hours') + ':' + pad2(date.get('minutes'));
            }
            var yesterday = new Date();
            yesterday.decrement('day', 1);
            if (date.get('date') == yesterday.get('date')) return 'včera';
            var tomorrow = new Date();
            tomorrow.increment('day', 1);
            if (date.get('date') == tomorrow.get('date')) return 'zítra';
        }
        var month_day = date.get('date') + '. ' + pad2(date.get('month'));
        if (date.get('year') == today.getYear('year')) return month_day;
        return month_day + '. ' + date.get('year');
    }
    function update() {
        var element = document.id(document);
        var now = new Date();
        element.getElements('time').each(function(el) {
            var then = new Date();
            then.parse(el.getProperty('datetime'));
            var difference = now.diff(then, 'second');
            if (el.getProperty('data-dateformat') == 'compact') {
                el.set('text', format_short(difference, then));
            } else {
                el.set('text', format_long(difference, then));
            }
        });
    }
    function start() {
        update();
        update.periodical(60000);
    }
    return {
        start: start,
    }
});
