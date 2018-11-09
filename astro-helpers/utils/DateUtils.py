from datetime import datetime
import pytz


def get_current_date():
    tz = pytz.timezone('Asia/Kolkata')
    return datetime.now().astimezone(tz).date()


def get_days_passed_from_current_date(before):
    return abs(before - get_current_date()).days


def get_date_from_str(date):
    return datetime.strptime(date, "%Y-%m-%d").date()
