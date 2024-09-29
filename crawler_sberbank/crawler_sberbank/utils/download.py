import logging
import os
import time
from random import choice

import requests
import urllib3

from .config import path_user_agent, path_to_socks5
from ..utils.work_with_path_and_dir import GeneralFilesDir
from ..utils.working_with_url import UrlConfig

logger = logging.getLogger(__name__)
project_dir = os.getcwd()

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
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
    headers_ = {
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        'accept-encoding': 'gzip, deflate, br',
        'accept-language': 'en-US,en;q=0.9,ru-RU;q=0.8,ru;q=0.7,de-DE;q=0.6,de;q=0.5,uk-UA;q=0.4,uk;q=0.3,ro-RO;q=0.2,ro;q=0.1',
        'cache-control': 'no-cache',
        'connection': 'keep-alive',
        'dnt': '1',
        'pragma': 'no-cache',
        'User-Agent': choice(agent_list)}

    def make_request(self, url, referer):
        u = UrlConfig()
        url = u.parse_url(url)
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
        # session.headers.update(self.headers_)
        # session.headers.update({'Referer': referer})
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
