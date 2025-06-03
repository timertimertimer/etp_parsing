import re
import functools
import logging
import string
import sys
from pathlib import Path, PurePath

import pandas as pd
import textwrap
import unicodedata
from http.cookies import SimpleCookie
from chardet import detect

from .time import datetime
from .config import lot_classifiers_code_to_name


def replace_one_dot(name):
    """ replace one dot if before extansion is occured """
    dot = re.findall(r'\.', name)
    if len(dot) > 1:
        lenght = len(dot)
        output = re.sub(r'\.', '_', name, (lenght - 1))
        return output
    else:
        return name


def clean_file_name(original_name):
    file_name = original_name.strip()
    file_name = replace_one_dot(file_name)
    replacements = {'-': '_', ' ': '_', '(': '_', ')': '_'}
    for key, value in replacements.items():
        file_name = file_name.replace(key, value)
    return file_name


def return_year_now():
    year = str(datetime.now().year).strip()
    return year


def return_month_now():
    month = str('{:0>2}'.format(datetime.now().month)).strip()
    return month


def return_day_now():
    day = str(datetime.now().day).strip()
    return day


def sanitize_filename(filename: str) -> str:
    try:
        sanitized = re.sub(r'[<>:"/\\|?*\x00-\x1F]', '_', filename)
    except Exception as e:
        raise e
    return sanitized


columns = ['Code', 'Name']
classifiers_df = pd.DataFrame(lot_classifiers_code_to_name.items(), columns=columns)
valid_codes = set(classifiers_df[columns[0]])
name_to_code = dict(zip(classifiers_df[columns[1]], classifiers_df[columns[0]].astype(str)))
logger = logging.getLogger(__name__)


def normalize_string(string_):
    return unicodedata.normalize("NFKD", string_)


def return_main_cookies(cookies: list) -> str:
    """ :arg cookies(list representation) with dictionary inside for itterate across dict for get cookie data """
    jsession = None
    _value = None
    for _ in cookies:
        if isinstance(_, dict):
            for k, v in _.items():
                if k == 'name':
                    jsession = v
                if k == 'value':
                    _value = v
    if jsession and _value:
        return f'{jsession}={_value}'


def cookie_parser(cookies_string):
    cookie_string = cookies_string
    cookie = SimpleCookie()
    cookie.load(cookie_string)
    cookies = {}
    for key, morsel in cookie.items():
        cookies[key] = morsel.value
    return cookies


def dedent_func(string: str):
    if string:
        string = textwrap.dedent(string)
        wrapped = textwrap.fill(string, width=50)
        string = textwrap.indent(wrapped, '')
        return string.replace('\n', ' ').strip()
    else:
        return


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


def check_case_number(case_number: str or None):
    if case_number:
        # find if 4 characters are inline together
        pattern = re.compile('\D{5,}')
        match = pattern.findall(case_number)
        if match and len(''.join(match)) > 0:
            match = ''.join(match)
            match1 = case_number.replace(match, '').strip()
        else:
            match1 = case_number
        return match1.replace('№', '').strip()


cyrillic = 'абвгдеёжзийклмнопрстуфхцчшщъыьэюяАБВГДЕЁЖЗИЙКЛМНОПРСТУФХЦЧШ ЩЪЫЬЭЮЯ'
mac_symbols = ('╨┐', '╨', 'MACOS', '╤')


def count_cyrillic(text):
    text_check = bytes(text, encoding="raw_unicode_escape")
    _encoding_type = detect(text_check)['encoding']
    if text.isascii():
        return text
    count = 0
    if len(text) > 12:
        minus = 4
    else:
        minus = 1
    stop = round(len(text) / 2 - minus)
    for i, ch in enumerate(text):
        if ch in cyrillic:
            count += 1
        if count == stop and i >= 1:
            return text
        elif i + 1 == len(text):
            try:
                if any(s in text for s in mac_symbols):
                    new_text = text.encode('CP437')
                    return new_text.decode('UTF-8')
                elif _encoding_type == 'ISO-8859-1':
                    new_text = text.encode('CP437', 'ignore')
                    new_text = new_text.decode('CP866')
                    new_text = new_text.encode('utf-8')
                    return new_text.decode('utf-8')
                else:
                    new_text = text.encode('CP437')
                    new_text = new_text.decode('CP866')
                    new_text = new_text.encode('utf-8')
                    return unicodedata.normalize('NFKC', new_text.decode('utf-8'))
            except:
                try:
                    new_text = text.encode('CP866')
                    new_text = new_text.decode('utf-8')
                    return unicodedata.normalize('NFKC', new_text)
                except:
                    return text


