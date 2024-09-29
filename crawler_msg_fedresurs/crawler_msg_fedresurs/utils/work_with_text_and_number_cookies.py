import re
import functools
from http.cookies import SimpleCookie
import textwrap
from ..utils.config import asp, bankrot, fedresurs


def cookie_parser(cookies_string):
    cookie_string = cookies_string
    cookie = SimpleCookie()
    cookie.load(cookie_string)
    cookies = {}
    for key, morsel in cookie.items():
        cookies[key] = morsel.value
    return cookies

# Multi replace
def replaceMultiple(mainString, toBeReplaces, newString):
    # Iterate over the sings to be replaced
    for elem in toBeReplaces:
        # Check if string is in the main string
        if elem in mainString:
            # Replace the string
            mainString = mainString.replace(elem, newString)

    return mainString


pattern_replace = ['(', ')', '«', '»', '\'', '"', ',', '.']
new_string = ''
pattern_replace1 = []


def dedent_func(string: str):
    if string:
        string = textwrap.dedent(string)
        wrapped = textwrap.fill(string, width=50)
        string = textwrap.indent(wrapped, '')
        return string.replace('\n', ' ').strip()
    else:
        return None


def return_main_cookies(cookies: list) -> str:
    """get list with cookies and return just 2 or 3 type of cookies without Messages cookie"""
    value_asp = ''
    value_bankrot = ''
    value_fedresurs = ''
    for i in cookies:
        if isinstance(i, dict):
            for k, v in i.items():
                if isinstance(v, str):
                    v = ''.join(v).lower()
                    if v == asp:
                        value_asp = f"{i['name']}={i['value']};"
                    elif v == bankrot:
                        value_bankrot = f"{i['name']}={i['value']};"
                    elif v == fedresurs:
                        value_fedresurs = f"{i['name']}={i['value']};"
    return f'{value_asp} {value_bankrot} {value_fedresurs}'.strip()


def return_message_cookies(text, type_, date_from, date_to, page_number=0) -> str:
    """get text - type of message, date from period and date to period"""
    return f'MessageNumber=&MessageType={type_}&MessageTypeText={text}' \
           f'&DateEndValue={date_to}+0%3a00%3a00&DateBeginValue={date_from}+0%3a00%3a00' \
           f'&PageNumber={page_number}&DebtorText=&DebtorId=&DebtorType=&PublisherType=&PublisherId=' \
           f'&PublisherText=&IdRegion=&IdCourtDecisionType=&WithAu=False&WithViolation=False'


def return_complex_cookies(cookies: list, text, type_, date_from, date_to) -> str:
    """add all cookies to one string"""
    main_cookies = return_main_cookies(cookies)
    msg_cookies = return_message_cookies(text, type_, date_from, date_to)
    return f'{main_cookies} {msg_cookies}'
