import logging
import re
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


# ###############___________FORMAT_____TIME_______##############
def format_time_strftime(func):
    def wrapper(*args):
        t = func(*args)
        if t:
            return t.strftime('%Y-%m-%d %H:%M:%S')

    return wrapper


@format_time_strftime
def format_time(strtime):
    pattern = re.compile(r'\d{1,2}\.\d{1,2}\.\d{2,4}.*?\d{1,2}\:\d{1,2}\:\d{1,2}')
    strtime = ''.join(pattern.findall(strtime))
    if strtime:
        date = strtime
        return datetime.strptime(date, '%d.%m.%Y %H:%M:%S')


@format_time_strftime
def format_time_auction(strtime):
    pattern = re.compile(r'\d{1,2}\.\d{1,2}\.\d{2,4}.*?\d{1,2}\:\d{1,2}')
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
