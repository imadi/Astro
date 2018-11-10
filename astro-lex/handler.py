import json
import os
import re
import traceback

import boto3

from utils.Constants import ERROR_MESSAGE
from utils.LexHelpers import get_geo_location, build_message, build_response_options, build_response_card, \
    get_date_from_text, elicit_slot, delegate, close

lambda_client = boto3.client('lambda')

dynamodb = boto3.resource('dynamodb', region_name=os.environ['REGION'])


def lex(event, context):
    print(json.dumps(event))
    try:
        session_attributes = event["sessionAttributes"]
        source = event["invocationSource"]
        calendars_language_list = supported_calendars_languages()
        slots = event["currentIntent"]["slots"]
        calendar_to_use = get_slot_value(slots.get("Calendar"))
        location = get_slot_value(slots.get("Location"))
        date = get_slot_value(slots.get("Date"))
        intent_name = event["currentIntent"]["name"]
        slots_details = event["currentIntent"]["slotDetails"]
        date = get_date_from_ip(date, event, slots, slots_details)
        if source == "DialogCodeHook":
            if location and get_geo_location(location) is None:
                return elicit_slot(session_attributes, intent_name, slots, "Location",
                                   build_message("Invalid location '%s'. Please enter the location" % location), None)
            if date is None:
                return elicit_slot(session_attributes, intent_name, slots, "Date",
                                   build_message("Please enter the date"), None)
            if intent_name in os.environ["ALLOWED_INTENTS_FOR_CALENDAR"].split(","):
                supported_language_names = [calendar_language["Language"] for calendar_language in
                                            calendars_language_list]
                if not (calendar_to_use and calendar_to_use in supported_language_names):
                    supported_calendars = build_response_options(supported_language_names)
                    return elicit_slot(session_attributes, event["currentIntent"]["name"], slots, "Calendar",
                                       build_message("Please select the calendar to use"),
                                       build_response_card("Calendars", "Supported Calendars", supported_calendars))
            return delegate(session_attributes, slots)
        if calendar_to_use:
            calendar_to_use = next(
                filter(lambda calendar_lang: calendar_lang["Language"] == calendar_to_use, calendars_language_list))
        date_utterance = slots_details["Date"]["originalValue"]
        date = get_date_from_text(date_utterance, location)
        event["currentIntent"]["slots"]["Date"] = date
        json_resp = invoke_lambda_function(calendar_to_use, location, date, event)
        return close(session_attributes, 'Fulfilled', {
            "contentType": 'PlainText',
            "content": format_close_response(json_resp)
        })
    except Exception as e:
        print("exception", e)
        traceback.print_exc()
        return close(event["sessionAttributes"], 'Fulfilled', {
            "contentType": 'PlainText',
            "content": ERROR_MESSAGE
        })


def get_date_from_ip(date, event, slots, slots_details):
    inp_text = event["inputTranscript"]
    text_list = re.findall(r"^today|tomorrow|yesterday", inp_text.lower())
    if len(text_list) > 0:
        date = slots["Date"] = slots_details["Date"]["originalValue"] = text_list[0]
    else:
        slots_details["Date"] = {}
        slots_details["Date"]["originalValue"] = date
    return date


def invoke_lambda_function(calendar_to_use, location, date, event):
    language_code = calendar_to_use.get("Code") if calendar_to_use else ""
    invoke_response = lambda_client.invoke(FunctionName=os.environ["PANCHANGA_FUNCTION_TO_INVOKE"],
                                           InvocationType='RequestResponse',
                                           Payload=json.dumps(
                                               {"location": location, "language_code": language_code,
                                                "date": date, "event": event})
                                           )
    json_resp = json.loads(invoke_response['Payload'].read().decode("utf-8"))
    return json_resp


def format_close_response(json_resp):
    response_string = "%s. Thanks for using Astro Bot. Here are the details" % json_resp["Greeting"]
    if json_resp.get("Day"):
        response_string += "\n Day : %s" % json_resp.get("Day")
    if json_resp.get("Month"):
        response_string += "\n Month : %s" % json_resp.get("Month")
    if json_resp.get("Tithi/Date"):
        response_string += "\n Tithi/Date : %s" % json_resp.get("Tithi/Date")
    if json_resp.get("Star"):
        response_string += "\n Star : %s" % json_resp.get("Star")
    if json_resp.get("Sunrise"):
        response_string += "\n Sunrise : %s" % json_resp.get("Sunrise")
    if json_resp.get("Sunset"):
        response_string += "\n Sunset : %s" % json_resp.get("Sunset")
    if json_resp.get("Moonrise"):
        response_string += "\n Moonrise : %s" % json_resp.get("Moonrise")
    if json_resp.get("Moonset"):
        response_string += "\n Moonset : %s" % json_resp.get("Moonset")
    return response_string


def supported_calendars_languages():
    table = dynamodb.Table('SupportedCalendarLanguages')
    return table.scan()["Items"]


def get_slot_value(text):
    return re.sub(r'[^\x00-\x7F]+', '', text.capitalize()) if text else text
