from .working_with_time import datetime
from .config import absolute_path_to_download, relative_path
from pathlib import Path
import re


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

    def return_relative_path(self):
        """ return relative path with date """
        return f'{relative_path}/{self.return_year_now()}/{self.return_month_now()}/'

    def create_dir(self):
        return Path(f'{absolute_path_to_download}/{self.return_year_now()}/{self.return_month_now()}').mkdir(
            parents=True, exist_ok=True)

    def return_absolute_path(self, name):
        return f'{absolute_path_to_download}/{self.return_year_now()}/{self.return_month_now()}/{name}'

    def return_root_dir(self):
        return f'{absolute_path_to_download}/{self.return_year_now()}/{self.return_month_now()}/'

    def replace_one_dot(self, name):
        """ replace one dot if before extansion is occured """
        dot = re.findall(r'\.', name)
        if len(dot) > 1:
            lenght = len(dot)
            output = re.sub(r'\.', '_', name, (lenght - 1))
            return output
        else:
            return name

    def name_file_on_server(self, _id, original_name):
        original_name = self.replace_one_dot(original_name)
        original_name = _id + '_~~_' + \
                        original_name.strip().replace('-', '_').replace(' ', '_').replace('(', '_').replace(')', '_')
        original_name = re.sub(r',$', '', original_name).strip()
        return f'{original_name}'

    def name_in_column_files(self, original_name):
        original_name = self.replace_one_dot(original_name)
        original_name = self.replace_one_dot(original_name)
        return f'{relative_path}/{self.return_year_now()}/{self.return_month_now()}/{original_name}'
