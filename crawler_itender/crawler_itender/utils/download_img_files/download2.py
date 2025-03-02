import os
import pathlib
import re
import time

import requests
import urllib3

from random import choice
import logging
import shutil

from general_utils import UrlConfig
from general_utils.archive import ZipFiles, RarFiles
from general_utils.config import socks_list, headers, lst_exet_archive
from general_utils.seven_z import SevenZFiles

logger = logging.getLogger(__name__)
try:
    urllib3.util.ssl_.DEFAULT_CIPHERS += ':HIGH:!DH:!aNULL'
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
except:
    pass

logger = logging.getLogger(__name__)


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
        url = UrlConfig.parse_url(url)
        session = requests.Session()
        session.proxies.update(self.proxies)
        session.headers.update(headers)
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

    def request_to_download_general(self, url, referer, _abs_path, host, _relative_path, _id, lot_num='', attempts=5):
        url_ = url
        # url_ = u.parse_url(url_)
        session = requests.Session()
        f_name = pathlib.Path(_relative_path).name
        _relative_path = ''.join(re.sub(f'/{f_name}$', '', str(_relative_path)))
        for attempt in range(1, attempts + 1):
            try:
                session.proxies.update(self.proxies)
                session.headers.update(headers)
                session.headers.update({'Referer': referer, 'Host': host})
                if attempt > 1:
                    time.sleep(2)  # 2 seconds wait time between downloads
                if pathlib.Path(_abs_path).suffix not in lst_exet_archive:
                    if 'uralbidin' in url_ or 'utender' in url_:
                        res = session.get(url_, stream=True, verify=False, timeout=20)
                        if attempt == 3:
                            with requests.get(url, stream=True, proxies=self.proxies, timeout=20) as response:
                                response.raise_for_status()
                                with open(_abs_path, 'wb') as out_file:
                                    for chunk in response.iter_content(chunk_size=1024 * 1024):  # 1MB chunks
                                        out_file.write(chunk)
                        with open(_abs_path, 'wb') as f:
                            res.raw.decode_content = True
                            shutil.copyfileobj(res.raw, f)
                        return 0
                    else:
                        if attempt == 3:
                            res = session.get(url_, stream=True, verify=False, timeout=20)
                            with open(_abs_path, 'wb') as f:
                                res.raw.decode_content = True
                                shutil.copyfileobj(res.raw, f)
                            return 0
                        with session.get(url, stream=True, timeout=20) as response:
                            response.raise_for_status()
                            with open(_abs_path, 'wb') as out_file:
                                for chunk in response.iter_content(chunk_size=1024 * 1024):  # 1MB chunks
                                    out_file.write(chunk)
                            logger.info('Download finished successfully')
                            return 0
                elif pathlib.Path(_abs_path).suffix == '.zip':
                    if 'uralbidin' in url_ or 'utender' in url_:
                        res = session.get(url_, stream=True, verify=False, timeout=20)
                        if attempt == 3:
                            with requests.get(url, stream=True, proxies=self.proxies, timeout=20) as response:
                                response.raise_for_status()
                                with open(_abs_path, 'wb') as out_file:
                                    for chunk in response.iter_content(chunk_size=1024 * 1024):  # 1MB chunks
                                        out_file.write(chunk)
                        with open(_abs_path, 'wb') as f:
                            res.raw.decode_content = True
                            shutil.copyfileobj(res.raw, f)
                    else:
                        res = requests.get(url, stream=True, proxies=self.proxies, verify=False)
                        with open(_abs_path, "wb") as zip_:
                            zip_.write(res.content)
                    # p -> tuple with etp dir and zip's name
                    p = os.path.split(_abs_path)
                    objectZip = ZipFiles(absolute_path=_abs_path, root_directory=p[0], file_name=p[1], trading_id=_id,
                                         lot_number=lot_num,
                                         url=url, relative_path=_relative_path)
                    lst_files = objectZip.extract_files()
                    objectZip.delete_archive()
                    logger.info(f'Download finished successfully ZIP')
                    return lst_files
                elif pathlib.Path(_abs_path).suffix == '.rar':
                    if 'uralbidin' in url_ or 'utender' in url_:
                        if attempt == 3:
                            with requests.get(url, stream=True, proxies=self.proxies, verify=False,
                                              timeout=15) as response:
                                with open(_abs_path, 'wb') as out_file:
                                    response.raw.decode_content = True
                                    shutil.copyfileobj(response.raw, out_file)
                        else:
                            with requests.get(url, stream=True, proxies=self.proxies, verify=False,
                                              timeout=15) as response:
                                response.raise_for_status()
                                with open(_abs_path, 'wb') as out_file:
                                    for chunk in response.iter_content(chunk_size=1024 * 1024):  # 1MB chunks
                                        out_file.write(chunk)
                        # p -> tuple with etp dir and zip's name
                        p = os.path.split(_abs_path)
                        objectRar = RarFiles(absolute_path=_abs_path, root_directory=p[0], file_name=p[1],
                                             trading_id=_id,
                                             lot_number=lot_num,
                                             url=url, relative_path=_relative_path)
                        lst_files = objectRar.extract_files()
                        objectRar.delete_archive()
                        logger.info(f'Download finished successfully Rar')
                        return lst_files
                    else:
                        if attempt == 3:
                            with requests.get(url, stream=True, proxies=self.proxies, verify=False) as response:
                                with open(_abs_path, 'wb') as out_file:
                                    response.raw.decode_content = True
                                    shutil.copyfileobj(response.raw, out_file)
                        else:
                            with requests.get(url, stream=True, proxies=self.proxies) as response:
                                response.raise_for_status()
                                with open(_abs_path, 'wb') as out_file:
                                    for chunk in response.iter_content(chunk_size=1024 * 1024):  # 1MB chunks
                                        out_file.write(chunk)
                        # p -> tuple with etp dir and zip's name
                        p = os.path.split(_abs_path)
                        objectRar = RarFiles(absolute_path=_abs_path, root_directory=p[0], file_name=p[1],
                                             trading_id=_id,
                                             lot_number=lot_num,
                                             url=url, relative_path=_relative_path)
                        lst_files = objectRar.extract_files()
                        objectRar.delete_archive()
                        return lst_files
                elif pathlib.Path(_abs_path).suffix == '.7z':
                    if 'uralbidin' in url_ or 'utender' in url_:
                        res = session.get(url_, stream=True, verify=False, timeout=20)
                    else:
                        res = requests.get(url, stream=True, proxies=self.proxies)
                    with open(_abs_path, "wb") as zip_:
                        zip_.write(res.content)
                    # p -> tuple with etp dir and zip's name
                    p = os.path.split(_abs_path)
                    objectZip = SevenZFiles(
                        absolute_path=_abs_path, root_directory=p[0], file_name=p[1], trading_id=_id,
                        lot_number=lot_num,
                        url=url, relative_path=_relative_path
                    )
                    lst_files = objectZip.extract_zip_files()
                    objectZip.delete_zip()
                    logger.info(f'Download finished successfully 7Z')
                    return lst_files
                return ''
            except Exception as ex:
                if attempt == 5:
                    logger.error(
                        f'Attempt #{attempt} failed with error: {ex} Referer -> {referer}::  :: File name {_abs_path}')
                else:
                    print(f'{ex} :: ERROR lot file -  Attempt - {attempt} - referer - {referer}')

        return ''
