import re

from .working_with_time import datetime
from pathlib import Path, PurePath


def replace_one_dot(name):
    """ replace one dot if before extansion is occured """
    dot = re.findall(r'\.', name)
    if len(dot) > 1:
        lenght = len(dot)
        output = re.sub(r'\.', '_', name, (lenght - 1))
        return output
    else:
        return name


def clean_file_name(original_name):
    file_name = original_name.strip()
    file_name = replace_one_dot(file_name)
    replacements = {'-': '_', ' ': '_', '(': '_', ')': '_'}
    for key, value in replacements.items():
        file_name = file_name.replace(key, value)
    return file_name


def return_year_now():
    year = str(datetime.now().year).strip()
    return year


def return_month_now():
    month = str('{:0>2}'.format(datetime.now().month)).strip()
    return month


def return_day_now():
    day = str(datetime.now().day).strip()
    return day


def sanitize_filename(filename: str) -> str:
    try:
        sanitized = re.sub(r'[<>:"/\\|?*\x00-\x1F]', '_', filename)
    except Exception as e:
        raise e
    return sanitized
