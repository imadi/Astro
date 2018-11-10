from utils.AstroEntity import AstroEntity
from utils.AstroUtils import get_day_name, get_month_name, get_star_name, get_date_name
from utils.Helpers import greeting


def handle(event, julian_day, place, language_code):
    json_response = {}
    slots = event["currentIntent"]["slots"]
    entity = slots["AstroEntity"].lower()
    print("entity", entity)
    if entity == AstroEntity.TITHI.value:
        date_str = get_date_name(julian_day, place)
        json_response = {
            "Greeting": greeting(place),
            "Tithi/Date": date_str[language_code]
        }
    elif entity == AstroEntity.STAR.value:
        star_str = get_star_name(julian_day, place)
        json_response = {
            "Greeting": greeting(place),
            "Star": star_str[language_code]
        }
    elif entity == AstroEntity.MONTH.value:
        month_str = get_month_name(julian_day, place)
        json_response = {
            "Greeting": greeting(place),
            "Month": month_str[language_code]
        }
    elif entity == AstroEntity.DAY.value:
        day_str = get_day_name(julian_day)
        json_response = {
            "Greeting": greeting(place),
            "Day": day_str[language_code]
        }
    return json_response
