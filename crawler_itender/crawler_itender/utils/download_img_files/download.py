import asyncio
import random
import logging
from aiohttp_retry import RetryClient, RetryOptions
from aiohttp_socks import ProxyConnector
import aiofiles

from crawler_itender.utils.config import path_user_agent, path_to_socks5
from crawler_itender.utils.headers_for_spiders.return_current_headers import recognize_etp

logger = logging.getLogger(__name__)


with open(f'{path_user_agent}', 'r') as f:
    lines = f.readlines()
agent_list = [i.replace('\\n', '').strip() for i in lines]

with open(f'{path_to_socks5}', 'r') as f:
    lines = f.readlines()
socks_list = [i.replace('\\n', '').strip() for i in lines]

statuses = {x for x in range(100, 600)}
# statuses.remove(200)
statuses.remove(302)
statuses.remove(303)
if len(socks_list) > 0 and socks_list[0] != '':
    proxies = {
        'http': 'socks5://' + random.choice(socks_list),
        'https': 'socks5://' + random.choice(socks_list)

    }
else:
    proxies = {
        "http": '',
        "https": '',
    }

async def get_headers(url):
    headers = [v for k, v in recognize_etp.items() if k in url]
    if len(headers) > 0:
        return headers[0]


async def fetch_retry(url, referer=None):
    headers = await get_headers(url)
    headers['User-Agent'] = random.choice(agent_list)
    connector = ProxyConnector.from_url(f'socks5://{random.choice(socks_list)}')
    retry_options = RetryOptions(attempts=10, statuses=statuses, max_timeout=5.0, exceptions={ValueError, Exception, ConnectionError})
    retry_client = RetryClient(raise_for_status=True, retry_options=retry_options, headers=headers,
                               connector=connector)
    async with retry_client.get(url) as response:
        text = await response.text()
        # await write_to_file('text', text)
        await retry_client.close()
        print(text)
        return text
        # logger.error(f'Referer {referer} :: URL {url} ERROR REQUEST', exc_info=True)

async def fetch_retry_download(url, referer=None):
    headers = await get_headers(url)
    headers['User-Agent'] = random.choice(agent_list)
    connector = ProxyConnector.from_url(f'socks5://{random.choice(socks_list)}')
    retry_options = RetryOptions(attempts=10, statuses=statuses, max_timeout=5.0)
    retry_client = RetryClient(raise_for_status=False, retry_options=retry_options, headers=headers,
                               connector=connector)
    async with retry_client.get(url) as response:
        text = await response.content.read()
        await retry_client.close()


        return text


async def write_to_file(file, text):
    async with aiofiles.open(file, 'a') as f:
        await f.write(text)


asyncio.run(fetch_retry('https://httpbin.org/ip'))
