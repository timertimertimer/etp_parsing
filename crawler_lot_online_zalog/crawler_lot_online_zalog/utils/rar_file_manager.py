import logging
import os
import pathlib
import re
import shutil

import rarfile

from general_utils.config import lst_exet_files
from .working_with_text_cookies_num import count_cyrillic
from ..utils.work_with_path_and_dir import GeneralFilesDir

logger = logging.getLogger(__name__)


class RarFiles:

    def __init__(self, _path_to_file, _root_dir, trade_id):
        self.abs_path = _path_to_file
        self.root_dir = _root_dir
        self._id = trade_id
        self._dir = GeneralFilesDir()
        self.rel_path = self._dir.return_relative_path()
        self.main_rar = rarfile
        self.rar = self.main_rar.RarFile(self.abs_path, 'r')

    def show_files_in_dir(self) -> list:
        """ return list with file's name """
        try:
            listOfFileNames = self.rar.namelist()
            return listOfFileNames
        except:
            listOfFileNames = list()
            return listOfFileNames

    def extract_rar_files(self):
        lst = self.show_files_in_dir()
        files_list = list()
        for fileName in lst:
            _suffix = pathlib.Path(fileName.replace(' ', '')).suffix
            if _suffix in lst_exet_files:
                # check if folder in rar. If true -> extract first from rar then from folder
                if re.match(f'.+/.+{_suffix}', fileName):
                    check = 0
                    # _root -> folder name
                    _root = str(fileName).rsplit('/', maxsplit=1)[0]
                    # file name
                    _name_file = ''.join(str(fileName).split('/')[-1])
                else:
                    check = 1
                    # _root -> folder name
                    _root = ''
                    # file name
                    _name_file = fileName
                if check == 0:
                    try:
                        size = int(self.rar.getinfo(fileName).file_size)
                    except:
                        size = 0
                    if size > 4500:
                        new_file_name = _name_file.replace('-', '_').replace(' ', '_').replace('(', '_').replace(')',
                                                                                                                 '_')
                        new_file_name = f'{self._id}_{count_cyrillic(new_file_name)}'
                        self.rar.extract(fileName, self.root_dir)
                        # path to folder with docs
                        path_to_folder = os.path.join(self.root_dir, _root)
                        # iterate throught doc (1) in directory
                        for doc_ in os.listdir(path_to_folder):
                            # move file to etp directory
                            old_name = f'{path_to_folder}/{doc_}'
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
                            files_list.append(
                                {'original_name': count_cyrillic(fileName), 'link': self.rel_path + new_file_name.strip(),
                                 'link_etp': self.rel_path + new_file_name.strip()})
                elif check == 1:
                    try:
                        size = int(self.rar.getinfo(fileName).file_size)
                    except:
                        size = 0
                    try:
                        if size > 4500:
                            new_file_name: str = self.return_file_name_extra(file_name=_name_file)
                            self.rar.extract(fileName, self.root_dir)
                            os.rename(f'{self.root_dir}/{fileName}', f'{self.root_dir}/{new_file_name}')
                            files_list.append(
                                {'original_name': count_cyrillic(fileName), 'link': self.rel_path + new_file_name.strip(),
                                    'link_etp': self.rel_path + new_file_name.strip()})
                    except Exception as ex:
                        os.remove(f'{self.root_dir}/{fileName}')
                        logger.error(f'{ex} :: this is exception extract rar')
        return files_list

    def return_file_name_extra(self, file_name) -> str:
        """ if rar without folder just files. return clean file name """
        new_file_name = file_name.replace('-', '_').replace(' ', '_').replace('(', '_').replace(')', '_')
        new_file_name = f'{self._id}_{count_cyrillic(new_file_name)}'
        return new_file_name

    def delete_rar(self):
        try:
            os.remove(self.abs_path)
            return 0
        except NotADirectoryError as ex:
            logger.error(f'{self._id} :: ERROR RAR FILE\n{ex}')
