from utils.Constants import COLON_SEPARATOR
from utils.Helpers import greeting, join_list, sunrise, sunset, moonrise, moonset
from utils.WeatherEntity import WeatherEntity


def handle(event, julian_day, place):
    json_response = {}
    slots = event["currentIntent"]["slots"]
    entity = slots["WeatherEntity"].lower()
    if entity == WeatherEntity.SUN_RISE.value:
        json_response = {
            "Greeting": greeting(place),
            "Sunrise": join_list(sunrise(julian_day, place)[1], COLON_SEPARATOR)
        }
    elif entity == WeatherEntity.SUN_SET.value:
        json_response = {
            "Greeting": greeting(place),
            "Sunset": join_list(sunset(julian_day, place)[1], COLON_SEPARATOR)
        }
    elif entity == WeatherEntity.MOON_RISE.value:
        json_response = {
            "Greeting": greeting(place),
            "Moonrise": join_list(moonrise(julian_day, place), COLON_SEPARATOR)
        }
    elif entity == WeatherEntity.MOON_SET.value:
        json_response = {
            "Greeting": greeting(place),
            "Moonset": join_list(moonset(julian_day, place), COLON_SEPARATOR)
        }
    return json_response
