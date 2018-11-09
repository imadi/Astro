import collections
import ssl
import swisseph as swe
from datetime import datetime

import certifi
import pytz
from geopy.geocoders import options, Nominatim
from pytz import timezone
from timezonefinder import TimezoneFinder

from Greeting import Greeting

ctx = ssl.create_default_context(cafile=certifi.where())
options.default_ssl_context = ctx

geolocator = Nominatim(user_agent="panchanga")
utc = pytz.utc
tf = TimezoneFinder()

Date = collections.namedtuple('Date', ['year', 'month', 'day'])
Place = collections.namedtuple('Location', 'latitude longitude timezone')


def to_dms(deg):
    d = int(deg)
    mins = (deg - d) * 60
    m = int(mins)
    s = int(round((mins - m) * 60))
    return [d, m, s]


def solar_longitude(julian_day):
    """Solar longitude at given instant julian day"""
    data = swe.calc_ut(julian_day, swe.SUN, flag=swe.FLG_SWIEPH)
    return data[0]  # in degrees


def lunar_longitude(julian_day):
    """Lunar longitude at given instant julian day"""
    data = swe.calc_ut(julian_day, swe.MOON, flag=swe.FLG_SWIEPH)
    return data[0]  # in degrees


def sunrise(julian_day, place):
    """Sunrise when centre of disc is at horizon for given date and place"""
    lat, lon, tz = place
    result = swe.rise_trans(julian_day - tz / 24, swe.SUN, lon, lat, rsmi=swe.BIT_DISC_CENTER + swe.CALC_RISE)
    rise = result[1][0]  # julian-day number
    # Convert to local time
    return [rise + tz / 24, to_dms((rise - julian_day) * 24 + tz)]


def sunset(julian_day, place):
    """Sunset when centre of disc is at horizon for given date and place"""
    lat, lon, tz = place
    result = swe.rise_trans(julian_day - tz / 24, swe.SUN, lon, lat, rsmi=swe.BIT_DISC_CENTER + swe.CALC_SET)
    setting = result[1][0]  # julian-day number
    # Convert to local time
    return [setting + tz / 24., to_dms((setting - julian_day) * 24 + tz)]


def moonrise(julian_day, place):
    """Moonrise when centre of disc is at horizon for given date and place"""
    lat, lon, tz = place
    result = swe.rise_trans(julian_day - tz / 24, swe.MOON, lon, lat, rsmi=swe.BIT_DISC_CENTER + swe.CALC_RISE)
    rise = result[1][0]  # julian-day number
    # Convert to local time
    return to_dms((rise - julian_day) * 24 + tz)


def moonset(julian_day, place):
    """Moonset when centre of disc is at horizon for given date and place"""
    lat, lon, tz = place
    result = swe.rise_trans(julian_day - tz / 24, swe.MOON, lon, lat, rsmi=swe.BIT_DISC_CENTER + swe.CALC_SET)
    setting = result[1][0]  # julian-day number
    # Convert to local time
    return to_dms((setting - julian_day) * 24 + tz)


def lunar_phase(julian_day):
    solar_long = solar_longitude(julian_day)
    lunar_long = lunar_longitude(julian_day)
    moon_phase = (lunar_long - solar_long) % 360
    return moon_phase


def inverse_lagrange(x, y, ya):
    """Given two lists x and y, find the value of x = xa when y = ya, i.e., f(xa) = ya"""
    total = 0
    for i in range(len(x)):
        numer = 1
        denom = 1
        for j in range(len(x)):
            if j != i:
                numer *= (ya - y[j])
                denom *= (y[i] - y[j])
        total += numer * x[i] / denom
    return total


def unwrap_angles(angles):
    result = angles
    for i in range(1, len(angles)):
        if result[i] < result[i - 1]: result[i] += 360
    return result


# New moon day: sun and moon have same longitude (0 degrees = 360 degrees difference)
# Full moon day: sun and moon are 180 deg apart
def new_moon(julian_day, tithi_, opt=-1):
    """Returns julian_dayN, where
       opt = -1:  julian_dayN < julian_day such that lunar_phase(julian_dayN) = 360 degrees
       opt = +1:  julian_dayN >= julian_day such that lunar_phase(julian_dayN) = 360 degrees
    """
    if opt == -1:  start = julian_day - tithi_  # previous new moon
    if opt == +1:  start = julian_day + (30 - tithi_)  # next new moon
    # Search within a span of (start +- 2) days
    x = [-2 + offset / 4 for offset in range(17)]
    y = [lunar_phase(start + i) for i in x]
    y = unwrap_angles(y)
    y0 = inverse_lagrange(x, y, 360)
    return start + y0


def elapsed_year(julian_day, maasa_num):
    sidereal_year = 365.25636
    ahar = julian_day - 588465.5
    kali = int((ahar + (4 - maasa_num) * 30) / sidereal_year)
    saka = kali - 3179
    return kali, saka


def get_date(place, date):
    now = datetime.strptime(date, "%Y-%m-%d").date() if date else get_current_datetime(place)
    return Date(now.year, now.month, now.day)


def greeting(place):
    now = get_current_datetime(place)
    if now.hour < 12:
        return Greeting.GM.value
    elif 12 <= now.hour < 16:
        return Greeting.GA.value
    else:
        return Greeting.GE.value


def get_current_datetime(place):
    tz_target = str(pytz.timezone(tf.timezone_at(lat=place.latitude, lng=place.longitude)))
    return datetime.now(timezone(tz_target))


def join_list(lst, char_to_join):
    return char_to_join.join(str(n) for n in lst)
