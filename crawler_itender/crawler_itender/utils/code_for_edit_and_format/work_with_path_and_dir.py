from .working_with_time import datetime

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

    def create_dir(self, _path_absolute):
        return Path(f'{_path_absolute}/{self.return_year_now()}/{self.return_month_now()}').mkdir(parents=True,
                                                                                                  exist_ok=True)

    def return_absolute_path(self, name, _path_absolute):
        return f'{_path_absolute}/{self.return_year_now()}/{self.return_month_now()}/{name}'

    def return_rel_path(self, _path_absolute):
        return f'{_path_absolute}/{self.return_year_now()}/{self.return_month_now()}/'

    @staticmethod
    def name_file_on_server(_id, original_name):
        original_name = _id + '_~~_' + \
                        original_name.strip().replace('-', '_').replace(' ', '_').replace('(', '_').replace(')', '_')
        return f'{original_name}'

    # @staticmethod
    # def lot_name_file_on_server(_id, original_name, lot_number):
    #     original_name = _id + f'_~~_lot_{lot_number}' + \
    #                     original_name.strip().replace('-', '_').replace(' ', '_').replace('(', '_').replace(')', '_')
    #     return f'{original_name}'

    @staticmethod
    def name_file_on_server_lot(_id, lot_num, original_name):
        original_name = _id + '_~~_' + lot_num + '_' + \
                        original_name.strip().replace('-', '_').replace(' ', '_').replace('(', '_').replace(')', '_')
        return f'{original_name}'

    def name_in_column_files(self, name, _path_rel):
        return f'{_path_rel}/{self.return_year_now()}/{self.return_month_now()}/{name}'



#
#
# class GeneralFilesDir:
#
#     def __repr__(self):
#         return self
#
#     @staticmethod
#     def return_year_now():
#         year = str(datetime.now().year).strip()
#         return year
#
#     @staticmethod
#     def return_month_now():
#         month = str('{:0>2}'.format(datetime.now().month)).strip()
#         return month
#
#     @staticmethod
#     def return_day_now():
#         day = str(datetime.now().day).strip()
#         return day
#
#     def create_dir(self, _path_absolute):
#         return Path(f'{_path_absolute}/{self.return_year_now()}/{self.return_month_now()}').mkdir(parents=True,
#                                                                                                   exist_ok=True)
#
#     def return_absolute_path(self, name, _path_absolute):
#         return f'{_path_absolute}/{self.return_year_now()}/{self.return_month_now()}/{name}'
#
#     @staticmethod
#     def name_file_on_server(_id, original_name):
#         original_name = _id + '_~~_' + \
#                         original_name.strip().replace('-', '_').replace(' ', '_').replace('(', '_').replace(')', '_')
#         return f'{original_name}'
#
#     @staticmethod
#     def name_file_on_server_lot(_id, lot_num, original_name):
#         original_name = _id + '_~~_' + lot_num + '_' + \
#                         original_name.strip().replace('-', '_').replace(' ', '_').replace('(', '_').replace(')', '_')
#         return f'{original_name}'
#
#     def name_in_column_files(self, original_name, _path_rel):
#         return f'{_path_rel}/{self.return_year_now()}/{self.return_month_now()}/{original_name}'
