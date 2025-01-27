import logging
import time
from random import choice

import requests
import urllib3

from general_utils import UrlConfig
from general_utils.config import socks_list
from ..utils.work_with_path_and_dir import GeneralFilesDir

logger = logging.getLogger(__name__)
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


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

    def make_request(self, url, referer):
        url = UrlConfig.parse_url(url)
        session = requests.Session()
        session.proxies.update(self.proxies)
        # session.headers.update(self.headers_)
        # session.headers.update({'Referer': referer})
        try:
            with session.get(url, allow_redirects=False) as r:
                stop_counter = 0
                while stop_counter < 10:
                    if str(r.status_code) in ['200', '302', '301']:
                        return r.text
                    else:
                        session.proxies.update(self.proxies)
                        stop_counter += 1
                        r = session.head(url, allow_redirects=False)
        except:
            logger.error(f'{url}:: REQUEST STATUS CODE - {r.status_code}')
            return None

    def request_to_download(self, url, referer, original_name):
        u = UrlConfig()
        url = u.parse_url(url)
        session = requests.Session()
        session.proxies.update(self.proxies)
        res = None
        stop_counter = 0
        while stop_counter < 10:
            try:
                res = session.get(url)
                if str(res.status_code) in ['200', '302', '301']:
                    break
                if stop_counter == 10:
                    break
                stop_counter += 1
                time.sleep(0.5)
                session.proxies.update(self.proxies)
            except ConnectionError as e:
                stop_counter += 1
                logger.error(f'{e}')
                continue
        abs_path = self.general.return_absolute_path()
        if res:
            try:
                with session.get(res.url, stream=True) as r2:
                    with open(abs_path + original_name, 'wb') as f:
                        f.write(r2.content)
            except Exception as e:
                logger.critical(f'{url}:: REQUEST STATUS CODE - {res.status_code}:: {e}')
                return None
