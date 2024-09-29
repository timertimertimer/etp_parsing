# -*- coding: utf-8 -*-
import re
from http.cookies import SimpleCookie


# Multi replace
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


# WORKING_WITH_COOKIES_SCRAPY_SPLASH
def cookie_parser(cookies_string):
    cookie_string = cookies_string
    cookie = SimpleCookie()
    cookie.load(cookie_string)
    cookies = {}
    for key, morsel in cookie.items():
        cookies[key] = morsel.value
    return cookies


# _END__WORKING_WITH_COOKIES_SCRAPY_SPLASH

def sort_trading_type(text):
    offer = ['Продажа посредством публичного предложения']
    auction = ['Аукцион с открытой формой подачи предложений',
               'Аукцион с закрытой формой подачи предложений']
    competition = ['Конкурс с открытой формой подачи предложений',
                   'Конкурс с закрытой формой подачи предложений']
    for t in offer:
        if t in text:
            return 'offer'
    for t in auction:
        if t in text:
            return 'auction'
    for t in competition:
        if t in text:
            return 'competition'
        else:
            return None


def get_trading_form(text):
    """get text and using regular expression get form
        :return open form. current web site does not have closed form
    """
    #text = ''.join(filter(lambda x: x.isalpha(), text))
    opened = ['Продажа посредством публичного предложения',
              'Аукцион с открытой формой подачи предложений',
              'Аукцион с закрытой формой подачи предложений',
              'Конкурс с открытой формой подачи предложений',
              'Конкурс с закрытой формой подачи предложений']
    closed = None
    for f in opened:
        if f in text:
            return 'open'
    return 'closed'
