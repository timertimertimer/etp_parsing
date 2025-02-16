import logging
import os
import pathlib
import shutil
import time
import requests
from random import choice

from requests import Session

from .config import lst_exet_archive, socks_list, headers
from .models import RequestData
from .archive import ZipFiles, RarFiles, SevenZipFiles
from .working_with_url import UrlConfig

logger = logging.getLogger(__name__)


class DownloadFiles:
    def __init__(self, referer: str = None, proxies: dict = None):
        self.proxies = proxies or self.change_proxy()
        self.session = requests.Session()
        if self.proxies:
            self.session.proxies.update(self.proxies)
        self.session.headers.update(headers | {'Referer': referer} if referer else {})

    def change_proxy(self):
        if socks_list:
            return {
                'http': 'socks5://' + choice(socks_list),
                'https': 'socks5://' + choice(socks_list)
            }

    def make_request(self, url, referer):
        u = UrlConfig()
        url = u.parse_url(url)
        try:
            with self.session.get(url, allow_redirects=False) as r:
                stop_counter = 0
                while stop_counter < 10:
                    if str(r.status_code) in ['200', '302', '301', '307']:
                        return r.text
                    else:
                        self.session.proxies.update(self.change_proxy())
                        stop_counter += 1
                        r = self.session.head(url, allow_redirects=False)
        except:
            logger.critical(f'{url}:: REQUEST STATUS CODE - {r.status_code}')

    def request_to_download_general(
            self, request_data: RequestData, absolute_path: pathlib.PurePath, relative_path: pathlib.PurePath,
            attempts: int = 5, trading_id=None, lot_number=None
    ):
        session = requests.Session()
        if self.proxies:
            session.proxies.update(self.proxies)
        session.headers.update(headers | request_data.headers)
        path = pathlib.Path(absolute_path)
        for attempt in range(1, attempts + 1):
            try:
                if path.suffix not in lst_exet_archive:
                    if path.exists():
                        return
                    return self.download_files(
                        attempt=attempt, session=session, absolute_path=absolute_path, request_data=request_data
                    )
                elif path.suffix == '.zip':
                    return self.download_zip(
                        attempt=attempt, session=session, absolute_path=absolute_path, trading_id=trading_id,
                        lot_number=lot_number,
                        relative_path=relative_path, request_data=request_data
                    )
                elif path.suffix == '.rar':
                    return self.download_rar(
                        attempt=attempt, session=session, request_data=request_data, absolute_path=absolute_path,
                        trading_id=trading_id, lot_number=lot_number, relative_path=relative_path
                    )
                elif path.suffix == '.7z':
                    return self.download_7z(
                        session=session, request_data=request_data, absolute_path=absolute_path, trading_id=trading_id,
                        lot_number=lot_number, relative_path=relative_path
                    )
            except Exception as ex:
                if attempt == attempts:
                    logger.error(f'Attempt #{attempt} failed with error: {ex} Referer - {request_data.referer}')
                    return []
            time.sleep(2)

    def download_files(
            self, session: Session, request_data: RequestData, attempt: int,
            absolute_path: pathlib.PurePath
    ):
        if attempt == 5:
            rd = request_data.model_dump()
            rd.pop('verify')
            with session.request(**rd, stream=True, proxies=self.proxies, verify=False) as response:
                response.raise_for_status()
                with open(absolute_path, 'wb') as out_file:
                    for chunk in response.iter_content(chunk_size=1024 * 1024):  # 1MB chunks
                        out_file.write(chunk)
            logger.info(f'Download finished successfully - attempt == {attempt}')
        else:
            with session.request(**request_data.model_dump(), stream=True, proxies=self.proxies) as response:
                with open(absolute_path, 'wb') as out_file:
                    response.raw.decode_content = True
                    shutil.copyfileobj(response.raw, out_file)
            logger.info(f'Download finished successfully')

    def download_zip(self, session: Session, request_data: RequestData, attempt: int, absolute_path: pathlib.PurePath,
                     trading_id: str,
                     lot_number: str, relative_path: pathlib.PurePath):
        if attempt == 5:
            rd = request_data.model_dump()
            rd.pop('verify')
            res = session.request(**rd, stream=True, proxies=self.proxies, verify=False)
        else:
            res = session.request(**request_data.model_dump(), stream=True, proxies=self.proxies)
        with open(absolute_path, "wb") as zip_:
            zip_.write(res.content)
        root_directory, archive_name = os.path.split(absolute_path)
        try:
            objectZip = ZipFiles(
                absolute_path=absolute_path, root_directory=root_directory, file_name=archive_name,
                trading_id=trading_id,
                lot_number=lot_number,
                url=request_data.url, relative_path=relative_path
            )
            lst_files = objectZip.extract_files()
            objectZip.delete_archive()
            logger.info(f'Download finished successfully ZIP')
            return lst_files
        except Exception as e:
            logger.error(f'Error downloading {request_data.url}: {e}')
            return []

    def download_rar(
            self, session: Session, request_data: RequestData, attempt: int, absolute_path: pathlib.PurePath,
            trading_id: str,
            lot_number: str, relative_path: pathlib.PurePath
    ):
        if attempt == 3:
            with session.request(**request_data.model_dump(), stream=True, proxies=self.proxies) as response:
                with open(absolute_path, 'wb') as out_file:
                    response.raw.decode_content = True
                    shutil.copyfileobj(response.raw, out_file)
        else:
            with session.request(**request_data.model_dump(), stream=True, proxies=self.proxies) as response:
                response.raise_for_status()
                with open(absolute_path, 'wb') as out_file:
                    for chunk in response.iter_content(chunk_size=1024 * 1024):  # 1MB chunks
                        out_file.write(chunk)
        root_directory, archive_name = os.path.split(absolute_path)
        try:
            objectRar = RarFiles(
                absolute_path=absolute_path, root_directory=root_directory, file_name=archive_name,
                trading_id=trading_id,
                lot_number=lot_number,
                url=request_data.url, relative_path=relative_path
            )
            lst_files = objectRar.extract_files()
            objectRar.delete_archive()
            logger.info(f'Download finished successfully RAR')
            return lst_files
        except Exception as e:
            logger.error(f'Error downloading {request_data.url}: {e}')
            os.remove(absolute_path)
            return []

    def download_7z(
            self, session: Session, request_data: RequestData, absolute_path: pathlib.PurePath, trading_id: str,
            lot_number: str,
            relative_path: pathlib.PurePath
    ):
        res = session.request(**request_data.model_dump(), stream=True, proxies=self.proxies)
        with open(absolute_path, "wb") as zip_:
            zip_.write(res.content)
        root_directory, archive_name = os.path.split(absolute_path)
        try:
            objectZip = SevenZipFiles(
                absolute_path=absolute_path, root_directory=root_directory, file_name=archive_name,
                trading_id=trading_id,
                lot_number=lot_number,
                url=request_data.url, relative_path=relative_path
            )
            lst_files = objectZip.extract_files()
            objectZip.delete_archive()
            logger.info(f'Download finished successfully 7Z')
            return lst_files
        except Exception as e:
            logger.error(f'Error downloading {request_data.url}: {e}')
            os.remove(absolute_path)
            return []
