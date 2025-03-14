import logging
import re
from datetime import datetime, timedelta
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


def parse_datetime(string: str, format: str) -> datetime:
    formats = [
        '%Y-%m-%dT%H:%M:%S.%fZ',  # с миллисекундами и Z
        '%Y-%m-%dT%H:%M:%S.%f',  # с миллисекундами без Z
        '%Y-%m-%dT%H:%M:%SZ',  # без миллисекунд с Z
        '%Y-%m-%dT%H:%M:%S',  # просто секундами без Z
    ]

    for date_format in formats:
        try:
            dt = datetime.strptime(string, date_format)
            return dt.replace(tzinfo=pytz.utc)
        except ValueError:
            continue
    if format:
        try:
            return datetime.strptime(string, format)
        except ValueError:
            pass
    raise ValueError(f"Не удалось распарсить дату: {string}")


@format_time_strftime
def return_parse_date(string: str = None, format: str = None) -> datetime:
    if string:
        utc_time = parse_datetime(string, format)
        return utc_time.astimezone(moscow_tz)
    return datetime.now(moscow_tz)


def return_servertime(format: str = '%H:%M:%S'):
    return datetime.now(moscow_tz).strftime(format)


def return_servertime_timestamp():
    return str(int(datetime.now(moscow_tz).timestamp()))


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


def increase_time_days(time_from, days):
    time_delta = timedelta(days=days)
    time_from = datetime.strptime(time_from, '%d.%m.%Y %H:%S')
    time_to = time_from + time_delta
    return time_to.strftime('%d.%m.%Y %H:%S')


if __name__ == '__main__':
    print(return_servertime_timestamp())
