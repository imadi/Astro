import ssl
from datetime import datetime, timedelta
import certifi
import pytz
from geopy.geocoders import options, Nominatim
from pytz import timezone
from utils.DialogActionType import DialogActionType
from timezonefinder import TimezoneFinder

ctx = ssl.create_default_context(cafile=certifi.where())
options.default_ssl_context = ctx

geolocator = Nominatim(user_agent="panchanga")
tf = TimezoneFinder()


# -------- Helpers to build responses which match the structure of the necessary dialog actions ------

def elicit_slot(session_attributes, intent_name, slots, slot_to_elicit, message, response_card):
    return {
        "sessionAttributes": session_attributes,
        "dialogAction": {
            "type": DialogActionType.ELICIT_SLOT.value,
            "intentName": intent_name,
            "slots": slots,
            "slotToElicit": slot_to_elicit,
            "message": message,
            "responseCard": response_card
        }
    }


def confirm_intent(session_attributes, intent_name, slots, message, response_card):
    return {
        "sessionAttributes": session_attributes,
        "dialogAction": {
            "type": DialogActionType.CONFIRM_INTENT.value,
            "intentName": intent_name,
            "slots": slots,
            "message": message,
            "responseCard": response_card
        }
    }


def close(session_attributes, fulfillment_state, message):
    return {
        "sessionAttributes": session_attributes,
        "dialogAction": {
            "type": DialogActionType.CLOSE.value,
            "fulfillmentState": fulfillment_state,
            "message": message
        }
    }


def delegate(session_attributes, slots):
    return {
        "sessionAttributes": session_attributes,
        "dialogAction": {
            "type": DialogActionType.DELEGATE.value,
            "slots": slots,
        },
    }


def build_message(message_content):
    return {
        "contentType": 'PlainText',
        "content": message_content,
    }


def build_response_options(options):
    response_options = []
    for option in options:
        temp = {
            "text": option,
            "value": option
        }
        response_options.append(temp)
    return response_options


def build_response_card(title, sub_title, options):
    buttons = []
    if options is not None:
        for i in range(0, min(5, len(options))):
            buttons.append(options[i])
    return {
        "contentType": "application/vnd.amazonaws.card.generic",
        "version": 1,
        "genericAttachments": [
            {
                "title": title,
                "subTitle": sub_title,
                "buttons": buttons
            }
        ]
    }


def key_exists(key, search):
    return True if key in search else False


def get_geo_location(city_name):
    return geolocator.geocode(city_name)


def get_current_date(city_name):
    place = get_geo_location(city_name)
    tz_target = str(pytz.timezone(tf.timezone_at(lat=place.latitude, lng=place.longitude)))
    return datetime.now(timezone(tz_target)).date()


def get_date_from_text(date_utterance, place):
    date = date_utterance
    if date_utterance.lower() == "today":
        date = (get_current_date(place)).strftime("%Y-%m-%d")
    elif date_utterance.lower() == "tomorrow":
        date = (get_current_date(place) + timedelta(days=1)).strftime("%Y-%m-%d")
    elif date_utterance.lower == "yesterday":
        date = (get_current_date(place) - timedelta(days=1)).strftime("%Y-%m-%d")
    return date
