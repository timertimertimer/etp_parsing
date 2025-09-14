import math
import re
from functools import reduce, wraps
from http.cookies import SimpleCookie

from app.crawlers.crawler_sberbank.crawler_sberbank.utils.config import (
    pattern_lots_links,
)


# Method for manage default value in dictionary. If key is None any error will not view - just None
def deep_get_dict(dictionary, keys, default=None):
    return reduce(
        lambda d, key: d.get(key, default) if isinstance(d, dict) else default,
        keys.split("."),
        dictionary,
    )


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


pattern_replace = [
    "(",
    ")",
    "-",
    "+",
    "- ",
    " ",
]
pattern_replace1 = ["(", ")", "-", "+", "- ", "null", "\n", "&nbsp;"]


def find_link_to_lot(response_text):
    pattern = re.compile(pattern_lots_links)
    return pattern.findall(response_text)


def format_lua_script_pagination(lua_script, start_time, time_to, current_page):
    return (
        lua_script.replace("datefrom", start_time)
        .replace("dateto", time_to)
        .replace("page", str(current_page))
    )


def sort_trading_type(text: str) -> str | None:
    text_lower = text.lower()
    if re.search(r"запрос", text_lower):
        return "rfp"
    if re.search(r"аукцион", text_lower) or re.search(r"ценовой отбор", text_lower):
        return "auction"
    if re.search(r"конкурс", text_lower):
        return "competition"
    if re.search(r"предложени", text_lower):
        return "offer"
    return None


def get_trading_form(text: str) -> str | None:
    text_lower = text.lower()
    if re.search(r"открыт", text_lower):
        return "open"
    if re.search(r"закрыт", text_lower):
        return "closed"
    return None


def cut_lot_number(func):
    @wraps(func)
    def wrapped(*args, **kwargs):
        result = func(*args, **kwargs)
        pattern = re.compile(r"^Лот.?\W\s?\d+:?|^Лот.?\W\d+\.?", flags=re.IGNORECASE)
        if result:
            match = pattern.findall(str(result))
        else:
            match = None
        if match:
            return result.replace("".join(match[0]), "", 1).strip().replace('"', "'")
        else:
            return result.strip().replace('"', "'")

    return wrapped


@cut_lot_number
def return_itself(text):
    return text


if __name__ == "__main__":
    print(sort_trading_type("Открытый аукцион"))  # auction
    print(sort_trading_type("Закрытый конкурс"))  # competition
    print(sort_trading_type("Открытое публичное предложение"))  # offer
    print(sort_trading_type("Запрос цен (коммерческих предложений)")) # rfp
    print(sort_trading_type("Что-то другое")) 
