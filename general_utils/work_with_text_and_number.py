import re
import textwrap
import unicodedata
from http.cookies import SimpleCookie

from chardet import detect


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
            price = ''.join(filter(lambda x: x.isdigit()
                                             or x == '.', price))
            price = ''.join(
                map(str, (re.findall(r'^\d+?\.\d{1,2}', str(price)))))
            if price is None:
                price = ''.join(
                    map(str, (re.findall(r'^\d+?', str(price)))))
            price = round(float(price), 2)
            return price
    except Exception as e:
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


def parse_classifiers(string: str) -> tuple[list, list]:
    pattern = r'(\d{2,7})\.? (.*?)(?=(?:, \d{2,7}\.|$))'

    matches = re.findall(pattern, string)

    if matches:
        codes = [code for code, _ in matches]
        names = [name for _, name in matches]
    else:
        codes = []
        names = [el.strip() for el in string.split('.')]

    return codes, names


if __name__ == '__main__':
    print(parse_classifiers('0401 Имущественные права: Права долевой собственности'))
