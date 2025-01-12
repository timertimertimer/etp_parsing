from .locator import *
from datetime import datetime
from http.cookies import SimpleCookie
import re
import string
from pathlib import Path
from .config import absolute_path_to_download, relative_path
import textwrap
import logging

logger = logging.getLogger(__name__)


# ##___WORKING_WITH_COOKIES_SCRAPY_SPLASH_###


def cookie_parser(cookies_string):
    cookie_string = cookies_string
    cookie = SimpleCookie()
    cookie.load(cookie_string)
    cookies = {}
    for key, morsel in cookie.items():
        cookies[key] = morsel.value
    return cookies


# ##_END__WORKING_WITH_COOKIES_SCRAPY_SPLASH_###


def dedent_func(string_: str):
    string_ = textwrap.dedent(string_)
    wrapped = textwrap.fill(string_, width=50)
    string_ = textwrap.indent(wrapped, '')
    return string_.replace('\n', ' ')


# #############__________Multiraplace__________#############
def replaceMultiple(mainString, toBeReplaces, newString):
    # Iterate over the sings to be replaced
    for elem in toBeReplaces:
        # Check if string is in the main string
        if elem in mainString:
            # Replace the string
            mainString = mainString.replace(elem, newString)

    return mainString


pattern_replace = ['(', ')', '-', '+', '- ', ' ', ]
pattern_replace1 = ['(', ')', '+', '- ', 'null', '\n', '&nbsp;']


# #############__________Multiraplace____END______###########

# ###############___________FORMAT_____TIME_______##############


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
            return datetime.strptime(date, '%d.%m.%Y %H:%M')
        else:
            return None
    except Exception as e:
        print(e)
        return None


year = str(datetime.now().year)
month = '{:0>2}'.format(str(datetime.now().month))
day = str(datetime.now().day)


def return_parse_date():
    return datetime.now().strftime('%Y-%m-%d %H:%M:%S')


def return_time_period(strtime):
    date = str(strtime).strip('\n, -').replace('- ', '').replace('&nbsp;', '')
    date = datetime.strptime(date, '%Y-%m-%d %H:%M:%S')
    return date.strftime('%Y-%m-%d %H:%M:%S')


# ##############__________END____FORMAT_____TIME################

# ###___WORK____WITH____TEXT____UNIVERSAL__#####
# _delete_new_line_symbols_#

# ##_WORKING_WITH_REQUEST_FORM_###


def get_from_data_start():
    return form_data_start


def get_start_date_request():
    return start_date_request_loc


def get_end_date_requests():
    return end_date_request_loc


def get_start_date_trading():
    return start_trading_loc


def get_end_date_trading():
    return end_trading_loc


def fetch_trading_links():
    return LINKS_to_TRADING_pages


# ##_INFO_TRADE_PAGE_###


def trade_type():
    return trade_type_loc


def trade_id(url):
    _id = ''.join(re.findall(r'\d+', str(url).strip()))
    return _id


# ##_org_info_###


def get_org_name():
    return org_name_loc


def get_org_inn():
    return inn_org


def get_org_email():
    return email_org_loc


def get_org_phone():
    return phone_org_loc


# ###_arbitr_info_###


def get_arbitr_name():
    return arbitr_name_loc


def get_arbitr_inn():
    return arbitr_inn_loc


def get_arbitr_org():
    return arbitr_org_loc


# ##_debitor_info_###


def get_debitor_inn():
    return debitor_inn

def get_address():
    return debitor_address


def get_case_number():
    return case_num_loc


def msg_number():
    return msg_num_loc


# ##_SET_DATES_REQUESTS/TRADING_###
# ##_CHECK_AND_FORMAT_INFO(_EMAIL_PHONE_INN_NAME)_CASE_NUMBER_MSG_NUMBER###


def check_email(email):
    try:
        if len(email) <= 50:
            if '@' in email:
                email = re.findall(
                    r'.+\S@\S.+\.\D{2,4}$', email, flags=re.IGNORECASE)
                return ''.join(email)
            else:
                return ''
    except Exception as e:
        print(e)
        return ''


def check_phone(phone):
    try:
        if 39 > len(phone) > 8:
            phone = replaceMultiple(phone, pattern_replace, '')
            match = re.search(r'\d{10,}', phone)
            if match:
                return '+' + phone
        else:
            return ''
    except Exception as e:
        print(e)
        return ''


def check_inn(inn):
    try:
        if inn:
            inn = inn.strip()
        if 10 <= len(inn) <= 12:
            match = re.findall(r'^\w\d{9,12}$', inn)
            if match:
                return ''.join(inn)
    except Exception as e:
        print(e)
        return ''


def check_name(string_: str):
    try:
        if string_ is not None and 3 < len(string_) < 256:
            return string_.strip()
        else:
            return None
    except Exception as e:
        print(e)
        return ''


def check_case_number(url, value):
    try:
        if value and len(value) < 32:
            pattern = r'\w.+\/\d{2,4}.*'
            value = value.replace('№', '').strip()
            match = re.findall(pattern, value)
            if type(match) == list and len(match) > 1:
                v = ''.join(match[0])
            else:
                v = ''.join(match)
            if len(v) > 0:
                return v.strip()
            else:
                return logger.error(f'{url} case_number length less than 0')

    except Exception as e:
        logger.error(f'{url} HASN\'T CASE NUMBER OR DATA INVALID {e}')


def check_msg_number(url, value: str):
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

    except Exception as e:
        value = 'INVALID'
        logger.error(f'{url} HASN\'T MESSAGE NUMBER OR DATA INVALID {e}')
        return value


# ##_END_CHECK_AND_FORMAT_INFO(_EMAIL_PHONE_INN_NAME)_###
# ##_working_with_table_periods_offer_###


def get_table_period():
    return table_period_1


def make_float(price):
    if price:
        printable = set(string.printable)
        price = ''.join(filter(lambda x: x in printable, price))
        price = price.strip().replace(" ", "").replace(',', '.')
        price = ''.join(
            map(str, (re.findall(r'^\d+\.\d{1,2}', str(price)))))
        return round(float(price), 2)


# ##_END_INFO_TRADE_PAGE_###


# ##_WORKING_WITH_DIRECTORIES_###
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
