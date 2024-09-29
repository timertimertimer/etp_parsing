import re
import functools
import textwrap
from .config import pattern_company_cut, pattern_name_cut
from http.cookies import SimpleCookie
from ..utils.config import bankrot, fedresurs, asp


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


def return_company_cut(company_: str):
    """cut extra words leave only company name"""
    cut_symbol = replaceMultiple(company_.lower(), pattern_replace, '')
    cut_words = replaceMultiple(cut_symbol, pattern_company_cut, '')
    return dedent_func(''.join(cut_words).lower())


def return_clean_name(fullname_: str):
    """cut extra words leave only person name"""
    if fullname_:
        fullname_ = fullname_.lower().strip()
        cut_ip = replaceMultiple(fullname_, pattern_name_cut, '')
        cut_ip = ''.join(re.sub(r'^ип\s', '', cut_ip, flags=re.IGNORECASE)).strip()
        return cut_ip.title().replace('.', ' ').strip()
    else:
        return ' '


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


def return_debtor_search_cookie(inn) -> str:
    """return cookies with inn"""
    return f' debtorsearch=typeofsearch=Organizations&orgname=&orgaddress=&orgregionid=&orgogrn=&orginn={inn}&orgokpo=&OrgCategory=&prslastname=&prsfirstname=&prsmiddlename=&prsaddress=&prsregionid=&prsinn=&prsogrn=&prssnils=&PrsCategory=&pagenumber=0'


def return_trade_cookies():
    """return default part of cookies"""
    return ' Trade=Region=&Status=&Type=&TradeObject=&TradeCode=&TradePlaceId=&DebtorText=&DebtorId=&DebtorType=&PropertyCategoriesText=&PropertyCategoriesValue=&PropertyCategoriesType=&ArmTOText=&ArmTOType=&ArmTOId=&PageNumber=0&DateEndValue=&DateBeginValue=;'


def return_debtor_search_cookie_person(inn) -> str:
    """return cookies with inn"""
    return f' debtorsearch=typeofsearch=Organizations&orgname=&orgaddress=&orgregionid=&orgogrn=&orginn=&orgokpo=&OrgCategory=&prslastname=&prsfirstname=&prsmiddlename=&prsaddress=&prsregionid=&prsinn={inn}&prsogrn=&prssnils=&PrsCategory=&pagenumber=0'


def return_complex_cookies(cookies: list, inn) -> str:
    """add all cookies to one string"""
    main_cookies = return_main_cookies(cookies)
    deb_search_cookies_org = return_debtor_search_cookie(inn)
    trade_cookies = return_trade_cookies()
    return f'{main_cookies}{deb_search_cookies_org}'


def return_complex_cookies_person(cookies: list, inn) -> str:
    """add all cookies to one string"""
    main_cookies = return_main_cookies(cookies)
    deb_search_cookies_person = return_debtor_search_cookie_person(inn)
    trade_cookies = return_trade_cookies()
    return f'{main_cookies}{deb_search_cookies_person}'
