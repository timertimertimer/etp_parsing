import logging
import re
from datetime import datetime
import time
import pytz

logger = logging.getLogger(__name__)
moscow_tz = pytz.timezone("Europe/Moscow")


def format_time_strftime(func):
    def wrapper(*args):
        t = func(*args)
        if t:
            return t.strftime('%Y-%m-%d %H:%M:%S')

    return wrapper


@format_time_strftime
def format_time(strtime):
    pattern = re.compile('\d{1,2}\.\d{1,2}\.\d{2,4}(?:.*?\d{1,2}:\d{1,2})?')
    strtime = ''.join(pattern.findall(strtime))
    if strtime:
        date = strtime
        try:
            return datetime.strptime(date, '%d.%m.%Y %H:%M')
        except ValueError:
            return datetime.strptime(date, '%d.%m.%Y')


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


@format_time_strftime
def return_parse_date(string: str = None, date_format: str = '%Y-%m-%dT%H:%M:%SZ'):
    if string:
        utc_time = datetime.strptime(string, date_format).replace(tzinfo=pytz.utc)
        utc_time_at_moscow = utc_time.astimezone(moscow_tz)
        return utc_time_at_moscow
    return datetime.now(moscow_tz)


def return_servertime():
    return datetime.now(moscow_tz).strftime('%H:%M:%S')


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


if __name__ == '__main__':
    print(return_parse_date('2025-03-04T21:00:00Z', '%Y-%m-%dT%H:%M:%SZ'))
