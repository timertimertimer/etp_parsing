from .working_with_time import datetime
from .config import absolute_path_to_download, relative_path
from pathlib import Path


class GeneralFilesDir:

    def __repr__(self):
        return self

    @staticmethod
    def return_year_now():
        year = str(datetime.now().year).strip()
        return year

    @staticmethod
    def return_month_now():
        month = str('{:0>2}'.format(datetime.now().month)).strip()
        return month

    @staticmethod
    def return_day_now():
        day = str(datetime.now().day).strip()
        return day

    def create_dir(self):
        return Path(f'{absolute_path_to_download}/{self.return_year_now()}/{self.return_month_now()}').mkdir(
            parents=True, exist_ok=True)

    def return_absolute_path(self):
        return f'{absolute_path_to_download}/{self.return_year_now()}/{self.return_month_now()}/'

    @staticmethod
    def just_file_name(original_name, extra=None):
        """:return name of file on server, begin from relative path"""
        if extra is None:
            extra = ''
        name = extra + '_' + original_name.strip(). \
            replace('-', '_'). \
            replace(' ', '_'). \
            replace('(', '_'). \
            replace(')', '_'). \
            replace('-', '_'). \
            replace('+', '_')
        return name

    def return_files_relative_path(self, name):
        if name:
            return f'{relative_path}/{self.return_year_now()}/{self.return_month_now()}/{name}'
