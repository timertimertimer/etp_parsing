import logging
import re
from datetime import datetime, timedelta
import time
import pytz

logger = logging.getLogger(__name__)
moscow_time = datetime.now(pytz.timezone('Europe/Moscow'))
moscow_time_str = moscow_time.strftime('%Y-%m-%d %H:%M:%S')


def return_timestamp_moscow():
    return int(moscow_time.timestamp() * 1000)


def format_time_strftime(func):
    def wrapper(*args):
        t = func(*args)
        if t:
            return t.strftime('%Y-%m-%d %H:%M:%S')

    return wrapper


@format_time_strftime
def format_time(strtime):
    pattern = re.compile('\d{1,2}\.\d{1,2}\.\d{2,4}.*?\d{1,2}\:\d{1,2}\:\d{1,2}')
    strtime = ''.join(pattern.findall(strtime))
    if strtime:
        date = strtime
        return datetime.strptime(date, '%d.%m.%Y %H:%M:%S')


@format_time_strftime
def format_time_auction(strtime):
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

def return_parse_date():
    return moscow_time_str


def return_servertime():
    return moscow_time.strftime('%H:%M:%S')

def return_servertime():
    return datetime.now().strftime('%H:%M:%S')


def what_time_bigger(time_string_1, time_string_2, url):
    date_var = time.strptime(time_string_1, '%d.%m.%Y %H:%M')
    date_var2 = time.strptime(time_string_2, '%d.%m.%Y %H:%M')
    if date_var > date_var2:
        return 1
    elif date_var2 > date_var:
        return 2
    else:
        logger.error(f'{url} :: ERROR WITH CHECK TIME WHAT IS BIGGER', exc_info=True)
    return date_var

