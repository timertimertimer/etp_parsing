import logging
import os
import pathlib
import re
import shutil

import rarfile

from general_utils import count_cyrillic
from general_utils.config import lst_exet_files

logger = logging.getLogger(__name__)


class RarFiles:

    def __init__(self, _path, _root_dir, _file_name, _id, lot_number, url, rel_path):
        self.abs_path = _path
        self.root_dir = _root_dir
        self._file_name = _file_name
        self._id = _id
        self.lot_number = lot_number
        self.url = url
        self.rel_path = rel_path + '/'
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
        new_file_name = ''
        for fileName in lst:
            _suffix = pathlib.Path(fileName.replace(' ', '')).suffix
            if _suffix in lst_exet_files:
                # check if folder in rar. If true -> extract first from rar then from folder
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
                    try:
                        size = int(self.rar.getinfo(fileName).file_size)
                    except:
                        size = 0
                    if size > 4500:
                        new_file_name = _name_file.replace('-', '_').replace(' ', '_').replace('(', '_').replace(')',
                                                                                                                 '_')
                        self.rar.extract(fileName, self.root_dir)
                        if self.lot_number is not None:
                            new_file_name = f'{self._id}_{self.lot_number}_{count_cyrillic(new_file_name)}'
                            if 'part' in fileName:
                                match = ''.join(re.findall(r'.+(part\d+).+', fileName))
                                new_file_name = f'{self._id}_{self.lot_number}_{match}_{count_cyrillic(new_file_name)}'
                        else:
                            new_file_name = f'{self._id}_{count_cyrillic(new_file_name)}'
                            if 'part' in fileName:
                                match = ''.join(re.findall(r'.+(part\d+).+', fileName))
                                new_file_name = f'{self._id}_{self.lot_number}_{match}_{count_cyrillic(new_file_name)}'
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
                        size = int(self.rar.getinfo(fileName).file_size)
                    except:
                        size = 0
                    if size > 4500:
                        new_file_name: str = self.return_file_name_extra(file_name=_name_file)
                        self.rar.extract(fileName, self.root_dir)
                        os.rename(f'{self.root_dir}/{fileName}', f'{self.root_dir}/{new_file_name}')
                else:
                    new_file_name = ''
                files_list.append(
                    {'original_name': count_cyrillic(fileName), 'link': self.rel_path + new_file_name.strip(), 'link_etp': self.url})
            else:
                files_list.append({'original_name': count_cyrillic(fileName), 'link': None, 'link_etp': self.url})
        return files_list

    def return_file_name_extra(self, file_name) -> str:
        """ if rar without folder just files. return clean file name """
        new_file_name = file_name.replace('-', '_').replace(' ', '_').replace('(', '_').replace(')', '_')
        if self.lot_number is not None:
            new_file_name = f'{self._id}_{self.lot_number}_{count_cyrillic(new_file_name)}'
        else:
            new_file_name = f'{self._id}_{count_cyrillic(new_file_name)}'
        return new_file_name

    def delete_rar(self):
        try:
            os.remove(self.abs_path)
            return 0
        except NotADirectoryError as ex:
            logger.error(f'{self._id} :: ERROR RAR FILE\n{ex}')
