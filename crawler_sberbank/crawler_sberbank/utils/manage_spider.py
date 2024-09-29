import re
from functools import reduce, wraps
from http.cookies import SimpleCookie

from .config import pattern_lots_links


# Method for manage default value in dictionary. If key is None any error will not view - just None
def deep_get_dict(dictionary, keys, default=None):
    return reduce(lambda d, key: d.get(key, default) if isinstance(d, dict) else default, keys.split("."), dictionary)


def cookie_parser(cookies_string):
    cookie_string = cookies_string
    cookie = SimpleCookie()
    cookie.load(cookie_string)
    cookies = {}
    for key, morsel in cookie.items():
        cookies[key] = morsel.value
    return cookies


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
pattern_replace1 = ['(', ')', '-', '+', '- ', 'null', '\n', '&nbsp;']


def find_link_to_lot(response_text):
    pattern = re.compile(pattern_lots_links)
    return pattern.findall(response_text)


def format_lua_script_pagination(lua_script, start_time, time_to, current_page):
    return lua_script.replace('datefrom',
                              start_time).replace('dateto', time_to).replace('page', str(current_page))


def sort_trading_type(text):
    offer = ['Открытое публичное предложение',
             'Закрытое публичное предложение']
    auction = ['Открытый аукцион',
               'Закрытый аукцион']
    competition = ['Открытый конкурс',
                   'Закрытый конкурс']
    try:
        text = ''.join(re.split(r'/', text.replace('\\', '/'))[0]).strip()
    except Exception as e:
        print(e)
        return None
    match1 = ''.join(filter(lambda x: re.findall(text, x, flags=re.IGNORECASE), auction))
    match2 = ''.join(filter(lambda x: re.findall(text, x, flags=re.IGNORECASE), offer))
    match3 = ''.join(filter(lambda x: re.findall(text, x, flags=re.IGNORECASE), competition))
    if match1:
        return 'auction'
    if match2:
        return 'offer'
    if match3:
        return 'competition'


def get_trading_form(text):
    """get text from trading page - section trading form an type
        :return open or close form
    """
    opened = ['Открытое публичное предложение',
              'Открытый аукцион',
              'Открытый конкурс',
              'Открытая']
    closed = ['Закрытое публичное предложение',
              'Закрытый аукцион',
              'Закрытый конкурс',
              'Закрытая']
    try:
        text = ''.join(re.split(r'/', text.replace('\\', '/'))[0]).strip()
        if '(' in text:
            text = ''.join(re.split(r'\(', text)[0]).strip()
    except Exception as e:
        print(e)
        return None
    match1 = ''.join(filter(lambda x: re.findall(text, x, flags=re.IGNORECASE), opened))
    match2 = ''.join(filter(lambda x: re.findall(text, x, flags=re.IGNORECASE), closed))
    if match1:
        return 'open'
    if match2:
        return 'closed'


# cut lot number

def cut_lot_number(func):
    @wraps(func)
    def wrapped(*args, **kwargs):
        result = func(*args, **kwargs)
        pattern = re.compile(r'^Лот.?\W\s?\d+:?|^Лот.?\W\d+\.?', flags=re.IGNORECASE)
        if result:
            match = pattern.findall(str(result))
        else:
            match = None
        if match:
            return result.replace(''.join(match[0]), '', 1).strip().replace('"', '\'')
        else:
            return result.strip().replace('"', '\'')

    return wrapped


@cut_lot_number
def return_itself(text):
    return text
