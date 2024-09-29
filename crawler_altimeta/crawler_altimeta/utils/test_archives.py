import pathlib
import re
from rarfile import RarFile
import os
import logging



_PATH = '/home/admin/web/78.24.219.218/public_html/downloads/etp_trade_place_vetp/2021/01/102041904_~~_5_Договора.rar'

class RarFiles:

    def __init__(self, _path):
        self.abs_path = _path
        self.rar = RarFile(self.abs_path, 'r')

    def show_files_in_dir(self) -> list:
        """ return list with file's name """
        listOfFileNames = self.rar.namelist()
        return listOfFileNames

rar = RarFiles(_path=_PATH)


if __name__ == '__main__':
    print(rar.show_files_in_dir())