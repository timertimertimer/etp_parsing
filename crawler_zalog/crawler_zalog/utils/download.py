import logging
import shutil
import time
from random import choice

import requests

from .working_with_url import UrlConfig
from ..utils.config import path_to_socks5, path_user_agent

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
        'Host': 'zalog.lot-online.ru',
        'Pragma': 'no-cache',
        'Sec-Fetch-Dest': 'document',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-Site': 'same-origin',
        'Sec-Fetch-User': '?1',
        'User-Agent': choice(agent_list)
    }

    def request_to_download_general(self, url, referer, _abs_path, attempts=5, _relative_path=None,
                                    _id=None):
        u = UrlConfig()
        url_ = url
        url_ = u.parse_url(url_)
        session = requests.Session()
        session.headers.update(self.headers)
        session.proxies.update(self.proxies)
        abs_path = _abs_path
        for attempt in range(1, attempts + 1):
            try:
                session.proxies.update(self.proxies)
                session.headers.update(self.headers)
                if attempt > 1:
                    time.sleep(2)  # 2 seconds wait time between downloads
                time.sleep(0.05)
                with session.get(url_, stream=True, timeout=10) as response:
                    if response.status_code != 404:
                        with open(abs_path, 'wb') as out_file:
                            response.raw.decode_content = True
                            shutil.copyfileobj(response.raw, out_file)

                        # logger.info(f'Download finished successfully')
                        return 0
                    else:
                        return -1
            except Exception as ex:
                if attempt == 5:
                    logger.error(f'Attempt #{attempt} failed with error: {ex} Referer - {referer}')
        return -1
