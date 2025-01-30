from .working_with_time import datetime
from .config import absolute_path, relative_path
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

    def create_dir(self):
        return Path(f'{absolute_path}/{self.return_year_now()}/{self.return_month_now()}').mkdir(parents=True, exist_ok=True)

    def return_abs(self):
        return f'{absolute_path}/{self.return_year_now()}/{self.return_month_now()}'

    def return_absolute_path(self, name):
        return f'{absolute_path}/{self.return_year_now()}/{self.return_month_now()}/{name}'

    def name_file_on_server(self, _id, original_name):
        original_name = _id + '_~~_' + \
            original_name.strip().replace('-', '_').replace(' ', '_').replace('(', '_').replace(')', '_')
        return f'{original_name}'

    def name_in_column_files(self, original_name):
        return f'{relative_path}/{self.return_year_now()}/{self.return_month_now()}/{original_name}'

