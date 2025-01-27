import requests
import urllib.request
import urllib.parse

from general_utils.config import socks_list, headers
from .manage import return_absolute_path
from random import choice
import logging
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
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

    session = requests.Session()
    session.headers = headers

    def requests_to_url(self, url):
        if ' ' in url:
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
        except:
            logger.error(f'CONNECTION ERROR {url}')
        return response.text

    def request_for_download(self, url, original_name):
        if ' ' in url:
            url = urllib.parse.urlparse(url)
            url = url.scheme + '://' + url.netloc + urllib.parse.quote(url.path)
        self.session.proxies.update(self.proxies)
        try:
            with self.session.get(url, stream=True) as r:
                stop_counter = 0
                while stop_counter < 10:
                    if str(r.status_code) == '200':
                        break
                    else:
                        self.session.proxies.update(self.proxies)
                        stop_counter += 1
                        r = self.session.get(url, stream=True)
                abs_path = return_absolute_path()
                with open(abs_path + '/' + original_name, 'wb') as f:
                    for chunk in r.iter_content(chunk_size=1024):
                        f.write(chunk)
        except Exception as e:
            logger.error(f'FILE WASN\'T DOWNLOAD {url}::: {e}')
