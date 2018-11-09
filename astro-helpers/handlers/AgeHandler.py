from utils import DateUtils


def handle(date):
    days_passed = DateUtils.get_days_passed_from_current_date(DateUtils.get_date_from_str(date))
    return "I am {} days old".format(days_passed)
