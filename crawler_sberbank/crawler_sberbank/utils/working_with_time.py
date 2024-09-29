from datetime import datetime, timedelta

import pytz
from dateutil import parser
import re
import logging

logger = logging.getLogger(__name__)

moscow_time = datetime.now(pytz.timezone('Europe/Moscow'))
moscow_time_str = moscow_time.strftime('%Y-%m-%d %H:%M:%S')
###_TEXT_DATA_WRAGLING_###
def get_time_data(text, possition, url):
    try:
        if text:
            date_line = re.findall('\d{2}.\d{2}.\d{4}\s\d{1,2}:\d{2}', text)
            for dt in date_line:
                result = parser.parse(dt).strptime(dt, '%d.%m.%Y %H:%M')
                if result and dt == date_line[possition]:
                    return result.strftime('%Y-%m-%d %H:%M:%S')
    except:
        logger.error(f'{url}::INVALID DATE')
        return None


###_MANAGE_TIME_FOR_REQUESTS_PERIODS_###
def format_request_time_strftime(func):
    def wrapper(*args):
        t = func(*args)
        return t.strftime('%d.%m.%Y')

    return wrapper


def increase_time_days(time_from, days):
    time_delta = timedelta(days=days)
    time_from = datetime.strptime(time_from, '%d.%m.%Y %H:%S')
    time_to = time_from + time_delta
    return time_to.strftime('%d.%m.%Y %H:%S')


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

def return_moskow_time():
    return moscow_time_str