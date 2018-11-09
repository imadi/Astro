import os

from handlers import AgeHandler,InformationHandler
from utils.Intent import Intent


def handle(event, context):
    intent_name = event["currentIntent"]["name"]
    message = ""
    if intent_name == Intent.AGE.value:
        message = AgeHandler.handle(date=os.environ['DATE'])
    elif intent_name == Intent.INFO.value:
        message = InformationHandler.handle(event)
    return close(event["sessionAttributes"], 'Fulfilled', {
        "contentType": 'PlainText',
        "content": message
    })


def close(session_attributes, fulfillment_state, message):
    return {
        "sessionAttributes": session_attributes,
        "dialogAction": {
            "type": "Close",
            "fulfillmentState": fulfillment_state,
            "message": message
        }
    }
