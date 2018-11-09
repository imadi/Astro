import swisseph as swe
from datetime import datetime
from math import ceil

import pytz

from utils.Helpers import geolocator, tf, utc, Place, solar_longitude, sunrise, lunar_phase, lunar_longitude, \
    inverse_lagrange, to_dms, unwrap_angles, new_moon, elapsed_year


def get_geo_location(city_name):
    location = geolocator.geocode(city_name)
    if location:
        today = datetime.now()
        tz_target = pytz.timezone(tf.timezone_at(lat=location.latitude, lng=location.longitude))
        tz = (utc.localize(today) - tz_target.localize(today)).total_seconds() / 3600
        return Place(location.latitude, location.longitude, tz)
    else:
        return None


def raasi(julian_day):
    """Zodiac of given julian_day. 1 = Mesha, ... 12 = Meena"""
    swe.set_sid_mode(swe.SIDM_LAHIRI)
    s = solar_longitude(julian_day)
    solar_nirayana = (solar_longitude(julian_day) - swe.get_ayanamsa_ut(julian_day)) % 360
    # 12 rasis occupy 360 degrees, so each one is 30 degrees
    return ceil(solar_nirayana / 30.)


def ritu(masa_num):
    """0 = Vasanta,...,5 = Shishira"""
    return (masa_num - 1) // 2


def days(julian_day):
    """Weekday for given Julian day. 0 = Sunday, 1 = Monday,..., 6 = Saturday"""
    return int(ceil(julian_day + 1) % 7)


def dates(julian_day, place):
    tz = place.timezone
    rise = sunrise(julian_day, place)[0] - tz / 24

    moon_phase = lunar_phase(rise)
    today = ceil(moon_phase / 12)
    degrees_left = today * 12 - moon_phase

    offsets = [0.25, 0.5, 0.75, 1.0]
    lunar_long_diff = [(lunar_longitude(rise + t) - lunar_longitude(rise)) % 360 for t in offsets]
    solar_long_diff = [(solar_longitude(rise + t) - solar_longitude(rise)) % 360 for t in offsets]
    relative_motion = [moon - sun for (moon, sun) in zip(lunar_long_diff, solar_long_diff)]

    y = relative_motion
    x = offsets
    # compute fraction of day (after sunrise) needed to traverse 'degrees_left'
    approx_end = inverse_lagrange(x, y, degrees_left)
    end_time = (rise + approx_end - julian_day) * 24 + tz
    answer = [int(today), to_dms(end_time)]

    moon_phase_tmrw = lunar_phase(rise + 1)
    tomorrow = ceil(moon_phase_tmrw / 12)
    is_skipped = (tomorrow - today) % 30 > 1
    if is_skipped:
        leap_tithi = today + 1
        degrees_left = leap_tithi * 12 - moon_phase
        approx_end = inverse_lagrange(x, y, degrees_left)
        end_time = (rise + approx_end - julian_day) * 24 + place.timezone
        answer += [int(leap_tithi), to_dms(end_time)]
    return answer


def stars(julian_day, place):
    tz = place.timezone
    swe.set_sid_mode(swe.SIDM_LAHIRI)

    rise = sunrise(julian_day, place)[0] - tz / 24.  # Sunrise at UT 00:00

    offsets = [0.0, 0.25, 0.5, 0.75, 1.0]
    longitudes = [(lunar_longitude(rise + t) - swe.get_ayanamsa_ut(rise)) % 360 for t in offsets]

    nak = ceil(longitudes[0] * 27 / 360)

    y = unwrap_angles(longitudes)
    x = offsets
    approx_end = inverse_lagrange(x, y, nak * 360 / 27)
    end_time = (rise - julian_day + approx_end) * 24 + tz
    answer = [int(nak), to_dms(end_time)]

    nak_tmrw = ceil(longitudes[-1] * 27 / 360)
    is_skipped = (nak_tmrw - nak) % 27 > 1
    if is_skipped:
        leap_nak = nak + 1
        approx_end = inverse_lagrange(offsets, longitudes, leap_nak * 360 / 27)
        end_time = (rise - julian_day + approx_end) * 24 + tz
        answer += [int(leap_nak), to_dms(end_time)]

    return answer


def months(julian_day, place):
    """Returns lunar month and if it is adhika or not.
       1 = Chaitra, 2 = Vaisakha, ..., 12 = Phalguna"""
    ti = dates(julian_day, place)[0]
    critical = sunrise(julian_day, place)[0]  # - tz/24 ?
    last_new_moon = new_moon(critical, ti, -1)
    next_new_moon = new_moon(critical, ti, +1)
    this_solar_month = raasi(last_new_moon)
    next_solar_month = raasi(next_new_moon)
    is_leap_month = (this_solar_month == next_solar_month)
    maasa = this_solar_month + 1
    if maasa > 12: maasa = (maasa % 12)
    return int(maasa)


def samvatsara(julian_day, maasa_num):
    kali = elapsed_year(julian_day, maasa_num)[0]
    # Change 14 to 0 for North Indian tradition
    if kali >= 4009:
        kali = (kali - 14) % 60
    return (kali + 27 + int((kali * 211 - 108) / 18000)) % 60
