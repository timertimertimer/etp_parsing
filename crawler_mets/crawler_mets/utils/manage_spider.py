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
    d = dict(
        offer=[
            'Открытые торги посредством публичного предложения',
            'Закрытые торги посредством публичного предложения',
            'Открытые торги (конкурс) посредством публичного предложения',
            'Открытые торги (конкурс) посредством публичного предложения'
        ],
        auction=[
            'Открытый аукцион с открытой формой представления предложений о цене',
            'Открытый аукцион с закрытой формой представления предложений о цене',
            'Закрытый аукцион с открытой формой представления предложений о цене',
            'Закрытый аукцион с закрытой формой представления предложений о цене'
        ],
        competition=[
            'ОКОФ',
            'ОКЗФ',
            'ЗКОФ',
            'ЗКЗФ'
        ]
    )
    for k, v in d.items():
        if text in v:
            return k


def get_trading_form(text):
    """get text from trading page - section trading form an type
        :return open or close form
    """
    d = dict(
        opened=[
            'Открытые торги посредством публичного предложения',
            'Открытые торги (конкурс) посредством публичного предложения',
            'Открытый аукцион с открытой формой представления предложений о цене',
            'Открытый аукцион с закрытой формой представления предложений о цене',
            'ОКОФ',
            'ОКЗФ'
        ],
        closed=[
            'Закрытые торги посредством публичного предложения',
            'Закрытые торги (конкурс) посредством публичного предложения',
            'Закрытый аукцион с открытой формой представления предложений о цене',
            'Закрытый аукцион с закрытой формой представления предложений о цене'
            'ЗКОФ',
            'ЗКЗФ'
        ]
    )
    for k, v in d.items():
        if text in v:
            return k
