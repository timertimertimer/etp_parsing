import re
import textwrap
import unicodedata


def normalize_string(string_):
    return unicodedata.normalize("NFKD", string_)


def dedent_func(string: str):
    if string:
        string = textwrap.dedent(string)
        wrapped = textwrap.fill(string, width=50)
        string = textwrap.indent(wrapped, '')
        return string.replace('\n', ' ').strip()
    else:
        return None


def make_float(price):
    try:
        if price:
            price = ''.join(price).replace(',', '.')
            print('make float', price)
            price = ''.join(filter(lambda x: x.isdigit()
                                             or x == '.', price))
            price = ''.join(
                map(str, (re.findall(r'^\d+?\.\d{1,2}', str(price)))))
            price = round(float(price), 2)
            print('round price', price)
            return price
    except Exception as e:
        print(e)
        return e
