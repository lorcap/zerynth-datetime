# main.py
#
# This is file is meant to be run through both Zerynth and Python3
# as to compare the two implementations.

try:
    # works in Zerynth
    import streams
    streams.serial()

    import datetime as datetimelib

    timedelta     = datetimelib.timedelta
    timezone      = datetimelib.timezone
    datetime      = datetimelib.datetime
    date          = datetime
    time          = timedelta
    combine       = datetimelib.combine
    fromisoformat = datetimelib.fromisoformat
    fromordinal   = datetimelib.fromordinal

except:
#-if False
    # works in Python
    import sys
    del sys.path[0] # search for system modules only
    import datetime as datetimelib

    class timedelta(datetimelib.timedelta):
        def add     (self, other): return self._ctor(self.__add__     , other)
        def sub     (self, other): return self._ctor(self.__sub__     , other)
        def mul     (self, other): return self._ctor(self.__mul__     , other)
        def abs     (self       ): return self._ctor(self.__abs__            )
        def neg     (self       ): return self._ctor(self.__neg__            )
        def mod     (self, other): return self._ctor(self.__mod__     , other)
        def divmod  (self, other): return self._ctor(self.__divmod__  , other)
        def truediv (self, other): return self._ctor(self.__truediv__ , other)
        def floordiv(self, other): return self._ctor(self.__floordiv__, other)
        def lt      (self, other): return self._ctor(self.__lt__      , other)
        def le      (self, other): return self._ctor(self.__le__      , other)
        def eq      (self, other): return self._ctor(self.__eq__      , other)
        def ge      (self, other): return self._ctor(self.__ge__      , other)
        def gt      (self, other): return self._ctor(self.__gt__      , other)
        def bool    (self       ): return self._ctor(self.__bool__           )

        def __str__(self):
            return self.isoformat()

        def isoformat(self):
            t = self.tuple()
            if 0 <= self.total_seconds() < 86400:
                return "%02d:%02d:%02d" % t[2:]
            else:
                return "%s%dd %02d:%02d:%02d" % t

        def total_seconds(self):
            return round(super().total_seconds())

        def tuple(self, sign_pos=''):
            s = self.total_seconds()
            m, s = divmod(s, 60)
            h, m = divmod(m, 60)
            d, h = divmod(h, 24)
            if d < 0:
                d = -d
                g = '-'
            else:
                g = sign_pos
            return g, d, h, m, s

        def _ctor(self, method, other=None):
            result = method() if other is None else method(other)
            if isinstance(result, datetimelib.timedelta):
                return type(self)(seconds=result.total_seconds())
            elif method == self.__divmod__:
                return result[0], type(self)(seconds=result[1].total_seconds())
            else:
                return result

    # Inheriting from datetimelib.timezone is not possible
    class timezone(datetimelib.tzinfo):
        def __init__(self, offset, name=None):
            self._tz = datetimelib.timezone(offset) if name is None\
                  else datetimelib.timezone(offset, name)

        def __str__(self):
            return self.tzname(None)

        def utcoffset(self, dt):
            return self._tz.utcoffset(dt).add(self.dst(dt))

        def dst(self, dt):
            return self._tz.dst(dt)

        def tzname(self, dt):
            return self._tz.tzname(dt)

        def isoformat(self, dt):
            sign, day, hour, minute, second = self.utcoffset(dt).tuple('+')
            if hour == 0 and minute == 0:
                return 'UTC'
            return 'UTC%s%02d:%02d' % (sign, hour, minute)

    timezone.utc = timezone(timedelta(0))

    date = datetimelib.date
    time = datetimelib.time

    class datetime(datetimelib.datetime):
        add = datetimelib.datetime.__add__
        sub = datetimelib.datetime.__sub__
        lt  = datetimelib.datetime.__lt__
        le  = datetimelib.datetime.__le__
        eq  = datetimelib.datetime.__eq__
        ge  = datetimelib.datetime.__ge__
        gt  = datetimelib.datetime.__gt__

        def date(self):
            return self.combine(super().date(), datetimelib.time(), self.tzinfo)

        def time(self):
            return timedelta(hours=self.hour, minutes=self.minute, seconds=self.second)

        def dateisoformat(self):
            return self.isoformat()[:10]

        def timeisoformat(self):
            return self.isoformat()[11:19]

        def tuple(self):
            return super().year, super().month , super().day,\
                   super().hour, super().minute, super().second,\
                   super().tzinfo

        @classmethod
        def combine(cls, date, time, tzinfo=True):
            return super().combine(date, time) if tzinfo is True\
              else super().combine(date, time, tzinfo)

        @classmethod
        def fromisoformat(cls, s):
            return super().fromisoformat(s)

    combine       = datetime.combine
    fromisoformat = datetime.fromisoformat
    fromordinal   = datetime.fromordinal

