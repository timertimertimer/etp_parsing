import logging
import re
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


def increase_time_days(time_from, days):
    time_delta = timedelta(days=days)
    time_from = datetime.strptime(time_from, '%d.%m.%Y')
    time_to = time_from + time_delta
    return time_to.strftime('%d.%m.%Y')


def increase_date_from(date_from, days):
    time_delta = timedelta(days=days)
    date_from = datetime.strptime(date_from, '%d.%m.%Y %H:%S')
    date_from = date_from + time_delta
    return date_from.strftime('%d.%m.%Y %H:%S')


################___________FORMAT_____TIME_______##############
def format_time_strftime(func):
    def wrapper(*args):
        t = func(*args)
        if t:
            return t.strftime('%Y-%m-%d %H:%M:%S')

    return wrapper


@format_time_strftime
def format_time(strtime):
    pattern = re.compile('\d{1,2}\.\d{1,2}\.\d{2,4}.*?\d{1,2}\:\d{1,2}')
    strtime = ''.join(pattern.findall(strtime))
    if strtime:
        date = strtime
        return datetime.strptime(date, '%d.%m.%Y %H:%M')


@format_time_strftime
def format_time_period(strtime):
    try:
        if strtime:
            date = str(strtime).strip(
                '\n, -').replace('- ', '').replace('&nbsp;', '')
            return datetime.strptime(date, '%d.%m.%Y %H:%M:%S')
        else:
            return None
    except:
        return None


def return_parse_date():
    return datetime.now().strftime('%Y-%m-%d %H:%M:%S')


def return_servertime():
    return datetime.now().strftime('%H:%M:%S')


def increase_time_seconds(time_from, seconds):
    time_delta = timedelta(seconds=seconds)
    time_from = datetime.strptime(time_from, '%H:%M:%S')
    time_to = time_from + time_delta
    return time_to.strftime('%H:%M:%S')
