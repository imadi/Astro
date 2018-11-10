from datetime import datetime

import pytz


def get_current_date():
    tz = pytz.timezone('Asia/Kolkata')
    return datetime.now().astimezone(tz).date()


def get_days_passed_from_current_date(before):
    return abs(before - get_current_date()).days


def get_date_from_str(date, date_format):
    return datetime.strptime(date, date_format).date()


def get_str_from_date(date, date_format):
    return datetime.strftime(date, date_format)
