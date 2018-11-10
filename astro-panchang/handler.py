import json
import os
import swisseph as swe

from handlers import WeatherHandler, AstroHandler
from utils.AstroUtils import get_day_name, get_month_name, get_star_name, get_date_name
from utils.Constants import COLON_SEPARATOR
from utils.EphemerisUtils import get_geo_location
from utils.Helpers import get_date, greeting, sunrise, sunset, moonrise, moonset, \
    join_list
from utils.Intent import Intent

# Julian Day number as on (year, month, day) at 00:00 UTC
gregorian_to_julian_day = lambda date: swe.julday(date.year, date.month, date.day, 0.0)


def panchang(event, context):
    print(json.dumps(event))
    place = get_geo_location(event.get("location") if event.get("location") else os.environ['DEFAULT_LOCATION'])
    received_event = event["event"]
    intent_name = received_event["currentIntent"]["name"]
    if place is None:
        return {"error_message": "Invalid Location %s" % (event.get("location"))}
    julian_day = gregorian_to_julian_day(get_date(place, event.get("date")))
    language_code = event.get("language_code")
    if intent_name == Intent.WEATHER.value:
        return WeatherHandler.handle(received_event, julian_day, place)
    elif intent_name == Intent.ASTRO.value:
        return AstroHandler.handle(received_event, julian_day, place, language_code)
    day_str = get_day_name(julian_day)
    month_str = get_month_name(julian_day, place)
    date_str = get_date_name(julian_day, place)
    star_str = get_star_name(julian_day, place)

    json_response = {
        "Greeting": greeting(place),
        "Day": day_str[language_code],
        "Month": month_str[language_code],
        "Tithi/Date": date_str[language_code],
        "Star": star_str[language_code],
        "Sunrise": join_list(sunrise(julian_day, place)[1], COLON_SEPARATOR),
        "Sunset": join_list(sunset(julian_day, place)[1], COLON_SEPARATOR),
        "Moonrise": join_list(moonrise(julian_day, place), COLON_SEPARATOR),
        "Moonset": join_list(moonset(julian_day, place), COLON_SEPARATOR)
    }

    return json_response
