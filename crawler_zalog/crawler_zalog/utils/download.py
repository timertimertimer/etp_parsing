import logging
import shutil
import time
from random import choice

import requests

from general_utils.config import socks_list, headers
from .working_with_url import UrlConfig

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

    def request_to_download_general(self, url, referer, _abs_path, attempts=5, _relative_path=None,
                                    _id=None):
        u = UrlConfig()
        url_ = url
        url_ = u.parse_url(url_)
        session = requests.Session()
        session.headers.update(headers)
        session.proxies.update(self.proxies)
        abs_path = _abs_path
        for attempt in range(1, attempts + 1):
            try:
                session.proxies.update(self.proxies)
                session.headers.update(headers)
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
