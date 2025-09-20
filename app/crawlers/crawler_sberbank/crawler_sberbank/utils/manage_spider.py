import re
from functools import reduce


# Method for manage default value in dictionary. If key is None any error will not view - just None
def deep_get_dict(dictionary, keys, default=None):
    return reduce(
        lambda d, key: d.get(key, default) if isinstance(d, dict) else default,
        keys.split("."),
        dictionary,
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


if __name__ == "__main__":
    print(sort_trading_type("Открытый аукцион"))  # auction
    print(sort_trading_type("Закрытый конкурс"))  # competition
    print(sort_trading_type("Открытое публичное предложение"))  # offer
    print(sort_trading_type("Запрос цен (коммерческих предложений)"))  # rfp
    print(sort_trading_type("Что-то другое")) 
