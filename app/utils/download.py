import pathlib
import shutil
import time
import requests
import urllib3
from random import choice
from requests import Session

from .config import archive_formats, socks5_proxies, headers, unpack_archives
from .archive import ZipFiles, RarFiles, SevenZipFiles
from .logger import logger
from app.db.models.download_data import DownloadData

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

ARCHIVE_HANDLERS = {".zip": ZipFiles, ".rar": RarFiles, ".7z": SevenZipFiles}


class DownloadFiles:
    @staticmethod
    def change_proxy():
        if socks5_proxies:
            return {
                "http": "socks5://" + choice(socks5_proxies),
                "https": "socks5://" + choice(socks5_proxies),
            }
        return None

    @staticmethod
    def request_to_download_general(
            download_data: DownloadData,
            absolute_path: pathlib.PurePath,
            relative_path: pathlib.PurePath,
            attempts: int = 5,
    ) -> list[pathlib.PurePath]:
        session = requests.Session()
        session.headers.update({"User-Agent": headers["User-Agent"]})
        path = pathlib.Path(absolute_path)

        for attempt in range(1, attempts + 1):
            try:
                if path.suffix.lower() not in archive_formats or (
                        path.suffix.lower() in archive_formats and not unpack_archives
                ):
                    if not path.exists():
                        DownloadFiles.download_file(
                            session, download_data, absolute_path, attempt
                        )
                    return [relative_path]
                return DownloadFiles.download_archive(
                    session,
                    download_data,
                    absolute_path,
                    relative_path,
                    attempt,
                )
            except Exception as ex:
                if attempt == attempts:
                    logger.warning(
                        f"Attempt #{attempt} failed with error: {ex} Referer - {download_data.referer}"
                    )
                time.sleep(2)
        return []

    @staticmethod
    def download_file(
            session: Session,
            download_data: DownloadData,
            absolute_path: pathlib.PurePath,
            attempt: int,
    ):
        rd = download_data.model_dump()
        verify = rd.pop("verify")
        with session.request(
                **rd,
                stream=True,
                verify=verify if attempt == 1 else (attempt != 5),
        ) as response:
            response.raise_for_status()
            with open(absolute_path, "wb") as out_file:
                shutil.copyfileobj(response.raw, out_file)
            logger.info(f"Download finished successfully (attempt {attempt})")

    @staticmethod
    def download_archive(
            session: Session,
            download_data: DownloadData,
            absolute_path: pathlib.PurePath,
            relative_path: pathlib.PurePath,
            attempt: int,
    ):
        handler = ARCHIVE_HANDLERS.get(absolute_path.suffix)
        if not handler:
            return []

        rd = download_data.model_dump()
        verify = rd.pop("verify")

        with session.request(
                **rd,
                stream=True,
                verify=verify if attempt == 1 else (attempt != 5),
        ) as response:
            with open(absolute_path, "wb") as archive_file:
                archive_file.write(response.content)

        archive = handler(
            absolute_path=absolute_path,
            relative_path=relative_path,
            file_name=download_data.file_name,
            url=download_data.url,
        )
        try:
            files = archive.extract_files()
            archive.delete_archive()
            logger.info(
                f"Extracting archive finished successfully {absolute_path.suffix.upper()}"
            )
            return files
        except Exception as e:
            logger.warning(f"Error extracting archive {download_data.url}: {e}")
            archive.delete_archive()
            return []