#-endif
    pass

### common ############################################################

test_total = 0
test_pass = 0
test_gran_total = 0
test_gran_pass = 0

class cet(timezone):
    # Central European Time (see https://en.wikipedia.org/wiki/Summer_time_in_Europe)
    _subclass = timezone

    def __init__(self):
        self._subclass.__init__(self, timedelta(hours=1))

    def dst(self, dt):
        return timedelta(hours=1) if self.isdst(dt) else timedelta(0)

    def tzname(self, dt):
        return 'CEST' if self.isdst(dt) else 'CET'

    def isdst(self, dt):
        if dt is None:
            return False
        year, month, day, hour, minute, second, tz = dt.tuple()
        if 3 < month < 10:
            return True
        if month == 3:
            beg = 31 - (5*year//4 + 4) % 7 # last Sunday of March
            if day < beg: return False
            if day > beg: return True
            return hour >= 3
        if month == 10:
            end = 31 - (5*year//4 + 1) % 7 # last Sunday of October
            if day < end: return True
            if day > end: return False
            return hour < 3
        return False

#-if False
timezone = datetimelib.timezone
#-endif

def test (name, result=None, expect=None):
    global test_total
    global test_pass
    global test_gran_total
    global test_gran_pass

    if result == None and expect == None:
        if test_total:
            print('Total pass: %d/%d' %(test_pass, test_total))
        print('--- ', name, ' ---')
        test_total = 0
        test_pass = 0
    else:
        print("#%d: %s: " % (test_total, name), end='')
        result_str = str(result)
        expect_str = str(expect)
        if result_str == expect_str:
            print("%s (pass)" % result_str)
            test_pass += 1
            test_gran_pass += 1
        else:
            print("fail:\n  expected: %s\n  got: %s" % (expect_str, result_str))

        test_total += 1
        test_gran_total += 1

### main ##############################################################

try:
    test('timedelta')

    td1 = timedelta(hours=5, minutes=4, seconds=3, days=2, weeks=1)
    test('__init__()', td1, '9d 05:04:03')
    test('total_seconds()', td1.total_seconds(), 795843)

    td1 = timedelta(minutes=1)
    td1 = td1.add(timedelta(seconds=7))
    test('add(timedelta)', td1.total_seconds(), 67)
    td2 = td1.add(timedelta(minutes=1))
    test('add(timedelta)', td2.total_seconds(), 127)

    td1 = td1.sub(timedelta(seconds=33))
    test('sub(timedelta)', td1.total_seconds(), 34)
    td2 = td1.sub(timedelta(seconds=1))
    test('sub(timedelta)', td2.total_seconds(), 33)

    td1 = td1.mul(1.5)
    test('mul(float)', td1.total_seconds(), 51)
    td2 = td1.mul(0.5)
    test('mul(int)', td2.total_seconds(), 26)
    td2 = td1.mul(2)
    test('mul(int)', td2.total_seconds(), 102)

    test('truediv(timedelta)', td2.truediv(td1), 2.0)
    test('truediv(int)', td1.truediv(2).total_seconds(), 26)
    test('truediv(float)', td2.truediv(1.1).total_seconds(), 93)
    test('truediv(float)', td2.truediv(2.4).total_seconds(), 42)

    test('floordiv(timedelta)', td2.floordiv(td1), 2)
    test('floordiv(int)', td1.floordiv(2), '00:00:25')

    td1 = td1.sub(timedelta(seconds=10))
    test('mod(timedelta)', td2.mod(td1).total_seconds(), 20)

    q, r = td2.divmod(td1)
    test('divmod(timedelta).q', q, 2)
    test('divmod(timedelta).r', r.total_seconds(), 20)

    test('neg()', td1.neg().total_seconds(), -41)
    test('abs()', td1.abs().total_seconds(), 41)

    test('eq()', td2.eq(td1), False)
    test('le()', td2.le(td1), False)
    test('lt()', td2.lt(td1), False)
    test('ge()', td2.ge(td1), True)
    test('gt()', td2.gt(td1), True)
    test('bool()', td2.bool(), True)

    ###################################################################

    test('timedelta: example #1')
    # Components of another_year add up to exactly 365 days
    year = timedelta(days=365)
    another_year = timedelta(weeks=40, days=84, hours=23, minutes=50, seconds=600)
    print(year.eq(another_year))        # True
    print(year.total_seconds())         # 31536000

    test('timedelta: example #2')
    print('min:', timedelta.min)        #
    print('max:', timedelta.max)        #
    print('res:', timedelta.resolution) #
    ten_years = year.mul(10)
    print(ten_years)                    # 3650d 00:00:00
    nine_years = ten_years.sub(year)
    print(nine_years)                   # 3285d 00:00:00
    three_years = nine_years.floordiv(3)
    print(three_years)                  # 1095d 00:00:00

    ###################################################################

    test('timezone')

    tz1 = timezone(timedelta(hours=-1))
    test('__init__()', tz1, 'UTC-01:00')

    tz2 = cet()
    test('__init__()', tz2, 'CET')
    test('utcoffset(None )', tz2.utcoffset(None                      ), '01:00:00')
    test('utcoffset( 3-27)', tz2.utcoffset(datetime(2010,  3, 27, 12)), '01:00:00')
    test('utcoffset( 3-28)', tz2.utcoffset(datetime(2010,  3, 28, 12)), '02:00:00')
    test('utcoffset(10-30)', tz2.utcoffset(datetime(2010, 10, 30, 12)), '02:00:00')
    test('utcoffset(10-31)', tz2.utcoffset(datetime(2010, 10, 31, 12)), '01:00:00')

    ###################################################################

    test('timezone: example CET')

    print(tz2.isoformat(datetime(2011, 1, 1))) # +01:00
    print(tz2.tzname   (datetime(2011, 1, 1))) # CET
    print(tz2.isoformat(datetime(2011, 8, 1))) # +02:00
    print(tz2.tzname   (datetime(2011, 8, 1))) # CEST

    ###################################################################

    test('datetime')

    dt1 = datetime(1975, 8, 10, 0, 30, tzinfo=tz1)
    test('__init__()', dt1, '1975-08-10 00:30:00-01:00')
    test('date()', dt1.date(), '1975-08-10 00:00:00-01:00')
    test('time()', dt1.time().isoformat(), '00:30:00')
    test('astimezone()', dt1.astimezone(timezone.utc), '1975-08-10 01:30:00+00:00')

    test('combine()', combine(date(1980, 8, 13), time(8, 20)), '1980-08-13 08:20:00')
    test('toordinal()', dt1.toordinal(), 721210)
    test('fromordinal()', fromordinal(1234567), '3381-02-16 00:00:00')

    test('fromisoformat(Y-M-D)'          , fromisoformat('1975-08-10'               ), '1975-08-10 00:00:00')
    test('fromisoformat(Y-M-D h)'        , fromisoformat('1975-08-10 23'            ), '1975-08-10 23:00:00')
    test('fromisoformat(Y-M-D h:m)'      , fromisoformat('1975-08-10 23:30'         ), '1975-08-10 23:30:00')
    test('fromisoformat(Y-M-D h:m:s)'    , fromisoformat('1975-08-10 23:30:12'      ), '1975-08-10 23:30:12')
    test('fromisoformat(Y-M-D h:m:s+h:m)', fromisoformat('1975-08-10 23:30:12+01:00'), '1975-08-10 23:30:12+01:00')

    test('add()', dt1.add(datetimelib.timedelta(minutes=5)), '1975-08-10 00:35:00-01:00')
    test('sub()', dt1.sub(datetimelib.timedelta(minutes=5)), '1975-08-10 00:25:00-01:00')

    dt2 = datetime(1975, 8, 10, 0, 30, tzinfo=tz2)
    test('astimezone()', dt2.astimezone(timezone.utc), '1975-08-09 22:30:00+00:00')
    test('dateisoformat()', dt2.dateisoformat(), '1975-08-10')
    test('timeisoformat()', dt2.timeisoformat(), '00:30:00')
    test('sub()', int(dt2.sub(dt1).total_seconds()), -3*3600)
    test('sub()', int(dt1.sub(dt2).total_seconds()),  3*3600)

    test('lt()', dt1.lt(dt2), False)
    test('le()', dt1.le(dt2), False)
    test('eq()', dt1.eq(dt1), True)
    test('eq()', dt1.eq(dt2), False)
    test('ge()', dt1.ge(dt2), True)
    test('gt()', dt1.gt(dt2), True)

    ###################################################################

    test('datetime: example #1')
    print(datetime(2005, 7, 14, 12, 30))            # 2005-07-14 12:30:00
    dt = fromisoformat('2006-11-21 16:30+01:00')
    print(dt.add(timedelta(hours=23)))              # 2006-11-22 15:30:00+01:00
    tz1 = timezone(timedelta(hours=4, minutes=30))
    print(tz1)                                      # UTC+04:30
    dt = datetime(1900, 11, 21, 3, 30, tzinfo=tz1)
    print(dt)                                       # 1900-11-21 03:30:00+04:30
    print(dt.astimezone(timezone.utc))              # 1900-11-20 23:00:00+00:00

    ###################################################################

    test('done')
    print('Gran total pass: %d/%d' %(test_gran_pass, test_gran_total))

except Exception as e:
#-if False
    raise
#-endif
    print("Something bad happened:",e)
