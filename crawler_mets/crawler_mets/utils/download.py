import requests

from .config import path_user_agent, path_to_socks5
from ..utils.work_with_path_and_dir import GeneralFilesDir
from random import choice
import logging
from ..utils.working_with_url import UrlConfig
import shutil
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
logger = logging.getLogger(__name__)
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

        'User-Agent': choice(agent_list)}

    def make_request(self, url, referer):
        u = UrlConfig()
        url = u.parse_url(url)
        session = requests.Session()
        session.proxies.update(self.proxies)
        session.headers.update(self.headers_)
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

    def request_to_download(self, url, referer, original_name):
        u = UrlConfig()
        url = url
        # url = u.parse_url(url)
        session = requests.Session()
        session.proxies.update(self.proxies)
        session.headers.update(self.headers_)
        # session.headers.update({'Referer': referer})
        res = None
        stop_counter = 0
        while stop_counter < 10:
            try:
                res = session.get(url, stream=True)
                if str(res.status_code) in ['200', '302', '301']:
                    break
                if stop_counter == 10:
                    break
                stop_counter += 1
                session.proxies.update(self.proxies)
            except ConnectionError as e:
                stop_counter += 1
                logger.error(f'{e}')
                continue
        abs_path = self.general.return_absolute_path()
        if str(res.status_code) in ['200', '302', '301']:
            try:
                with open(abs_path + original_name, 'wb') as f:
                    res.raw.decode_content = True
                    shutil.copyfileobj(res.raw, f)
            except Exception as e:
                logger.critical(f'{url}:: REQUEST STATUS CODE - {res.status_code}:: {e}')
                return None
