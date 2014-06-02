import datetime

import pytz

local_timezone = pytz.timezone('Europe/Prague')

formats = dict(
    date='{0.day}. {0.month}. {0.year} {0.hour:02}:{0.minute:02}',
    compact='{0.hour:02}:{0.minute:02}',
)


class FormattedDate(object):
    def __init__(self, date, format, pubdate=False):
        assert '"' not in format
        self.format = format
        self.utc_date = date
        self.local_date = pytz.utc.localize(date).astimezone(local_timezone)
        self.pubdate = pubdate

    def __unicode__(self):
        return formats[self.format].format(self.local_date)
    __str__ = __unicode__

    def __html__(self):
        attribs = ['data-dateformat="%s"' % self.format]
        if self.pubdate:
            attribs.append(' pubdate="pubdate"')
        return '<time datetime="%sZ" %s>%s</time>' % (
            self.utc_date.isoformat(), ' '.join(attribs), self)


def format_date(date, **kwargs):
    kwargs.setdefault('format', 'date')
    return FormattedDate(date, **kwargs)
