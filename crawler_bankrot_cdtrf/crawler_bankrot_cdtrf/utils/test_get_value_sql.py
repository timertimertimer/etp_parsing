import asyncio
import logging
import os
import random
import re
import time
from aiohttp_retry import RetryClient
import aiofiles
import aiohttp
import aiosqlite
from aiohttp_socks import ProxyConnector

logging.basicConfig(filename='service_DOWNLOAD_FILES_ASYNC.log', level=logging.ERROR)
#  root_dir -> return home/user_name/


root_dir = '/home/parser'
path_to_file = '/parse_etp/crawler_bankrot_cdtrf/'
full_path_to_sql_file = root_dir + path_to_file
database = 'download_files'
table = 'files_links'
project_dir = os.getcwd()
with open(f'{root_dir}/user_agent_list.txt', 'r') as f:
    lines = f.readlines()
agent_list = [l.replace('\\n', '').strip() for l in lines]

with open(f'{root_dir}/lst_with_proxy_for_download.txt', 'r') as f:
    lines = f.readlines()
socks_lits = [l.replace('\\n', '').strip() for l in lines]

header = {
    'Accept': "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.",
    'Accept-Encoding': 'gzip, deflate, br',
    'Accept-Language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7',
    'Cache-Control': 'no-cach',
    'Connection': 'keep-alive',
    'Host': 'bankrot.cdtrf.ru',
    'Pragma': 'no-cache',
    'Sec-Fetch-Dest': 'document',
    'Sec-Fetch-Mode': 'navigate',
    'Sec-Fetch-Site': 'same-origin',
    'Sec-Fetch-User': '?1',
    'User-Agent': random.choice(agent_list)
}


async def fetch_retry(url):
    header['User-Agent'] = random.choice(agent_list)
    connector = ProxyConnector.from_url(f'socks5://{random.choice(socks_lits)}')
    async with RetryClient() as client:
        async with client.get(url) as response:
            text = await response.content.read()
            return text


async def read_db_table():
    os.chdir(full_path_to_sql_file)
    if database in os.listdir():
        async with aiosqlite.connect(database) as db:
            async with db.execute(f' SELECT link, full_path FROM {table} WHERE status="active" ') as cursor:
                link_and_path = await cursor.fetchall()
                return link_and_path


async def set_value_done():
    os.chdir(full_path_to_sql_file)
    if database in os.listdir():
        async with aiosqlite.connect(database) as db:
            async with db.execute(f' SELECT link, full_path FROM {table} WHERE status="active" ') as cursor:
                link_and_path = await cursor.fetchall()
                for link in link_and_path:
                    await db.execute(f' UPDATE {table} SET status="done" WHERE link="{link[0]}" ')
                await db.commit()


async def write_to_file(text, full_path):
    async with aiofiles.open(full_path, 'wb') as f:
        await f.write(text)


async def fetch(url):
    header['User-Agent'] = random.choice(agent_list)
    connector = ProxyConnector.from_url(f'socks5://{random.choice(socks_lits)}')
    async with aiohttp.ClientSession(headers=header, connector=connector) as session:
        async with session.get(url) as response:
            content_file = await response.content.read()
            return content_file


async def main():
    tasks = []
    link_and_path = await read_db_table()
    if link_and_path:
        for data in link_and_path:
            try:
                text = await fetch(data[0])
                await set_value_done()
            except:
                text = await fetch_retry(data[0])
                await set_value_done()
            tasks.append(write_to_file(text, data[1]))
        await asyncio.gather(*tasks)
    else:
        await asyncio.sleep(10)


if __name__ == '__main__':
    while True:
        time.sleep(2 * 60)
        logging.error(asyncio.run(main()))
