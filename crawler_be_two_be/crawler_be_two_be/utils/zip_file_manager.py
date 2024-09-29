import pathlib
import re
import shutil
from zipfile import ZipFile
from crawler_be_two_be.utils.config import lst_exet_files
import os
import logging

from crawler_be_two_be.utils.work_with_text_and_number import count_cyrillic

logger = logging.getLogger(__name__)

# _path = f'/home/admin/web/78.24.219.218/public_html/downloads/etp_trade_place_vetp/2021/01/102043719_~~_lot_1_0_Электростанция.zip'
# p = '/home/admin/web/78.24.219.218/public_html/downloads/etp_trade_place_vetp/2021/01/'


class ZipFiles:

    def __init__(self, _path, _root_dir, _file_name, _id, lot_number, url, rel_path):
        self.abs_path = _path
        self.root_dir = _root_dir
        self._file_name = _file_name
        self._id = _id
        self.lot_number = lot_number
        self.url = url
        self.rel_path = rel_path + '/'
        self.zip = ZipFile(self.abs_path, 'r')

    def show_files_in_dir(self) -> list:
        """ return list with file's name """
        listOfFileNames = self.zip.namelist()
        return listOfFileNames

    def extract_zip_files(self):
        """ iterate throught files and extract their """
        lst = self.show_files_in_dir()
        files_list = list()
        new_file_name = ''
        for fileName in lst:
            _suffix = pathlib.Path(fileName.replace(' ', '')).suffix
            if pathlib.Path(fileName.replace(' ', '')).suffix in lst_exet_files:
                # check if folder in zip. If true -> extract first from zip then from folder
                if re.match(f'.+/.+{_suffix}', fileName):
                    check = 0
                    # _root -> folder name
                    _root = str(fileName).split('/')[0]
                    # file name
                    _name_file = ''.join(str(fileName).split('/')[-1])
                else:
                    check = 1
                    # _root -> folder name
                    _root = ''
                    # file name
                    _name_file = fileName
                if check == 0:
                    # check size of files
                    try:
                        size = int(self.zip.getinfo(fileName).file_size)
                    except:
                        size = 0
                    if size > 4500:
                        new_file_name = _name_file.replace('-', '_').replace(' ', '_').replace('(', '_').replace(')',
                                                                                                                 '_')
                        self.zip.extract(fileName, self.root_dir)
                        if self.lot_number is not None:
                            new_file_name = f'{self._id}_{self.lot_number}_{count_cyrillic(new_file_name)}'
                        else:
                            new_file_name = f'{self._id}_{count_cyrillic(new_file_name)}'
                        # path to folder with pictures
                        path_to_folder = os.path.join(self.root_dir, _root)

                        # iterate throught picture (1) in directory
                        for pic in os.listdir(path_to_folder):
                            # move file to etp directory
                            old_name = f'{path_to_folder}/{pic}'
                            new_name = f'{self.root_dir}/{new_file_name}'
                            if os.path.isdir(old_name):
                                old_name = old_name + '/' + _name_file
                                os.rename(old_name, new_name)
                                # delete folder
                                shutil.rmtree(path_to_folder, ignore_errors=True)
                            else:
                                # move file to etp directory
                                os.rename(old_name, new_name)
                                # delete folder
                                os.rmdir(path_to_folder)
                elif check == 1:
                    try:
                        size = int(self.zip.getinfo(fileName).file_size)
                    except:
                        size = 0
                    if size > 4500:
                        new_file_name: str = self.return_file_name_extra(file_name=_name_file)
                        self.zip.extract(fileName, self.root_dir)
                        os.rename(f'{self.root_dir}/{fileName}', f'{self.root_dir}/{new_file_name}')
                else:
                    new_file_name = ''
                files_list.append(
                    {'original_name': count_cyrillic(fileName), 'link': self.rel_path + new_file_name.strip(), 'link_etp': self.url})
            else:
                files_list.append({'original_name': count_cyrillic(fileName), 'link': '', 'link_etp': self.url})
        return files_list

    def delete_zip(self):
        try:
            os.remove(self.abs_path)
            return 0
        except NotADirectoryError as ex:
            logger.error(f'{self._id} :: ERROR ZIP FILE\n{ex}')

    def return_file_name_extra(self, file_name) -> str:
        """ if rar without folder just files. return clean file name """
        new_file_name = file_name.replace('-', '_').replace(' ', '_').replace('(', '_').replace(')', '_')
        if self.lot_number is not None:
            new_file_name = f'{self._id}_{self.lot_number}_{count_cyrillic(new_file_name)}'
        else:
            new_file_name = f'{self._id}_{count_cyrillic(new_file_name)}'
        return new_file_name


# _zip = ZipFiles(_path, _root_dir=p)
#
# if __name__ == '__main__':
#     print(_zip.extract_zip_files())
#     _zip.delete_zip()
