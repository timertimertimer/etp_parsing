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


###___WORKING_WITH_COOKIES_SCRAPY_SPLASH_###
def cookie_parser(cookies_string):
    cookie_string = cookies_string
    cookie = SimpleCookie()
    cookie.load(cookie_string)
    cookies = {}
    for key, morsel in cookie.items():
        cookies[key] = morsel.value
    return cookies


###_END__WORKING_WITH_COOKIES_SCRAPY_SPLASH_###
def dedent_func(string: str):
    string = textwrap.dedent(string)
    wrapped = textwrap.fill(string, width=50)
    string = textwrap.indent(wrapped, '')
    return string.replace('\n', ' ')


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
pattern_replace1 = ['(', ')', '+', '- ', 'null', '\n', '&nbsp;']


##############__________Multiraplace____END______###########

################___________FORMAT_____TIME_______##############
def format_time_strftime(func):
    def wrapper(*args):
        t = func(*args)
        return t.strftime('%Y-%m-%d %H:%M:%S')

    return wrapper


@format_time_strftime
def format_time(strtime):
    pattern = re.compile(r'\d{1,2}\.\d{1,2}\.\d{2,4}.*?\d{1,2}\:\d{1,2}')
    strtime = ''.join(pattern.findall(strtime))
    if strtime:
        date = strtime
        return datetime.strptime(date, '%d.%m.%Y %H:%M')


@format_time_strftime
def format_time_period(strtime):
    try:
        if strtime:
            date = str(strtime).strip('\n, -').replace('- ', '').replace('&nbsp;', '')
            return datetime.strptime(date, '%d.%m.%Y %H:%M')
        else:
            return None
    except BaseException:
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


###############__________END____FORMAT_____TIME################

###_BASIC_INFO_###

def trade_id(url):
    id = ''.join(re.findall(r'\d+', str(url).strip()))
    return id


###_CHECK_AND_FORMAT_INFO(_EMAIL_PHONE_INN_NAME)_CASE_NUMBER_MSG_NUMBER###
def check_email(email):
    try:
        if len(email) <= 50:
            if '@' in email:
                email = re.findall(
                    r'.+\S@\S.+\.\D{2,4}$', email, flags=re.IGNORECASE)
                return ''.join(email)
            else:
                return ''
    except:
        return ''


def check_phone(phone):
    try:
        if len(phone) < 39 and len(phone) > 8:
            phone = replaceMultiple(phone, pattern_replace, '')
            match = re.search(r'\d{10,}', phone)
            if match:
                return '+' + phone
        else:
            return ''
    except:
        return ''


def check_inn(inn):
    try:
        if inn:
            inn = inn.strip()
        if len(inn) >= 10 and len(inn) <= 12:
            match = re.findall(r'^\w\d{9,12}$', inn)
            if match:
                return ''.join(inn)

    except:
        return ''


def check_name(string: str):
    try:
        if string is not None and len(string) > 3 and len(string) < 256:
            return string.strip()
        else:
            return None
    except:
        return None


def check_case_number(case_number, url):
    try:
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
        logger.warning(f'{url} HASN\'T CASE NUMBER OR DATA INVALID')


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

    except:
        value = 'INVALID'
        logger.error(f'{url} HASN\'T MESSAGE NUMBER OR DATA INVALID')
        return value


###_END_CHECK_AND_FORMAT_INFO(_EMAIL_PHONE_INN_NAME)_###
###_get_arbitr_name_###
def get_org_info(last, first, middle, url):
    try:
        if last or first or middle:
            l = list()
            if last:
                l.append(last)
            if first:
                l.append(first)
            if middle:
                l.append(middle)

            return string.capwords(' '.join(l))
    except:
        logger.error(f'{url} WITHOUT ARBITR NAME')


###_WORKING_WITH_LOTS_###
def get_amount_lots():
    return amount_lots_loc


def get_lot_number(num):
    return lot_number_loc.format(num)


def clean_lot_number(lot_num: str):
    try:
        if lot_num:
            lot_num = re.findall(r'^Лот . \d{1,4}:', str(lot_num))
            number = ''.join(
                map(str, (re.findall(r'\d{1,6}', str(lot_num)))))
            return number
    except Exception:
        logger.error('ERROREROOR___LOT_NUMBER')


def get_short_name(num):
    return short_name_loc.format(num)


def get_lot_info(num):
    return lot_info_loc.format(num)


def get_property_info(num):
    return property_informationloc.format(num)


def get_status(num):
    return status_loc.format(num)


def get_start_price(num):
    return start_price_loc.format(num)


def get_step_price(num):
    return step_price_loc.format(num)


def make_float(price):
    if price:
        printable = set(string.printable)
        price = ''.join(filter(lambda x: x in printable, price))
        price = price.strip().replace(" ", "").replace(',', '.')
        price = ''.join(
            map(str, (re.findall(r'^\d+\.\d{1,2}', str(price)))))
        return round(float(price), 2)


# _offer_date_#
def get_start_request_offer(number):
    return start_date_request_offer_loc.format(number)


def get_end_request_offer(number):
    return end_date_requests_offer_loc.format(number)


# _periods_table_#
def get_table_periods(num):
    return table_period_loc.format(num)


###_WORKING_WITH_FILES_###
def get_general_files():
    return files_generel_loc


def get_lot_files(lot_number):
    return lot_files_loc.format(lot_number)


###_WORKING_WITH_DIRECTORIES_###
def create_dir():
    return Path(f'{absolute_path_to_download}/{year}/{month}').mkdir(parents=True, exist_ok=True)


def return_absolute_path():
    return f'{absolute_path_to_download}/{year}/{month}'


def name_file_on_server(url, original_name):
    original_name = trade_id(url) + '~~' + \
                    original_name.strip().replace(' ', '_').replace('(', '_').replace(')', '_')
    return f'{original_name}'


def name_file_on_server_lot(url, original_name, n):
    original_name = trade_id(url) + '_lot_' + str(n) + '_' + \
                    original_name.strip().replace(' ', '_').replace('(', '_').replace(')', '_')
    return f'{original_name}'


def name_in_column_files(url, original_name):
    original_name = trade_id(url) + '~~' + \
                    original_name.strip().replace(' ', '_').replace('(', '_').replace(')', '_')
    return f'{relative_path}/{year}/{month}/{original_name}'


def name_in_column_files_lot(url, original_name, n):
    original_name = trade_id(url) + '_lot_' + str(n) + '_' + \
                    original_name.strip().replace(' ', '_').replace('(', '_').replace(')', '_')
    return f'{relative_path}/{year}/{month}/{original_name}'
