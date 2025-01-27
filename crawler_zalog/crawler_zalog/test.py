import os
import re
import textwrap


def dedent_func(string: str):
    if string:
        string = textwrap.dedent(string)
        wrapped = textwrap.fill(string, width=50)
        string = textwrap.indent(wrapped, '')
        return string.replace('\n', ' ').strip()
    else:
        return None
tup = ('Описание обременения: Договор залога от 31.05.2013   Вид ограничения: Запрет '
       'регистрационных действий  Дата наложения обременения:                       '
       '31/05/2013  В пользу кого установлено ограничение: АО "Россельхозбанк"')
div = re.sub(r':\s{2,}', ': ', tup)
div_text = re.sub(r'\s{2,}', os.linesep, div)
print((div_text))
