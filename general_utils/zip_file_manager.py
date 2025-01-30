import pathlib
import re
import shutil
from zipfile import ZipFile

from pydantic import HttpUrl

from .config import lst_exet_files
import os
import logging

from .work_with_text_and_number import count_cyrillic

logger = logging.getLogger(__name__)


def fix_encoding(name):
    if re.search(r'[^\w\s\.\-/]', name):
        try:
            return name.encode("cp437").decode("cp866")
        except UnicodeDecodeError:
            return name
    return name


class ZipFiles:

    def __init__(
            self,
            absolute_path: pathlib.PurePath,
            relative_path: pathlib.PurePath | str,
            root_directory: str,
            file_name: str, trading_id: str, lot_number: str, url: str | HttpUrl,
    ):
        self.absolute_path = pathlib.PurePath(absolute_path)
        self.root_directory = pathlib.PurePath(root_directory)
        self.file_name = file_name
        self.trading_id = trading_id
        self.lot_number = lot_number
        self.url = url
        self.relative_path = pathlib.PurePath(relative_path)
        self.zip = ZipFile(str(self.absolute_path))

    def show_files_in_dir(self) -> list:
        """ return list with file's name """
        listOfFileNames = self.zip.namelist()
        return listOfFileNames

    def extract_zip_files(self):
        """ Разархивирует файлы и перемещает их в `root_directory`. """
        files_list = []

        with ZipFile(self.absolute_path) as zip_file:
            for file_name in zip_file.namelist():
                if file_name.endswith('/'):
                    continue  # Пропускаем папки

                extract_path = os.path.join(self.root_directory, os.path.basename(file_name))

                zip_file.extract(file_name, self.root_directory)

                # Поиск извлеченного файла
                extracted_file = None
                for root, _, files in os.walk(self.root_directory):
                    for f in files:
                        if f == os.path.basename(file_name):
                            extracted_file = os.path.join(root, f)
                            break
                    if extracted_file:
                        break  # Останавливаем поиск после первого совпадения

                if extracted_file:
                    os.rename(extracted_file, extract_path)
                    files_list.append({
                        'original_name': count_cyrillic(file_name),
                        'link': self.root_directory / os.path.basename(file_name),
                        'link_etp': str(self.url)
                    })
                else:
                    logger.error(f"Файл {file_name} не найден после извлечения!")

        return files_list

    def delete_zip(self):
        try:
            os.remove(self.absolute_path)
            return 0
        except NotADirectoryError as ex:
            logger.error(f'{self.trading_id} :: ERROR ZIP FILE\n{ex}')

    def return_file_name_extra(self, file_name) -> str:
        """ if rar without folder just files. return clean file name """
        new_file_name = re.sub(r'[-\s()]', '_', file_name)
        if self.lot_number:
            return f"{self.trading_id}_{self.lot_number}_{count_cyrillic(new_file_name)}"
        return f"{self.trading_id}_{count_cyrillic(new_file_name)}"
