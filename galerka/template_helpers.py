import datetime
import json as json_module

import pytz
from markupsafe import Markup

local_timezone = pytz.timezone('Europe/Prague')

formats = dict(
    title='{d.day_cz} {s.day}. {s.month}. {s.year}, {s.hour:02}:{s.minute:02}',
    date='{s.day}. {s.month}. {s.year} {s.hour:02}:{s.minute:02}',
    compact='{s.hour:02}:{s.minute:02}',
)


class FormattedDate(object):
    def __init__(self, date, format):
        assert '"' not in format
        self.format = format
        self.utc_date = date
        self.local_date = pytz.utc.localize(date).astimezone(local_timezone)

    @property
    def day_cz(self):
        return [
            None,
            'Pondělí',
            'Úterý',
            'Středa',
            'Čtvrtek',
            'Pátek',
            'Sobota',
            'Neděle',
        ][self.local_date.isoweekday()]

    def __unicode__(self):
        return formats[self.format].format(s=self.local_date, d=self)
    __str__ = __unicode__

    def __html__(self):
        attribs = [
            'data-dateformat="%s"' % self.format,
            'datetime="%sZ"' % self.utc_date.isoformat(),
            'title="%s"' % FormattedDate(self.utc_date, 'title'),
        ]
        return '<time %s>%s</time>' % (
            ' '.join(attribs),
            self)


def format_date(date, **kwargs):
    kwargs.setdefault('format', 'date')
    return FormattedDate(date, **kwargs)


def json(data):
    return Markup(json_module.dumps(data))


def js_export(**decls):
    exports = []
    for name, data in decls.items():
        dump = json_module.dumps(
            data,
            ensure_ascii=False,
            separators=(',', ':'),
            sort_keys=True,
        )
        exports.append(Markup('var %s=%s;' % (name, dump)))
    return Markup().join(exports)
