import re

from .working_with_time import datetime
from .config import path_absolute, path_relative
from pathlib import Path


class GeneralFilesDir:
    def __init__(self, spider):
        self.path_absolute = path_absolute[spider]
        self.path_relative = path_relative[spider]

    def __repr__(self):
        return self

    def return_year_now(self):
        year = str(datetime.now().year).strip()
        return year

    def return_month_now(self):
        month = str('{:0>2}'.format(datetime.now().month)).strip()
        return month

    def return_day_now(self):
        day = str(datetime.now().day).strip()
        return day

    def create_dir(self):
        return Path(f'{self.path_absolute}/{self.return_year_now()}/{self.return_month_now()}').mkdir(parents=True,
                                                                                                      exist_ok=True)

    def return_download_dir_etp(self):
        return f'{self.path_relative}/{self.return_year_now()}/{self.return_month_now()}'

    def return_absolute_path(self, name):
        return f'{self.path_absolute}/{self.return_year_now()}/{self.return_month_now()}/{name}'

    def name_file_on_server(self, _id, original_name):
        original_name = self.replace_one_dot(original_name)
        original_name = _id + '_~~_' + \
                        original_name.strip().replace('-', '_').replace(' ', '_').replace('(', '_').replace(')', '_')
        return f'{original_name}'

    def replace_one_dot(self, name):
        """ replace one dot if before extansion is occured """
        dot = re.findall(r'\.', name)
        if len(dot) > 1:
            lenght = len(dot)
            output = re.sub(r'\.', '_', name, (lenght - 1))
            return output
        else:
            return name

    def name_in_column_files(self, original_name):
        return f'{self.path_relative}/{self.return_year_now()}/{self.return_month_now()}/{original_name}'

    def name_file_lot_on_server(self, _id, lot_num, original_name):
        original_name = self.replace_one_dot(original_name)
        original_name = _id + f'_~~_lot_{lot_num}_' + \
                        original_name.strip().replace('-', '_').replace(' ', '_').replace('(', '_').replace(')', '_')
        return f'{original_name}'


class LotFilesDir(GeneralFilesDir):
    """class for manage lot files dir inheritance from GeneralFilesDir"""

    def name_in_column_files_lot(self, url, lot, original_name):
        """ generate and return lot files name in db """
        original_name = url + '_lot_' + lot + '_~~_' + \
                        original_name.strip().replace('-', '_').replace(' ', '_').replace('(', '_').replace(')', '_')
        return f'{self.path_relative}/{self.return_year_now()}/{self.return_month_now()}/{original_name}'

    def name_file_on_server_lot(self, url, lot, original_name):
        original_name = url + '_lot_' + lot + '_~~_' + \
                        original_name.strip().replace('-', '_').replace(' ', '_').replace('(', '_').replace(')', '_')
        return f'{original_name}'
