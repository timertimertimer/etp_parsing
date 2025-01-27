from datetime import datetime
import re
import string
import textwrap
from pathlib import Path
from http.cookies import SimpleCookie
from .locator import *
from .config import pattern_next_page, pattern_periods, absolute_path_to_download, relative_path
import logging
import traceback

logger = logging.getLogger(__name__)


##############__________Multiraplace__________#############
def replaceMultiple(mainString, toBeReplaces, newString):
    # Iterate over the sings to be replaced
    for elem in toBeReplaces:
        # Check if string is in the main string
        if elem in mainString:
            # Replace the string
            mainString = mainString.replace(elem, newString)

    return mainString


pattern_replace = ['(', ')', '-', '+', '- ', ' ', ]
pattern_replace1 = ['(', ')', '-', '+', '- ', 'null', '\n', '&nbsp;']


##############__________Multiraplace____END______###########

################___________FORMAT_____TIME_______##############
def format_time_strftime(func):
    def wrapper(*args):
        t = func(*args)
        return t.strftime('%Y-%m-%d %H:%M:%S')

    return wrapper


@format_time_strftime
def format_time(strtime):
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
    except BaseException:
        return None


year = str(datetime.now().year)
month = '{:0>2}'.format(str(datetime.now().month))
day = str(datetime.now().day)


def return_parse_date():
    return datetime.now().strftime('%Y-%m-%d %H:%M:%S')


###############__________END____FORMAT_____TIME################
###___WORKING_WITH_COOKIES_SCRAPY_SPLASH_###
def cookie_parser(cookies_string):
    cookie_string = cookies_string
    cookie = SimpleCookie()
    cookie.load(cookie_string)
    cookies = {}
    for key, morsel in cookie.items():
        cookies[key] = morsel.value
    return cookies
###_REMOVE_EXTRA_SPACES(INDENTS)_###


def dedent_func(_string: str):
    if _string:
        _string = textwrap.dedent(_string)
        wrapped = textwrap.fill(_string, width=50)
        _string = textwrap.indent(wrapped, '')
        return _string.replace('\n', ' ').strip()
    else:
        return None
###_MAKE_PRINTABLE_###


def replace_html(value: str):
    try:
        if value:
            if "&amp;" in value:
                value = value.replace("&amp;", "&")
            return value
    except:
        return None

###_BASIC_INFO_###


def get_links_to_trading():
    return TABLE_LIST_OF_LINKS_TO_TRADE


def trade_id(url):
    id = ''.join(re.findall(r'\d+', str(url).strip()))
    return id


def get_lot_id(url):
    _id = ''.join(re.findall(r'lot_id=\d+$', str(url).strip()))
    _id = ''.join(re.findall(r'\d+', str(_id).strip()))
    if _id:
        return _id
    else:
        return None


def clean_names_members(value, url):
    if value:
        value = re.split(r'\s', value.strip())
        return ' '.join(map(lambda x: x, filter(lambda y: "@" not in y and y.isalpha(), value)))
    else:
        logger.warning(f'{url}::WITHOUT ORGANIZATOR NAME ')


def check_inn(inn, url):
    try:
        if inn and len(inn) >= 10 and len(inn) <= 12:
            match = re.findall(r'^\w\d{9,12}$', inn)
            if match:
                return ''.join(inn)
        else:
            return None

    except Exception:
        logger.warning(f'{url}:: INVALID DATA INN')


def check_email(email, url):
    try:
        if email and len(email) <= 50:
            if '@' in email:
                email = re.findall(
                    r'.+\S@\S.+\.\D{2,4}$', email, flags=re.IGNORECASE)
                return ''.join(email)
            else:
                return ''
    except Exception:
        logger.warning(f'{url}:: INVALID DATA EMAIL')


def check_phone(phone, url):
    try:
        if phone and len(phone) < 39 and len(phone) > 8:
            phone = replaceMultiple(phone, pattern_replace, '')
            match = re.search(r'\d{10,}', phone)
            if match:
                return '+' + phone
        else:
            return ''
    except Exception:
        logger.warning(f'{url}:: INVALID DATA PHONE')


def check_case_number(case_number, url):
    try:
        case_number = dedent_func(case_number.strip())
        if case_number:
            # find if 4 characters are inline together
            if 'от' in case_number:
                case_number = ''.join(str(case_number).split('от')[0])
            pattern = re.compile(r'\D{5,}')
            match = pattern.findall(case_number)
            if match and len(''.join(match)) > 0:
                match = ''.join(match)
                match1 = case_number.replace(match, '').strip()
            else:
                match1 = case_number
            return match1.replace('№', '').strip()

    except:
        logger.warning(f'{url} HASN\'T CASE NUMBER OR DATA INVALID 1')


def check_extra_case_number(value, url):
    match = re.findall(r'А\d+.+\/\d{2,4}', value)
    if match and len(match) < 16:
        return match
    else:
        logger.warning(f'{url} HASN\'T CASE NUMBER OR DATA INVALID 2')
        return None


def check_lot_number(value, url):
    if value:
        lot_number = ''.join(filter(lambda x: x.isdigit(), value))
        if lot_number:
            return lot_number
        else:
            logger.warning(f'{url}:; LOT WITHOUT LOT NUMBER')


def check_msg_number(value, url):
    try:
        if value:
            pattern = r'^\d+$'
            match = re.findall(pattern, value.strip())
            if type(match) == list and len(match) > 1:
                v = ''.join(match[0])
            else:
                v = ''.join(match)
            if len(v) > 0:
                return v.strip()
            else:
                return logger.error(f'{url} MESSAGE NUMBER length less than 0')

    except:
        value = 'INVALID'
        logger.error(f'{url} HASN\'T MESSAGE NUMBER OR DATA INVALID')
        return value


###_WORKING_WITH_PRICE_CONVERT_TO_FLOAT_###
def make_float(price):
    try:
        if price:
            printable = set(string.printable)
            price = ''.join(filter(lambda x: x in printable, price))
            price = price.strip().replace(" ", "").replace(',', '.')
            price = ''.join(
                map(str, (re.findall(r'^\d+\.\d{1,2}', str(price)))))
            return round(float(price), 2)
    except:
        return None


def create_dir():
    return Path(f'{absolute_path_to_download}/{year}/{month}').mkdir(parents=True, exist_ok=True)


def return_absolute_path():
    return f'{absolute_path_to_download}/{year}/{month}'


def name_file_on_server(url, original_name):
    original_name = trade_id(url) + '~~' + \
        original_name.strip().replace(' ', '_').replace('(', '_').replace(')', '_')
    return f'{original_name}'


def name_in_column_files(url, original_name):
    original_name = trade_id(url) + '~~' + \
        original_name.strip().replace(' ', '_').replace('(', '_').replace(')', '_')
    return f'{relative_path}/{year}/{month}/{original_name}'


def name_file_on_server_lot(url, original_name, n):
    original_name = get_lot_id(url) + '_lot_' + str(n) + '_' + \
        original_name.strip().replace(' ', '_').replace('(', '_').replace(')', '_')
    return f'{original_name}'


def name_in_column_files_lot(url, original_name, n):
    original_name = get_lot_id(url) + '_lot_' + str(n) + '_' + \
        original_name.strip().replace(' ', '_').replace('(', '_').replace(')', '_')
    return f'{relative_path}/{year}/{month}/{original_name}'
