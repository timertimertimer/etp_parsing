import string
import re
import functools
import textwrap


def dedent_func(string: str):
    if string:
        string = textwrap.dedent(string)
        wrapped = textwrap.fill(string, width=50)
        string = textwrap.indent(wrapped, '')
        return string.replace('\n', ' ').strip()
    else:
        return None

def get_price_period(text):
    match = ''.join(re.findall(r'\d{1,}\.\d{1,2}|$', text)[0])
    return round(float(''.join(match)), 2)


def get_price(text):
    lot_match = re.findall(r'Лот\s+?№\s?\d+\s', text)
    if lot_match:
        text = text.replace(''.join(lot_match), '')
    else:
        text = text
    text = ''.join(e for e in text.replace(',', '.') if e.isalnum() or e == '.')
    text = dedent_func(text)
    match = ''.join(re.findall(r'\d+\.\d{1,2}|$', text)[0])
    if match:
        return round(float(''.join(match)), 2)

def get_lot_num_simple(text):
    return ''.join(re.findall('\d+', text))

def get_lot_number(func):
    @functools.wraps(func)
    def wrapped(*args, **kwargs):
        result = func(*args, **kwargs)
        pattern = re.compile(r'^Лот.?\W\s?\d{1,}\:?|^Лот.?\W\d{1,}\.?', flags=re.IGNORECASE)
        if result:
            match = pattern.findall(str(result))
        else:
            match = None
        if match:
            lot_number = ''.join(re.findall(r'\d+', ''.join(match)))
        else:
            return '1'
        if len(lot_number) < 5:
            return lot_number
        else:
            return '1'

    return wrapped

def cut_lot_number(func):
    @functools.wraps(func)
    def wrapped(*args, **kwargs):
        result = func(*args, **kwargs)
        pattern = re.compile(r'^Лот.?\W\s?\d{1,}\:?|^Лот.?\W\d{1,}\.?', flags=re.IGNORECASE)
        if result:
            match = pattern.findall(str(result))
        else:
            match = None
        if match:
            return result.replace(''.join(match[0]), '', 1).strip().replace('"', '\'')
        else:
            return result.strip().replace('"', '\'')
    return wrapped


def delete_extra_symbols(func):
    @functools.wraps(func)
    def wrapped(*args, **kwargs):
        result = func(*args, **kwargs)
        if result:
            pattern = re.compile(r'^\:|^\.|^\-|^\(|^\,', flags=re.IGNORECASE)
            match = pattern.findall(str(result))
            if match:
                string_ = str(result).replace(''.join(match), '').strip().replace('"', '\'')
                return string_[0].upper()+string_[1:]
            else:
                string_ = str(result).strip().replace('"', '\'')
                return string_[0].upper()+string_[1:]

    return wrapped
