import logging
import re
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


# __FORMAT__TIME__
def format_time_strftime(func):
    def wrapper(*args):
        t = func(*args)
        if t:
            return t.strftime('%Y-%m-%d %H:%M:%S')

    return wrapper


@format_time_strftime
def format_time(strtime):
    pattern = re.compile(r'\d{1,2}\.\d{1,2}\.\d{2,4}.*?\d{1,2}:\d{1,2}')
    strtime = ''.join(pattern.findall(strtime))
    if strtime:
        date = strtime
        return datetime.strptime(date, '%d.%m.%Y %H:%M')


@format_time_strftime
def format_time_auction(strtime):
    pattern = re.compile(r'\d{1,2}\.\d{1,2}\.\d{2,4}.*?\d{1,2}:\d{1,2}')
    strtime = ''.join(pattern.findall(strtime))
    if strtime:
        date = strtime
        return datetime.strptime(date, '%d.%m.%Y %H:%M')


def return_parse_date():
    return datetime.now().strftime('%Y-%m-%d %H:%M:%S')
