import logging
import os
from pathlib import PurePath, Path
from pydantic import HttpUrl

from .work_with_path_and_dir import FilesDir
from .config import lst_exet_files
from .work_with_text_and_number import count_cyrillic, fix_encoding

logger = logging.getLogger(__name__)


class ArchiveFiles:
    """Родительский класс для работы с архивами"""

    def __init__(
            self,
            absolute_path: PurePath,
            relative_path: PurePath | str,
            root_directory: str,
            file_name: str, trading_id: str, lot_number: str, url: str | HttpUrl,
    ):
        self.absolute_path = PurePath(absolute_path)
        self.root_directory = PurePath(root_directory)
        self.file_name = file_name
        self.trading_id = trading_id
        self.lot_number = lot_number
        self.url = url
        self.relative_path = PurePath(relative_path)
        self.archive_class = None

    def extract_files(self):
        files_list = []
        with self.archive_class(str(self.absolute_path)) as archive:
            for file_name in archive.namelist():
                fixed_name = FilesDir.name_file_on_server(self.trading_id, fix_encoding(file_name), self.lot_number)
                fixed_extract_path = Path(self.root_directory / fixed_name)
                if file_name.endswith('/'):
                    if not fixed_extract_path.exists():
                        fixed_extract_path.mkdir()
                    continue
                elif not fixed_extract_path.parent.exists():
                    fixed_extract_path.parent.mkdir(parents=True)
                link = ''
                if fixed_extract_path.exists():
                    link = (self.relative_path.parent / fixed_name).as_posix()
                elif fixed_extract_path.suffix in lst_exet_files:
                    # archive.extract(file_name, self.root_directory)
                    # extracted_file = None
                    # for root, _, files in os.walk(self.root_directory):
                    #     for f in files:
                    #         if f == os.path.basename(file_name):
                    #             extracted_file = Path(root) / f
                    #             break
                    #     if extracted_file:
                    #         break
                    # os.rename(extracted_file, fixed_extract_path)
                    with archive.open(file_name) as source, open(fixed_extract_path, 'wb') as target:
                        target.write(source.read())
                    link = (self.relative_path.parent / fixed_name).as_posix()
                files_list.append(
                    {'original_name': count_cyrillic(fixed_name), 'link': link, 'link_etp': str(self.url)}
                )
        return files_list

    def delete_archive(self):
        try:
            os.remove(self.absolute_path)
        except NotADirectoryError as ex:
            logger.error(f'{self.trading_id} :: ERROR ARCHIVE FILE\n{ex}')


class ZipFiles(ArchiveFiles):
    """Класс для работы с ZIP-архивами"""
    from zipfile import ZipFile

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.archive_class = self.ZipFile


class RarFiles(ArchiveFiles):
    """Класс для работы с RAR-архивами"""
    from rarfile import RarFile

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.archive_class = self.RarFile


class SevenZipFiles(ArchiveFiles):
    """Класс для работы с 7z-архивами"""
    from py7zr import SevenZipFile

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.archive_class = self.SevenZipFile
