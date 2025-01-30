import logging
from random import choice

import requests
import urllib3

from general_utils.config import socks_list, headers
from ..utils.work_with_path_and_dir import GeneralFilesDir
from ..utils.working_with_url import UrlConfig

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
logger = logging.getLogger(__name__)


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
        u = UrlConfig()
        url = u.parse_url(url)
        session = requests.Session()
        session.proxies.update(self.proxies)
        session.headers.update(headers)
        session.headers.update({'Referer': referer})
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
            logger.critical(f'{url}:: REQUEST STATUS CODE - {r.status_code}')
            return None

    def request_to_download(self, url, referer, original_name):
        u = UrlConfig()
        url = u.parse_url(url)
        session = requests.Session()
        session.proxies.update(self.proxies)
        session.headers.update(headers)
        session.headers.update({'Referer': referer})
        res = session.get(url)
        try:
            stop_counter = 0
            while stop_counter < 10:
                if str(res.status_code) in ['200', '302', '301']:
                    break
                else:
                    session.proxies.update(self.proxies)
                    stop_counter += 1
            abs_path = self.general.return_absolute_path()
            with session.get(res.url, stream=True) as r2:
                with open(abs_path + original_name, 'wb') as f:
                    f.write(r2.content)
        except:
            logger.critical(f'{url}:: REQUEST STATUS CODE - {res.status_code}')
            return None
