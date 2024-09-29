import re
import functools
import textwrap
from http.cookies import SimpleCookie
import unicodedata
from chardet import detect


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
        return None


def return_normalize_text(string: str):
    new_str = unicodedata.normalize("NFKD", string)
    return new_str


def make_float(price):
    try:
        if price:
            price = ''.join(price).replace(',', '.')
            print('make float', price)
            price = ''.join(filter(lambda x: x.isdigit()
                                             or x == '.', price))
            price = ''.join(
                map(str, (re.findall(r'^\d+?\.\d{1,2}', str(price)))))
            price = round(float(price), 2)
            print('round price', price)
            return price
    except Exception as e:
        print(e)
        return e


def get_lot_number(func):
    @functools.wraps(func)
    def wrapped(*args, **kwargs):
        result = func(*args, **kwargs)
        pattern = re.compile(r'^Лот.?\W\s?\d{1,}\:?|^Лот.?\W\d{1,}\.?', flags=re.IGNORECASE)
        if result:
            match = pattern.findall(str(result))
        else:
            match = None
        if match:
            lot_number = ''.join(re.findall(r'\d+', ''.join(match)))
        else:
            return '1'
        if len(lot_number) < 5:
            return lot_number
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
