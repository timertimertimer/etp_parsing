import logging
import os
import pathlib
import shutil
import time
from random import choice

import requests
import urllib3
from crawler_be_two_be.utils.config import path_user_agent, path_to_socks5, lst_exet_archive
from ..utils.rar_file_manager import RarFiles
from ..utils.seven_z import SevenZFiles
from ..utils.working_with_url import UrlConfig
from ..utils.zip_file_manager import ZipFiles

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
logger = logging.getLogger(__name__)
with open(f'{path_user_agent}', 'r') as f:
    lines = f.readlines()
agent_list = [i.replace('\\n', '').strip() for i in lines]

with open(f'{path_to_socks5}', 'r') as f:
    lines = f.readlines()
socks_list = [i.replace('\\n', '').strip() for i in lines]

USER_AGENT = choice(agent_list)
headers_ = {'Accept': '*/*',
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept-Language': 'en-US,en;q=0.9,ru-RU;q=0.8,ru;q=0.7,de-DE;q=0.6,de;q=0.5,uk-UA;q=0.4,uk;q=0.3,ro-RO;q=0.2,ro;q=0.1',
            'Cache-Control': 'no-cache',
            'Connection': 'keep-alive',
            'DNT': '1',
            'User-Agent': USER_AGENT}


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

    def make_request(self, url, referer):
        u = UrlConfig()
        url = u.parse_url(url)
        session = requests.Session()
        #session = requests.Session()
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

    def request_to_download_general(self, url, referer, _abs_path, attempts=7, _relative_path=None,
                                    _id=None, lot_num=None):
        u = UrlConfig()
        url_ = url
        url_ = u.parse_url(url_)
        session = requests.Session()
        session.proxies.update(self.proxies)
        session.headers.update(headers_)
        abs_path = _abs_path
        for attempt in range(1, attempts + 1):
            try:
                _proxies = self.proxies
                session.proxies.update(self.proxies)
                if attempt > 1:
                    time.sleep(2)  # 2 seconds wait time between downloads

                if pathlib.Path(abs_path).suffix not in ['.zip', '.rar', '.7z']:
                    if attempt == 5 or attempt == 3:
                        with requests.get(url, stream=True, proxies=self.proxies, verify=False, timeout=30) as response:
                            response.raise_for_status()
                            with open(abs_path, 'wb') as out_file:
                                for chunk in response.iter_content(chunk_size=1024 * 1024):  # 1MB chunks
                                    out_file.write(chunk)
                        logger.info(f'Download finished successfully - attempt == {attempt}')
                        return 0
                    else:
                        with session.get(url, stream=True, timeout=10) as response:
                            with open(abs_path, 'wb') as out_file:
                                response.raw.decode_content = True
                                shutil.copyfileobj(response.raw, out_file)

                            logger.info(f'Download finished successfully')
                            return 0
                elif pathlib.Path(abs_path).suffix == '.zip':
                    if attempt == 5 or attempt == 3:
                        res = requests.get(url, stream=True, proxies=self.proxies, verify=False, timeout=30)
                    else:
                        res = session.get(url, stream=True, timeout=10, verify=False, )
                    with open(abs_path, "wb") as zip_:
                        zip_.write(res.content)
                    # p -> tuple with etp dir and zip's name
                    p = os.path.split(abs_path)
                    objectZip = ZipFiles(_path=abs_path, _root_dir=p[0], _file_name=p[1], _id=_id, lot_number=lot_num,
                                         url=url, rel_path=_relative_path)
                    lst_files = objectZip.extract_zip_files()
                    objectZip.delete_zip()
                    logger.info(f'Download finished successfully ZIP')
                    return lst_files
                elif pathlib.Path(abs_path).suffix == '.rar':
                    if attempt != 3:
                        with session.get(url, stream=True, timeout=10) as response:
                            with open(abs_path, 'wb') as out_file:
                                response.raw.decode_content = True
                                shutil.copyfileobj(response.raw, out_file)
                    else:
                        with requests.get(url, stream=True, proxies=self.proxies, timeout=12) as response:
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
                if attempt == 7:
                    logger.error(f'Attempt #{attempt} failed with error: {ex} Referer - {referer}')
        return ''
