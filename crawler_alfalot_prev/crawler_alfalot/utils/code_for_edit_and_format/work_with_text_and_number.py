import textwrap
import unicodedata

from chardet import detect


def dedent_func(string: str):
    if string:
        string = textwrap.dedent(string)
        wrapped = textwrap.fill(string, width=50)
        string = textwrap.indent(wrapped, '')
        return string.replace('\n', ' ').strip()
    else:
        return None


cyrillic = 'абвгдеёжзийклмнопрстуфхцчшщъыьэюяАБВГДЕЁЖЗИЙКЛМНОПРСТУФХЦЧШ ЩЪЫЬЭЮЯ'
mac_symbols = ('╨┐', '╨', 'MACOS', '╤')


def count_cyrillic(text):
    text_check = bytes(text, encoding="raw_unicode_escape")
    _encoding_type = detect(text_check)['encoding']
    if text.isascii():
        return text
    count = 0
    if len(text) > 12:
        minus = 4
    else:
        minus = 1
    stop = round(len(text) / 2 - minus)
    for i, ch in enumerate(text):
        if ch in cyrillic:
            count += 1
        if count == stop and i >= 1:
            return text
        elif i + 1 == len(text):
            try:
                if any(s in text for s in mac_symbols):
                    new_text = text.encode('CP437')
                    return new_text.decode('UTF-8')
                elif _encoding_type == 'ISO-8859-1':
                    new_text = text.encode('CP437', 'ignore')
                    new_text = new_text.decode('CP866')
                    new_text = new_text.encode('utf-8')
                    return new_text.decode('utf-8')
                else:
                    new_text = text.encode('CP437')
                    new_text = new_text.decode('CP866')
                    new_text = new_text.encode('utf-8')
                    return unicodedata.normalize('NFKC', new_text.decode('utf-8'))
            except:
                try:
                    new_text = text.encode('CP866')
                    new_text = new_text.decode('utf-8')
                    return unicodedata.normalize('NFKC', new_text)
                except:
                    return text