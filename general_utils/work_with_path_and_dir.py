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


class FilesDir:

    def __init__(self, path_relative, path_absolute):
        self.path_relative = path_relative
        self.path_absolute = path_absolute

    def __repr__(self):
        return self

    def create_dir(self):
        return Path(f'{self.path_absolute}/{return_year_now()}/{return_month_now()}').mkdir(parents=True, exist_ok=True)

    def return_download_dir_etp(self):
        return PurePath(f'{self.path_relative}/{return_year_now()}/{return_month_now()}')

    def return_root_dir(self):
        return PurePath(f'{self.path_absolute}/{return_year_now()}/{return_month_now()}/')

    def return_absolute_path(self, name):
        return self.return_root_dir() / name

    def return_relative_path(self, name):
        """ return relative path with date """
        return self.return_download_dir_etp() / name

    @staticmethod
    def name_file_on_server(trading_id: str, original_name: str, lot_number: str = None):
        return f'{trading_id}_~~_{f"lot_{lot_number}_" if lot_number else ""}{clean_file_name(original_name)}'

    @staticmethod
    def name_file_lot_on_server(trading_id, lot_number, original_name):
        return f'{trading_id}_~~_lot_{lot_number}_{clean_file_name(original_name)}'
