import pathlib
import re
import shutil
import py7zr
from crawler_bankrot_cdtrf.utils.config import lst_exet_files
import os
import logging

logger = logging.getLogger(__name__)

# _path = f'/home/admin/web/78.24.219.218/public_html/downloads/etp_trade_place_vetp/2021/01/102043719_~~_lot_1_0_Электростанция.zip'
# p = '/home/admin/web/78.24.219.218/public_html/downloads/etp_trade_place_vetp/2021/01/'


class SevenZFiles:

    def __init__(self, _path, _root_dir, _file_name, _id, lot_number, url, rel_path):
        self.abs_path = _path
        self.root_dir = _root_dir
        self._file_name = _file_name
        self._id = _id
        self.lot_number = lot_number
        self.url = url
        self.rel_path = rel_path + '/'

    def extract_zip_files(self):
        """ iterate throught files and extract their """
        files_list = list()
        with py7zr.SevenZipFile(self.abs_path, 'r') as _zip:
            allfiles = _zip.getnames()
            targets = [f for f in allfiles if pathlib.Path(f).suffix in lst_exet_files]
            _zip.extract(path=self.root_dir, targets=targets)
            for t in targets:
                _suffix = pathlib.Path(t).suffix
                if re.match(f'.+/.+{_suffix}', t):
                    check = 0
                    # _root -> folder name
                    _root = str(t).rsplit('/', maxsplit=1)[0]
                    # file name
                    _name_file = ''.join(str(t).split('/')[-1])
                else:
                    check = 1
                    # _root -> folder name
                    _root = ''
                    # file name
                    _name_file = t
                new_file_name = _name_file.replace('-', '_').replace(' ', '_').replace('(', '_').replace(')', '_')
                if self.lot_number is not None:
                    new_file_name = f'{self._id}_{self.lot_number}_{new_file_name}'
                else:
                    new_file_name = f'{self._id}_{new_file_name}'
                old_name = os.path.join(self.root_dir, t)
                size = os.path.getsize(old_name)
                if size > 15000:
                    new_name = os.path.join(self.root_dir, new_file_name)
                    if os.path.isdir(old_name):
                        os.rename(old_name, new_name)
                        shutil.rmtree(old_name, ignore_errors=True)
                    else:
                        # move file to etp directory
                        os.rename(old_name, new_name)
                    files_list.append(
                                 {'original_name': _name_file, 'link': self.rel_path + new_file_name.strip(), 'link_etp': self.url})
                else:
                    shutil.rmtree(old_name, ignore_errors=True)
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
            new_file_name = f'{self._id}_{self.lot_number}_{new_file_name}'
        else:
            new_file_name = f'{self._id}_{new_file_name}'
        return new_file_name



