import os

from utils.DateUtils import get_date_from_str, get_days_passed_from_current_date, get_str_from_date


def handle(event):
    date = os.environ['DATE']
    slots = event["currentIntent"]["slots"]
    date = get_date_from_str(date, "%Y-%m-%d")
    if slots["Dob"]:
        return "I was born on %s" % get_str_from_date(date, "%B %-d, %Y")
    days_passed = get_days_passed_from_current_date(date)
    return "I am %s days old" % days_passed
