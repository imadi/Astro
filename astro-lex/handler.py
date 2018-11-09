import json
import boto3
import os
import traceback
from utils.Constants import ERROR_MESSAGE
from utils.LexHelpers import *
import re

lambda_client = boto3.client('lambda')

dynamodb = boto3.resource('dynamodb', region_name=os.environ['REGION'])


def lex(event, context):
    print(json.dumps(event))
    try:
        session_attributes = event["sessionAttributes"]
        source = event["invocationSource"]
        calendars_language_list = supported_calendars_languages()
        slots = event["currentIntent"]["slots"]
        calendar_to_use = get_slot_value(slots["Calendar"])
        location = get_slot_value(slots["Location"])
        date = get_slot_value(slots["Date"])
        intent_name = event["currentIntent"]["name"]
        if source == "DialogCodeHook":
            if location and get_geo_location(location) is None:
                return close(session_attributes, 'Fulfilled', {
                    "contentType": 'PlainText',
                    "content": "Invalid location '%s'" % location
                })
            if date is None:
                return close(session_attributes, 'Fulfilled', {
                    "contentType": 'PlainText',
                    "content": "Invalid date."
                })
            if intent_name in os.environ["ALLOWED_INTENTS_FOR_CALENDAR"].split(","):
                supported_language_names = [calendar_language["Language"] for calendar_language in
                                            calendars_language_list]
                if not (calendar_to_use and calendar_to_use in supported_language_names):
                    supported_calendars = build_response_options(supported_language_names)
                    return elicit_slot(session_attributes, event["currentIntent"]["name"], slots, "Calendar",
                                       build_message("Please select the calendar to use"),
                                       build_response_card("Calendars", "Supported Calendars", supported_calendars))
            return delegate(session_attributes, slots)
        calendar_to_use = next(
            filter(lambda calendar_lang: calendar_lang["Language"] == calendar_to_use, calendars_language_list))
        slots_details = event["currentIntent"]["slotDetails"]
        date_utterance = slots_details["Date"]["originalValue"]
        date = get_date_from_text(date_utterance, location)
        json_resp = invoke_lambda_function(calendar_to_use, location, date, slots)
        return close(session_attributes, 'Fulfilled', {
            "contentType": 'PlainText',
            "content": format_close_response(json_resp)
        })
    except Exception as e:
        print("exception", e)
        traceback.print_stack()
        return close(event["sessionAttributes"], 'Fulfilled', {
            "contentType": 'PlainText',
            "content": ERROR_MESSAGE
        })


def invoke_lambda_function(calendar_to_use, location, date, slots):
    invoke_response = lambda_client.invoke(FunctionName=os.environ["PANCHANGA_FUNCTION_TO_INVOKE"],
                                           InvocationType='RequestResponse',
                                           Payload=json.dumps(
                                               {"location": location, "language_code": calendar_to_use["Code"],
                                                "date": date, "slots": slots})
                                           )
    json_resp = json.loads(invoke_response['Payload'].read().decode("utf-8"))
    return json_resp


def format_close_response(json_resp):
    return """{}. Thanks for using Astro Bot. Here are the details
               \n Day : {} \n Month : {} \n Tithi/Date : {} \n Star : {} \n Sunrise : {} \n Sunset : {}""" \
        .format(json_resp["Greeting"], json_resp["Day"], json_resp["Month"], json_resp["Tithi/Date"],
                json_resp["Star"], json_resp["Sunrise"], json_resp["Sunset"])


def supported_calendars_languages():
    table = dynamodb.Table('SupportedCalendarLanguages')
    return table.scan()["Items"]


def get_slot_value(text):
    return re.sub(r'[^\x00-\x7F]+', '', text.capitalize()) if text else text
