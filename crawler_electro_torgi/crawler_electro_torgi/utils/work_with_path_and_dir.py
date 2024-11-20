import re

from .working_with_time import datetime
from pathlib import Path


class GeneralFilesDir:
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

    def create_dir(self, path_absolute):
        return Path(f'{path_absolute}/{self.return_year_now()}/{self.return_month_now()}').mkdir(parents=True, exist_ok=True)

    def return_download_dir_etp(self, path_relative):
        return f'{path_relative}/{self.return_year_now()}/{self.return_month_now()}'

    def return_absolute_path(self, name, path_absolute):
        return f'{path_absolute}/{self.return_year_now()}/{self.return_month_now()}/{name}'

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

    def name_in_column_files(self, original_name, path_relative):
        return f'{path_relative}/{self.return_year_now()}/{self.return_month_now()}/{original_name}'

    def name_file_lot_on_server(self, _id, lot_num, original_name):
        original_name = self.replace_one_dot(original_name)
        original_name = _id + f'_~~_lot_{lot_num}_' + \
            original_name.strip().replace('-', '_').replace(' ', '_').replace('(', '_').replace(')', '_')
        return f'{original_name}'


class LotFilesDir(GeneralFilesDir):
    """class for manage lot files dir inheritance from GeneralFilesDir"""

    def name_in_column_files_lot(self, url, lot, original_name, path_relative):
        """ generate and return lot files name in db """
        original_name = url + '_lot_' + lot + '_~~_' + \
            original_name.strip().replace('-', '_').replace(' ', '_').replace('(', '_').replace(')', '_')
        return f'{path_relative}/{self.return_year_now()}/{self.return_month_now()}/{original_name}'

    def name_file_on_server_lot(self, url, lot, original_name):
        original_name = url + '_lot_' + lot + '_~~_' + \
            original_name.strip().replace('-', '_').replace(' ', '_').replace('(', '_').replace(')', '_')
        return f'{original_name}'
