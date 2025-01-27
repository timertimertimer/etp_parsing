from .working_with_time import datetime
from .config import absolute_path_to_download, relative_path
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
        return Path(f'{absolute_path_to_download}/{self.return_year_now()}/{self.return_month_now()}').mkdir(
            parents=True, exist_ok=True)

    def return_absolute_path(self):
        return f'{absolute_path_to_download}/{self.return_year_now()}/{self.return_month_now()}/'

    def return_relative_path(self):
        """ return relative path with date """
        return f'{relative_path}/{self.return_year_now()}/{self.return_month_now()}/'

    def name_file_on_server(self, id_, original_name):
        original_name = id_ + '_~~_' + \
                        original_name.strip().replace('-', '_').replace(' ', '_').replace('(', '_').replace(')', '_')
        return f'{original_name}'

    def name_in_column_files(self, id_, original_name):
        original_name = id_ + '_~~_' + \
                        original_name.strip().replace('-', '_').replace(' ', '_').replace('(', '_').replace(')', '_')
        return f'{relative_path}/{self.return_year_now()}/{self.return_month_now()}/{original_name}'


class LotFilesDir(GeneralFilesDir):
    """class for manage lot files dir inheritance from GeneralFilesDir"""

    def name_in_column_files_lot(self, url_id, lot, original_name):
        """ generate and return lot files name in db """
        original_name = url_id + '_lot_' + lot + '_~~_' + \
                        original_name.strip().replace('-', '_').replace(' ', '_').replace('(', '_').replace(')', '_')
        return f'{relative_path}/{self.return_year_now()}/{self.return_month_now()}/{original_name}'

    def name_file_on_server_lot(self, url_id, lot, original_name):
        original_name = url_id + '_lot_' + lot + '_~~_' + \
                        original_name.strip().replace('-', '_').replace(' ', '_').replace('(', '_').replace(')', '_')
        return f'{original_name}'
