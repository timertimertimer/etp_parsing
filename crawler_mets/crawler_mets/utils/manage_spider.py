# -*- coding: utf-8 -*-
import re
from http.cookies import SimpleCookie
from ..utils.config import pattern_trade_links


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
def find_link_to_lot(link):
    pattern = re.compile(pattern_trade_links)
    match = pattern.findall(link)
    if match:
        return link


def sort_trading_type(text):
    text = ''.join(filter(lambda x: x.isalpha(), text))
    offer = ['ОТПП',
             'ЗТПП',
             'ОКПП',
             'ЗКПП']
    auction = ['ОАОФ',
               'ОАЗФ',
               'ЗАОФ',
               'ЗАЗФ']
    competition = ['ОКОФ',
                   'ОКЗФ',
                   'ЗКОФ',
                   'ЗКЗФ']
    match1 = ''.join(filter(lambda x: re.findall(
        text, x, flags=re.IGNORECASE), auction))
    match2 = ''.join(filter(lambda x: re.findall(
        text, x, flags=re.IGNORECASE), offer))
    match3 = ''.join(filter(lambda x: re.findall(
        text, x, flags=re.IGNORECASE), competition))
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
    text = ''.join(filter(lambda x: x.isalpha(), text))
    opened = ['ОТПП',
              'ОКПП',
              'ОАОФ',
              'ОАЗФ',
              'ОКОФ',
              'ОКЗФ']
    closed = ['ЗТПП',
              'ЗКПП',
              'ЗАОФ',
              'ЗАЗФ',
              'ЗКОФ',
              'ЗКЗФ']
    match1 = ''.join(filter(lambda x: re.findall(
        text, x, flags=re.IGNORECASE), opened))
    match2 = ''.join(filter(lambda x: re.findall(
        text, x, flags=re.IGNORECASE), closed))
    if match1:
        return 'open'
    if match2:
        return 'closed'
