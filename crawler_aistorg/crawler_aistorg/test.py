import re


def clean_names_members(value):
    if value:
        value = re.split(r'\s', value.strip())
        return ' '.join(map(lambda x: x, filter(lambda y: "@" not in y and y.isalpha(), value)))
    else:
        return 'Fuck'


strf = 'Старыстоянц Руслан Авдеевич prestig21@bk.ru 1LFSJLJ:JF:SJF:D'
