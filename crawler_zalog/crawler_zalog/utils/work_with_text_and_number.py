import re
import textwrap
import unicodedata
from http.cookies import SimpleCookie

from chardet import detect


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
            if jsession == 'JSESSIONID':
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
        return None


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


def make_float(price):
    try:
        if len(price) > 0:
            price = re.sub(r'\s', '', price).replace(',', '.')
            price = re.sub(r'\.$', '', price).strip()
            price = ''.join(filter(lambda x: x.isdigit() or x == '.', price))
            if len(price) > 0:
                return round(float(price), 2)
    except Exception as e:
        print(e)
        return None

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