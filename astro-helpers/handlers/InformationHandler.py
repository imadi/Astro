import os
import traceback
import boto3

dynamodb = boto3.resource('dynamodb', region_name=os.environ['REGION'])


def handle(event):
    table = dynamodb.Table('Information')
    slots = event["currentIntent"]["slots"]
    entity = slots["entity"].capitalize()
    try:
        return table.get_item(Key={'Entity': entity})["Item"]["About"]
    except Exception as e:
        traceback.print_stack()
        return None
