import re

from .working_with_time import datetime
from pathlib import Path


class GeneralFilesDir:

    def __init__(self, path_relative, path_absolute):
        self.path_relative = path_relative
        self.path_absolute = path_absolute

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

    @staticmethod
    def name_file_on_server(_id, original_name):
        original_name = _id + '_~~_' + \
                        original_name.strip().replace('-', '_').replace(' ', '_').replace('(', '_').replace(')', '_')
        return f'{original_name}'

    def name_in_column_files(self, name_on_server):
        return f'{self.path_relative}/{self.return_year_now()}/{self.return_month_now()}/{name_on_server}'

    def return_absolute_path(self, name):
        return f'{self.path_absolute}/{self.return_year_now()}/{self.return_month_now()}/{name}'
