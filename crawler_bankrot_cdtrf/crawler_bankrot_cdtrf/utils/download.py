import asyncio
import logging
import pathlib
import random
import re

import aiofiles
import aiohttp
import urllib3
from aiohttp_retry import RetryClient, RetryOptions
from aiohttp_socks import ProxyConnector
from bs4 import BeautifulSoup as BS

from general_utils.config import socks_list, headers, agent_list, lst_exet
from ..utils.config import data_origin_url
from ..utils.work_with_path_and_dir import GeneralFilesDir
from ..utils.work_with_text_and_number import dedent_func
from ..utils.working_with_url import UrlConfig

logger = logging.getLogger(__name__)

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

_dir = GeneralFilesDir()
_url = UrlConfig()
statuses = {x for x in range(100, 600)}
statuses.remove(200)


async def fetch(url) -> list or None:
    connector = ProxyConnector.from_url(f'socks5://{random.choice(socks_list)}')
    async with aiohttp.ClientSession(headers=headers, connector=connector) as session:
        async with session.get(url) as response:
            try:
                text = await response.text()
                soup = BS(text, 'lxml')
                link = soup.find_all('a', {'href': re.compile(r'undef/card/download.aspx\?fileid.+0')})
                return link
            except:
                return None


async def fetch_retry(url, referer=None):
    connector = ProxyConnector.from_url(f'socks5://{random.choice(socks_list)}')
    retry_options = RetryOptions(attempts=10, statuses=statuses, max_timeout=5.0,
                                 exceptions={ValueError, Exception, ConnectionError})
    retry_client = RetryClient(raise_for_status=True, retry_options=retry_options, headers=headers,
                               connector=connector)
    async with retry_client.get(url) as response:
        try:
            text = await response.text()
            soup = BS(text, 'lxml')
            link = soup.find_all('a', {'href': re.compile(r'undef/card/download.aspx\?fileid.+0')})
        except:
            logger.error(f'{url}:: ERROR FILE referer - {referer}')
        finally:
            await retry_client.close()
            return link
        # logger.error(f'Referer {referer} :: URL {url} ERROR REQUEST', exc_info=True)


async def fetch_retry_download(url, referer=None):
    headers['User-Agent'] = random.choice(agent_list)
    connector = ProxyConnector.from_url(f'socks5://{random.choice(socks_list)}')
    retry_options = RetryOptions(attempts=10, statuses=statuses, max_timeout=4.0)
    retry_client = RetryClient(raise_for_status=False, retry_options=retry_options, headers=headers,
                               connector=connector)
    async with retry_client.get(url) as response:
        try:
            text = await response.content.read()
        finally:
            await retry_client.close()
        return text

async def fetchdownload(url, referer=None):
    headers['User-Agent'] = random.choice(agent_list)
    connector = ProxyConnector.from_url(f'socks5://{random.choice(socks_list)}')
    async with aiohttp.ClientSession(headers=headers, connector=connector) as session:
        async with session.get(url) as response:
            content_file = await response.content.read()
            try:
                return content_file
            except:
                return None

async def write_to_file(file, text):
    async with aiofiles.open(file, 'wb') as f:
        await f.write(text)


async def main(_urls, file_id, referer):
    if _urls:
        lst = list()
        tasks = []
        for url in _urls:
            try:
                # get files links for download
                links = await fetch(url)
            except:
                links = None
            try:
                if links is None:
                    links = await fetch_retry(url)
            except:
                logger.error(f'{referer} :: INVALID REQUEST TO FILE PAGE')
            # itterate throught link's list
            if links:
                for link in links:
                    link = BS(str(link), features='lxml')
                    text_link = link.get_text()
                    name_on_server = _dir.name_file_on_server(file_id, text_link)
                    if len(name_on_server) > 72:
                        name_on_server = name_on_server[-45:-1:1]
                    link_file = re.sub(r'\s', '', dedent_func(link.find('a').get('href')))
                    link_file = _url.parse_url(_url.url_join(data_origin_url, link_file))
                    # do request and get byte content of file
                    try:
                        content_byte = await fetch_retry_download(link_file, referer)
                    except:
                        content_byte = None
                    try:
                        if content_byte is None:
                            content_byte = await fetchdownload(link_file, referer)
                    except:
                        logger.error(f'{referer}, content byte file wasn\'t download')
                        content_byte = None
                    path_on_server = ''
                    if pathlib.Path(text_link.replace(' ', '')).suffix in lst_exet:
                        _dir.create_dir()
                        path_on_server = _dir.name_in_column_files(name_on_server)
                        if content_byte:
                            tasks.append(write_to_file(_dir.return_absolute_path(name_on_server), content_byte))
                    lst.append({'original_name': text_link,
                                'link': path_on_server,
                                'link_etp': link_file})
        await asyncio.gather(*tasks)
        return lst
