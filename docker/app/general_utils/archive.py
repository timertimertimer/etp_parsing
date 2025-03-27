import logging
import os
from pathlib import PurePath, Path
from pydantic import HttpUrl

from .work_with_path_and_dir import sanitize_filename
from .config import image_and_doc_formats
from .work_with_text_and_number import fix_encoding

logger = logging.getLogger(__name__)


class ArchiveFiles:
    """Родительский класс для работы с архивами"""

    def __init__(
            self,
            absolute_path: PurePath,
            relative_path: PurePath | str,
            file_name: str, url: str | HttpUrl
    ):
        self.absolute_archive_path = PurePath(absolute_path)
        self.relative_archive_path = PurePath(relative_path)
        self.file_name = file_name
        if isinstance(url, HttpUrl):
            self.url = str(url)
        else:
            self.url = url
        self.archive_class = None

    def extract_files(self):
        files_list = []
        with self.archive_class(str(self.absolute_archive_path)) as archive:
            for file_name in archive.namelist():
                fixed_name = sanitize_filename(fix_encoding(file_name))
                if len(fixed_name) > 75:
                    fixed_name = fixed_name[:30] + '_' + fixed_name[-35::1]
                fixed_absolute_file_path = Path(self.absolute_archive_path.parent / fixed_name)
                fixed_relative_file_path = Path(self.relative_archive_path.parent / fixed_name)
                if fixed_name.endswith('/'):
                    fixed_absolute_file_path.mkdir(parents=True, exist_ok=True)
                    continue
                fixed_absolute_file_path.parent.mkdir(parents=True, exist_ok=True)
                link = None
                if fixed_absolute_file_path.exists():
                    link = fixed_relative_file_path
                elif fixed_absolute_file_path.suffix in image_and_doc_formats:
                    with archive.open(file_name) as source, open(fixed_absolute_file_path, 'wb') as target:
                        target.write(source.read())
                    link = fixed_relative_file_path
                if link:
                    files_list.append(link)
        return files_list

    def delete_archive(self):
        try:
            os.remove(self.absolute_archive_path)
        except NotADirectoryError as ex:
            logger.error(f'{self.file_name} :: ERROR ARCHIVE FILE\n{ex}')


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
