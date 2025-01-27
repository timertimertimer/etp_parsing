import logging
import os
import pathlib
import shutil
import time
from random import choice

from icecream import ic

from .config import path_user_agent, path_to_socks5, lst_exet_archive
from ..utils.zip_file_manager import ZipFiles
from ..utils.rar_file_manager import RarFiles
from ..utils.seven_z import SevenZFiles

import requests

from ..utils.working_with_url import UrlConfig

logger = logging.getLogger(__name__)
with open(f'{path_user_agent}', 'r') as f:
    lines = f.readlines()
agent_list = [i.replace('\\n', '').strip() for i in lines]

with open(f'{path_to_socks5}', 'r') as f:
    lines = f.readlines()
socks_list = [i.replace('\\n', '').strip() for i in lines]


class DownloadFiles:
    if len(socks_list) > 0 and socks_list[0] != '':
        proxies = {
            'http': 'socks5://' + choice(socks_list),
            'https': 'socks5://' + choice(socks_list)

        }
    else:
        proxies = {
            "http": '',
            "https": '',
        }

    headers = {
        'Accept': "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.",
        'Accept-Encoding': 'gzip, deflate, br',
        'Accept-Language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7',
        'Cache-Control': 'no-cach',
        'Connection': 'keep-alive',
        'Pragma': 'no-cache',
        'Sec-Fetch-Dest': 'document',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-Site': 'same-origin',
        'Sec-Fetch-User': '?1',
        'User-Agent': choice(agent_list)
    }

    def make_request(self, url, referer):
        u = UrlConfig()
        url = u.parse_url(url)
        session = requests.Session()
        session.proxies.update(self.proxies)
        session.headers.update(self.headers)
        session.headers.update({'Referer': referer})
        try:
            with session.get(url, allow_redirects=False) as r:
                stop_counter = 0
                while stop_counter < 10:
                    if str(r.status_code) in ['200', '302', '301', '307']:
                        return r.text
                    else:
                        session.proxies.update(self.proxies)
                        stop_counter += 1
                        r = session.head(url, allow_redirects=False)
        except:
            logger.critical(f'{url}:: REQUEST STATUS CODE - {r.status_code}')
            return None

    def request_to_download_general(
            self, url, referer, _abs_path, host='nistp.ru', attempts=1, _relative_path=None,
                                    _id=None, lot_num=None
    ):
        u = UrlConfig()
        url_ = url
        host = u.return_netloc(host)
        url_ = u.parse_url(url_)
        session = requests.Session()
        if self.proxies:
            session.proxies.update(self.proxies)
        session.headers.update(self.headers)
        session.headers.update({'Referer': referer, 'Host': host})
        abs_path = _abs_path
        for attempt in range(1, attempts + 1):
            try:
                _headers = self.headers
                _headers['Referer'] = referer
                _headers['Host'] = host
                if self.proxies:
                    session.proxies.update(self.proxies)
                if attempt > 1:
                    time.sleep(2)  # 2 seconds wait time between downloads

                if pathlib.Path(abs_path).suffix not in lst_exet_archive:
                    self.download_files(attempt, url, abs_path)
                elif pathlib.Path(abs_path).suffix == '.zip':
                    self.download_zip(attempt, url, abs_path, _id, lot_num, _relative_path)
                elif pathlib.Path(abs_path).suffix == '.rar':
                    if attempt == 3:
                        with requests.get(url, stream=True, proxies=self.proxies) as response:
                            with open(abs_path, 'wb') as out_file:
                                response.raw.decode_content = True
                                shutil.copyfileobj(response.raw, out_file)
                    else:
                        with requests.get(url, stream=True, proxies=self.proxies) as response:
                            response.raise_for_status()
                            with open(abs_path, 'wb') as out_file:
                                for chunk in response.iter_content(chunk_size=1024 * 1024):  # 1MB chunks
                                    out_file.write(chunk)
                    # p -> tuple with etp dir and zip's name
                    p = os.path.split(abs_path)
                    try:
                        objectRar = RarFiles(_path=abs_path, _root_dir=p[0], _file_name=p[1], _id=_id,
                                             lot_number=lot_num,
                                             url=url, rel_path=_relative_path)

                        lst_files = objectRar.extract_rar_files()
                        objectRar.delete_rar()
                        logger.info(f'Download finished successfully  RAR')
                        return lst_files
                    except:
                        os.remove(abs_path)
                        return ''
                elif pathlib.Path(abs_path).suffix == '.7z':
                    res = requests.get(url, stream=True, proxies=self.proxies)
                    with open(abs_path, "wb") as zip_:
                        zip_.write(res.content)
                    # p -> tuple with etp dir and zip's name
                    p = os.path.split(abs_path)
                    objectZip = SevenZFiles(_path=abs_path, _root_dir=p[0], _file_name=p[1], _id=_id,
                                            lot_number=lot_num,
                                            url=url, rel_path=_relative_path)
                    lst_files = objectZip.extract_zip_files()
                    objectZip.delete_zip()
                    logger.info(f'Download finished successfully  7Z')
                    return lst_files
                return ''
            except Exception as ex:
                print(url, ex)
                if attempt == 5:
                    logger.error(f'Attempt #{attempt} failed with error: {ex} Referer - {referer}')
        return ''

    def download_files(self, attempt: int, url: str, absolute_path: str):
        if attempt == 5:
            with requests.get(url, stream=True, proxies=self.proxies, verify=False) as response:
                response.raise_for_status()
                with open(absolute_path, 'wb') as out_file:
                    for chunk in response.iter_content(chunk_size=1024 * 1024):  # 1MB chunks
                        out_file.write(chunk)
            logger.info(f'Download finished successfully - attempt == {attempt}')
        else:
            with requests.get(url, stream=True, proxies=self.proxies) as response:
                with open(absolute_path, 'wb') as out_file:
                    response.raw.decode_content = True
                    shutil.copyfileobj(response.raw, out_file)
                logger.info(f'Download finished successfully')

    def download_zip(self, attempt: int, url: str, absolute_path: str, id_: str, lot_number: str, relative_path: str):
        if attempt == 5:
            res = requests.get(url, stream=True, proxies=self.proxies, verify=False)
        else:
            res = requests.get(url, stream=True, proxies=self.proxies)
        with open(absolute_path, "wb") as zip_:
            zip_.write(res.content)
        # p -> tuple with etp dir and zip's name
        p = os.path.split(absolute_path)
        objectZip = ZipFiles(
            absolute_path=absolute_path, root_directory=p[0], file_name=p[1], _id=id_, lot_number=lot_number,
            url=url, rel_path=relative_path
        )
        lst_files = objectZip.extract_zip_files()
        objectZip.delete_zip()
        logger.info(f'Download finished successfully ZIP')
        return lst_files
