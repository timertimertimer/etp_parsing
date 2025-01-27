import os
import time

import requests
import pathlib
from .work_with_text_and_number import cookie_parser
from ..utils.work_with_path_and_dir import GeneralFilesDir
from random import choice
import logging
from ..utils.working_with_url import UrlConfig
import shutil
from .config import path_user_agent, path_to_socks5
from .rar_file_manager import RarFiles
from .zip_file_manager import ZipFiles
from .seven_z import SevenZFiles
import shutil
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
logger = logging.getLogger(__name__)
with open(f'{path_user_agent}', 'r') as f:
    lines = f.readlines()
agent_list = [i.replace('\\n', '').strip() for i in lines]

with open(f'{path_to_socks5}', 'r') as f:
    lines = f.readlines()
socks_list = [i.replace('\\n', '').strip() for i in lines]


class DownloadFiles(GeneralFilesDir):
    general = GeneralFilesDir()

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
    headers_ = {'Accept': '*/*',
                'Accept-Encoding': 'gzip, deflate, br',
                'Accept-Language': 'en-US,en;q=0.9,ru-RU;q=0.8,ru;q=0.7,de-DE;q=0.6,de;q=0.5,uk-UA;q=0.4,uk;q=0.3,ro-RO;q=0.2,ro;q=0.1',
                'Cache-Control': 'no-cache',
                'Connection': 'keep-alive',
                'DNT': '1',
                'Host': 'sales.lot-online.ru',
                'Origin': 'https://sales.lot-online.ru',
                'Pragma': 'no-cache',
                'Sec-Fetch-Dest': 'document',
                'Sec-Fetch-Mode': 'navigate',
                'Sec-Fetch-Site': 'same-origin',
                'Sec-Fetch-User': '?1',
                'Upgrade-Insecure-Request': '1',
                'User-Agent': choice(agent_list)}

    def make_request(self, url, referer, cookies):
        u = UrlConfig()
        url = u.parse_url(url)
        session = requests.Session()
        session.proxies.update(self.proxies)
        session.headers.update(self.headers_)
        session.headers.update({'Referer': referer, 'Cookie': cookies})
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
        except Exception as e:
            logger.critical(f'{url}:: REQUEST STATUS CODE - {r.status_code} {e}')
            return None

    def request_to_download_general(self, url, referer, original_name, cookies, post_data, trade_id, attempts=5):
        u = UrlConfig()
        url = url
        url = u.parse_url(url)
        session = requests.Session()
        cookie = cookie_parser(cookies)
        root_dir = self.general.return_absolute_path()
        abs_path = self.general.return_absolute_path()
        for attempt in range(1, attempts + 1):
            try:
                # session.proxies.update(self.proxies)
                session.headers.update(self.headers_)
                session.cookies.update(cookie)
                session.proxies.update(self.proxies)
                session.headers.update({'Referer': referer, 'Cookie': cookies})
                abs_path = abs_path + original_name
                if attempt > 1:
                    time.sleep(2)  # 2 seconds wait time between downloads
                if pathlib.Path(abs_path).suffix not in ['.zip', '.rar', '.7z']:
                    with session.post(url, data=post_data, stream=True) as response:
                        with open(abs_path, 'wb') as out_file:
                            response.raw.decode_content = True
                            shutil.copyfileobj(response.raw, out_file)
                            # for chunk in response.iter_content(chunk_size=1024 * 1024):  # 1MB chunks
                            #     out_file.write(chunk)
                        # logger.info('Download finished successfully')
                        return 0
                elif pathlib.Path(abs_path).suffix == '.rar':
                    with session.post(url, data=post_data, stream=True) as response:
                        with open(abs_path, 'wb') as out_file:
                            response.raw.decode_content = True
                            shutil.copyfileobj(response.raw, out_file)
                    rarObject = RarFiles(_path_to_file=abs_path, _root_dir=root_dir, trade_id=trade_id)
                    lst_archive_files = rarObject.extract_rar_files()
                    rarObject.delete_rar()
                    logger.info(f'Download finished successfully RAR RAR RAR RAR {trade_id}')
                    return lst_archive_files

                elif pathlib.Path(abs_path).suffix == '.zip':
                    with session.post(url, data=post_data, stream=True) as response:
                        with open(abs_path, 'wb') as out_file:
                            response.raw.decode_content = True
                            shutil.copyfileobj(response.raw, out_file)
                    zipObject = ZipFiles(_path_to_file=abs_path, _root_dir=root_dir, trade_id=trade_id)
                    lst_archive_files = zipObject.extract_zip_files()
                    zipObject.delete_zip()
                    logger.info(f'Download finished successfully ZIP ZIP ZIP ZIP {trade_id}')
                    return lst_archive_files

                elif pathlib.Path(abs_path).suffix == '.7z':
                    with session.post(url, data=post_data, stream=True) as response:
                        with open(abs_path, 'wb') as out_file:
                            response.raw.decode_content = True
                            shutil.copyfileobj(response.raw, out_file)
                    sevenObject = SevenZFiles(_path_to_file=abs_path, _root_dir=root_dir, trade_id=trade_id)
                    lst_archive_files = sevenObject.extract_zip_files()
                    sevenObject.delete_zip()
                    logger.info(f'Download finished successfully 7Z 7Z 7Z 7Z {trade_id}')
                    return lst_archive_files
            except Exception as ex:
                if attempt == 3 and 'rar' in original_name:
                    os.remove(abs_path)
                    return list()
                elif 'Need to start from first volume' in str(ex):
                    logger.warning(f'{ex} :: Attempt - {attempt} :: EXIT')
                    os.remove(abs_path)
                    return list()
                if attempt == 5:
                    logger.error(f'Attempt #{attempt} failed with error: {ex}, \n{url} - referer {referer}')
                elif attempt == 3:
                    logger.warning(f'{ex} :: Attempt - {attempt}')
        return ''

    def request_to_download_lot(self, url, referer, original_name, cookies, attempts=5):
        u = UrlConfig()
        url = url
        url = u.parse_url(url)
        session = requests.Session()
        abs_path = self.general.return_absolute_path()
        for attempt in range(1, attempts + 1):
            try:
                session.proxies.update(self.proxies)
                session.headers.update(self.headers_)
                session.headers.update({'Referer': referer, 'Cookie': cookies})
                if attempt > 1:
                    time.sleep(2)  # 2 seconds wait time between downloads
                with session.get(url, stream=True) as response:
                    response.raise_for_status()
                    with open(abs_path + original_name, 'wb') as out_file:
                        for chunk in response.iter_content(chunk_size=1024 * 1024):  # 1MB chunks
                            out_file.write(chunk)
                    # logger.info('Download finished successfully')
                    return 0
            except Exception as ex:
                if attempt == 5:
                    logger.error(
                        f'Attempt #{attempt} failed with error: {ex} Referer -> {referer}::  :: File name {original_name}')
                elif attempt == 2:
                    logger.error(f'{ex} :: ERROR lot file -  Attempt - {attempt}')
        return ''
