import requests
import urllib.request
import urllib.parse
from .manage import return_absolute_path
from .config import *
from random import choice
import logging
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
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

    session = requests.Session()
    session.headers = {
        "User-Agent": choice(agent_list)
    }

    headers_brow = choice(agent_list)

    def requests_to_url(self, url):
        url = urllib.parse.urlparse(url)
        url = url.scheme + '://' + url.netloc + urllib.parse.quote(url.path)
        self.session.proxies.update(self.proxies)
        response = self.session.get(url)
        stop_counter = 0
        try:
            while stop_counter < 10:
                if str(response.status_code) == '200':
                    break
                else:
                    self.session.proxies.update(self.proxies)
                    response = self.session.get(url)
                    stop_counter += 1
        except Exception as e:
            logger.error(f'CONNECTION ERROR {url} - {e}')
        return response.text

    def request_for_download(self, url, original_name, attempts=5):
        if ' ' in url:
            url = urllib.parse.urlparse(url)
            url = url.scheme + '://' + url.netloc + urllib.parse.quote(url.path)
        for attempt in range(1, attempts + 1):
            self.session.proxies.update(self.proxies)
            try:
                with self.session.get(url, stream=True) as r:
                    abs_path = return_absolute_path()
                    with open(abs_path + '/' + original_name, 'wb') as f:
                        for chunk in r.iter_content(chunk_size=1024):
                            f.write(chunk)
            except Exception as e:
                if attempt == 5:
                    logger.error(f'{url} ::ERROR - problem with downloading file - {original_name}\n{e}')