def make_float(price):
    try:
        if price:
            price = ''.join(price).replace(',', '.')
            price = ''.join(filter(lambda x: x.isdigit() or x == '.', price))
            price = ''.join(map(str, (re.findall(r'^\d+?\.\d{1,2}', str(price)))))
            if price is None:
                price = ''.join(map(str, (re.findall(r'^\d+?', str(price)))))
            price = round(float(price), 2)
            return price
    except Exception as e:
        logger.error(f'Cant convert {price} to float: {e}')
        return e


def contains(text: str):
    return lambda x: x and text in x


def fix_encoding(name):
    if re.search(r'[^\w\s\.\-/]', name):
        try:
            return name.encode("cp437").decode("cp866")
        except (UnicodeDecodeError, UnicodeEncodeError):
            return name
    return name


def parse_classifiers(category_str: str) -> list[str]:
    category_str = ' '.join(category_str.strip().split())
    possible_code_pattern = re.compile(r'\b\d{2,}\b')
    found_codes = set()
    extracted_codes = possible_code_pattern.findall(category_str)
    found_codes.update(code for code in extracted_codes if code in valid_codes)
    for name, code in name_to_code.items():
        if name.lower() in category_str.lower():
            found_codes.add(code)

    if not found_codes:
        pass
    return list(found_codes)


def get_lot_number(func):
    @functools.wraps(func)
    def wrapped(*args, **kwargs):
        result = func(*args, **kwargs)
        pattern = re.compile(r'^Лот.?\W\s?\d{1,}\:?|^Лот.?\W\d{1,}\.?', flags=re.IGNORECASE)
        result_without_spaces = re.sub(r'\s', '', str(result))
        if result:
            match = pattern.findall(str(result))
        else:
            match = None
        if match:
            lot_number = ''.join(re.findall(r'\d+', ''.join(match)))
            if len(lot_number) > 4:
                pattern = re.compile(r'Лот.?\W\s?\d{1,}\:?|Лот.?\W\d{1,}\.?', flags=re.IGNORECASE)
                match = pattern.findall(str(result))
                lot_number = ''.join(re.findall(r'\d+', min(match)))
            return lot_number
        else:
            pattern_2 = re.compile(r'лот№\d+', flags=re.IGNORECASE)
            match2 = pattern_2.findall(str(result_without_spaces))
            if match2:
                match2 = ''.join(re.findall(r'\d+', max(match2)))
                if len(match2) > 4:
                    match2 = ''.join(re.findall(r'\d+', min(match2)))
                return match2
            else:
                return '1'

    return wrapped


def cut_lot_number(func):
    @functools.wraps(func)
    def wrapped(*args, **kwargs):
        result = func(*args, **kwargs)
        pattern = re.compile(r'^Лот.?\W\s?\d{1,}\:?|^Лот.?\W\d{1,}\.?', flags=re.IGNORECASE)
        if result:
            match = pattern.findall(str(result))
        else:
            match = None
        if match:
            return result.replace(''.join(match[0]), '', 1).strip().replace('"', '\'')
        else:
            return result.strip().replace('"', '\'')

    return wrapped


def delete_extra_symbols(func):
    @functools.wraps(func)
    def wrapped(*args, **kwargs):
        result = func(*args, **kwargs)
        if result:
            pattern = re.compile(r'^\:|^\.|^\-|^\(|^\,', flags=re.IGNORECASE)
            match = pattern.findall(str(result))
            if match:
                string_ = str(result).replace(''.join(match), '').strip().replace('"', '\'')
                return string_[0].upper() + string_[1:]
            else:
                string_ = str(result).strip().replace('"', '\'')
                return string_[0].upper() + string_[1:]

    return wrapped


def get_org_info(last, first, middle):
    if last or first or middle:
        l = list()
        if last:
            l.append(last)
        if first:
            l.append(first)
        if middle:
            l.append(middle)

        return string.capwords(' '.join(l))


def set_logger(logger):
    logger.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(asctime)s [%(name)-12s] %(levelname)-8s %(message)s')
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    console_handler.setLevel(logging.DEBUG)
    logger.addHandler(console_handler)


if __name__ == '__main__':
    print(parse_classifiers('0401 Имущественные права: Права долевой собственности'))
