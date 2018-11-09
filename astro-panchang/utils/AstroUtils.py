import os
import boto3

from utils.EphemerisUtils import days, dates, stars, months

dynamodb = boto3.resource('dynamodb', region_name=os.environ['REGION'])


def get_day_name(julian_day):
    day = days(julian_day)
    table = dynamodb.Table("Days")
    day_str = table.get_item(Key={'Number': day + 1})["Item"]["Name"]
    return day_str


def get_month_name(julian_day, place):
    month = months(julian_day, place)
    table = dynamodb.Table("Months")
    month_str = table.get_item(Key={'Number': month})["Item"]["Name"]
    return month_str


def get_star_name(julian_day, place):
    star = stars(julian_day, place)
    table = dynamodb.Table("Stars")
    star_str = table.get_item(Key={'Number': star[0]})["Item"]["Name"]
    return star_str


def get_date_name(julian_day, place):
    date = dates(julian_day, place)
    table = dynamodb.Table('Dates')
    date_str = table.get_item(Key={'Number': date[0]})["Item"]["Name"]
    return date_str
