from datetime import datetime
import re
import string
import textwrap
from pathlib import Path
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
###_REMOVE_EXTRA_SPACES(INDENTS)_###
def dedent_func(string: str):
    if string:
        string = textwrap.dedent(string)
        wrapped = textwrap.fill(string, width=50)
        string = textwrap.indent(wrapped, '')
        return string.replace('\n', ' ').strip()
    else:
        return None


###_BASIC_INFO_###
def get_links_to_trading():
    return LIST_OF_LINKS_TO_TRADING


def get_status(data):
    return status_loc.format(data)


def get_next_page():
    return pagination


def clean_next_page(next_page, url: str):
    match1 = re.findall(pattern_next_page, str(next_page))
    match2 = re.findall(r'\d+$', ''.join(match1))
    return url.format(''.join(match2))


def get_start_request():
    return start_date_request_loc


def trade_id(url):
    id = ''.join(re.findall(r'\d{4,}', str(url).strip()))
    return id


######_______TRADING_____ORGANIZATOR____########
def get_last_name():
    return last_name_org


def get_first_name():
    return first_name_org


def get_mid_name():
    return middle_name_org


def get_inn_org():
    return inn_org_loc


def get_if_company():
    return organization_name


def get_if_company_short():
    return organization_name_short


def get_email_org():
    return email_org_loc


def get_phone_org():
    return phone_org_loc


# check who is promoter of trade
def get_full_name_info(last, first, middle, url, company=None):
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
        if company and len(company) > 2:
            return str(company)
    except Exception as e:
        logger.warning(
            f'{url}---ERROR DURING HANDLING ORGANIZATOR INFO--\n{traceback.format_exc(e)}')


def check_inn(inn):
    try:
        if inn and len(inn) >= 10 and len(inn) <= 12:
            match = re.findall(r'^\w\d{9,12}$', inn)
            if match:
                return ''.join(inn)
        else:
            return None

    except BaseException:
        return ''


def check_email(email):
    try:
        if email and len(email) <= 50:
            if '@' in email:
                email = re.findall(
                    r'.+\S@\S.+\.\D{2,4}$', email, flags=re.IGNORECASE)
                return ''.join(email)
            else:
                return ''
    except BaseException:
        return ''


def check_phone(phone):
    try:
        if phone and len(phone) < 39 and len(phone) > 8:
            phone = replaceMultiple(phone, pattern_replace, '')
            match = re.search(r'\d{10,}', phone)
            if match:
                return '+' + phone
        else:
            return ''
    except BaseException:
        return ''


def check_case_number(value, url):
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
                return logger.warning(f'{url} case_number length less than 0')

    except:
        logger.warning(f'{url} HASN\'T CASE NUMBER OR DATA INVALID')


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
                return None

    except:
        value = 'INVALID'
        logger.error(f'{url} HASN\'T MESSAGE NUMBER OR DATA INVALID')
        return value


###########_____DEBITOR__________INFO#############
def get_debitor_inn():
    return debitor_inn


def get_msg_number():
    return msg_number


def get_case_number():
    return case_number_loc


###########__END___DEBITOR_______INFO#############

# _____ARBITR__________INFO########################_____ARBITR___
def get_arbitr_inn():
    return arb_man_inn


def get_arbitr_org():
    return arbit_manager_org_loc


###########__END___ARBITR_______INFO#############

###_WORKING_WITH_LOTS_###
def get_short_name(n):
    return short_name_loc.format(n)


def get_start_price(n):
    """:arg lot_number"""
    return start_price_loc.format(n)


def get_step_price(n):
    """:arg lot_number"""
    return step_price_loc.format(n)


def get_lot_number(title):
    if title:
        title = title.strip()
        match = re.findall(r'\d+$', title)
        return ''.join(match)
    else:
        return None


def get_period_data(n):
    return period_table_data.format(n)


###_WORKING_WITH_PERIODS_OFFER_###
def clean_periods(periods):
    new_periods = list()
    for p in periods:
        match = re.compile(pattern_periods, flags=re.IGNORECASE)
        if match and len(p) > 50:
            p = re.split('\s', p)
            p = list(filter(lambda x: x[0].isdigit(), p))
            new_periods.append(p)
    return new_periods


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


###_WORKING_WITH_DIRECTORIES_###
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
