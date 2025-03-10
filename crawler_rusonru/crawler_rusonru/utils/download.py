import logging
import os
import pathlib
import shutil
import time
from random import choice

import urllib3

from general_utils.config import socks5_proxies, headers
from ..utils.zip_file_manager import ZipFiles
from ..utils.rar_file_manager import RarFiles
from ..utils.seven_z import SevenZFiles

import requests

from ..utils.working_with_url import UrlConfig

logger = logging.getLogger(__name__)
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


class DownloadFiles:
    if len(socks5_proxies) > 0 and socks5_proxies[0] != '':
        proxies = {
            'http': 'socks5://' + choice(socks5_proxies),
            'https': 'socks5://' + choice(socks5_proxies)

        }
    else:
        proxies = {
            "http": '',
            "https": '',
        }

    def request_to_download_general(self, url, referer, _abs_path, host='rus-on.ru', attempts=6, _relative_path=None,
                                    _id=None, lot_num=None):
        u = UrlConfig()
        url_ = url
        host = u.return_netloc(host)
        url_ = u.parse_url(url_)
        session = requests.Session()
        if self.proxies:
            session.proxies.update(self.proxies)
        session.headers.update(headers)
        session.headers.update({'Referer': referer, 'Host': host})
        abs_path = _abs_path
        for attempt in range(1, attempts + 1):
            try:
                _headers = headers
                _headers['Referer'] = referer
                _headers['Host'] = host
                if self.proxies:
                    session.proxies.update(self.proxies)
                if attempt > 1:
                    time.sleep(2)  # 2 seconds wait time between downloads

                if pathlib.Path(abs_path).suffix not in ['.zip', '.rar', '.7z']:
                    if attempt == 5:
                        with requests.get(url, stream=True, proxies=self.proxies, verify=False) as response:
                            response.raise_for_status()
                            with open(abs_path, 'wb') as out_file:
                                for chunk in response.iter_content(chunk_size=1024 * 1024):  # 1MB chunks
                                    out_file.write(chunk)
                        logger.info(f'Download finished successfully - attempt == {attempt}')
                        return 0
                    else:
                        with requests.get(url, stream=True, proxies=self.proxies) as response:
                            with open(abs_path, 'wb') as out_file:
                                response.raw.decode_content = True
                                shutil.copyfileobj(response.raw, out_file)
                            logger.info(f'Download finished successfully')
                            return 0
                elif pathlib.Path(abs_path).suffix == '.zip':
                    if attempt == 5:
                        res = requests.get(url, stream=True, proxies=self.proxies, verify=False)
                    else:
                        res = requests.get(url, stream=True, proxies=self.proxies)
                    with open(abs_path, "wb") as zip_:
                        zip_.write(res.content)
                    # p -> tuple with etp dir and zip's name
                    p = os.path.split(abs_path)
                    objectZip = ZipFiles(_path=abs_path, _root_dir=p[0], _file_name=p[1], _id=_id, lot_number=lot_num,
                                         url=url, rel_path=_relative_path)
                    lst_files = objectZip.extract_zip_files()
                    objectZip.delete_zip()
                    # logger.info(f'Download finished successfully ZIP')
                    return lst_files
                elif pathlib.Path(abs_path).suffix == '.rar':
                    if attempt == 3:
                        with requests.get(url, stream=True, proxies=self.proxies, timeout=20) as response:
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
                        # logger.info(f'Download finished successfully  RAR')
                        return lst_files
                    except:
                        os.remove(abs_path)
                        return ''
                elif pathlib.Path(abs_path).suffix == '.7z':
                    res = requests.get(url, stream=True, proxies=self.proxies, timeout=20)
                    with open(abs_path, "wb") as zip_:
                        zip_.write(res.content)
                    # p -> tuple with etp dir and zip's name
                    p = os.path.split(abs_path)
                    objectZip = SevenZFiles(_path=abs_path, _root_dir=p[0], _file_name=p[1], _id=_id,
                                            lot_number=lot_num,
                                            url=url, rel_path=_relative_path)
                    lst_files = objectZip.extract_zip_files()
                    objectZip.delete_zip()
                    # logger.info(f'Download finished successfully  7Z')
                    return lst_files
                return ''
            except Exception as ex:
                print(url, ex)
                if attempt == 5:
                    logger.error(f'Attempt #{attempt} failed with error: {ex} Referer - {referer}')
        return ''
