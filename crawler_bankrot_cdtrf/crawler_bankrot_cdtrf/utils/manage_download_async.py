# import pathlib
# import aiohttp
# import asyncio
# import aiofiles
# import aiosqlite
# import os
# import random
# import re
# from aiohttp_socks import ProxyConnector
# from bs4 import BeautifulSoup as BS
# import logging
# from aiohttp_retry import RetryClient
# from crawler_bankrot_cdtrf.utils.work_with_text_and_number import dedent_func
# from crawler_bankrot_cdtrf.utils.working_with_url import UrlConfig
# from crawler_bankrot_cdtrf.utils.work_with_path_and_dir import GeneralFilesDir
# from crawler_bankrot_cdtrf.utils.config import lst_exet, data_origin_url
#
# logger = logging.getLogger(__name__)
#
# statuses = {x for x in range(100, 600)}
# statuses.remove(200)
#
# project_dir = os.getcwd()
# with open(f'{project_dir}/crawler_bankrot_cdtrf/utils/user-agent.txt', 'r') as f:
#     lines = f.readlines()
# new_lits = [l.replace('\\n', '').strip() for l in lines]
# with open(f'{project_dir}/crawler_bankrot_cdtrf/utils/socks_5.txt', 'r') as f:
#     lines = f.readlines()
# socks_lits = [l.replace('\\n', '').strip() for l in lines]
#
# header = {
#     'Accept': "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.",
#     'Accept-Encoding': 'gzip, deflate, br',
#     'Accept-Language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7',
#     'Cache-Control': 'no-cach',
#     'Connection': 'keep-alive',
#     'Host': 'bankrot.cdtrf.ru',
#     'Pragma': 'no-cache',
#     'Sec-Fetch-Dest': 'document',
#     'Sec-Fetch-Mode': 'navigate',
#     'Sec-Fetch-Site': 'same-origin',
#     'Sec-Fetch-User': '?1',
#     'User-Agent': random.choice(new_lits)
# }
#
# _dir = GeneralFilesDir()
# _url = UrlConfig()
# # async def fetch_retry(url, referer=None):
# #     headers = await get_headers(url)
# #     headers['User-Agent'] = random.choice(agent_list)
# #     connector = ProxyConnector.from_url(f'socks5://{random.choice(socks_lits)}')
# #     retry_options = RetryOptions(attempts=10, statuses=statuses, max_timeout=5.0, exceptions={ValueError, Exception, ConnectionError})
# #     retry_client = RetryClient(raise_for_status=True, retry_options=retry_options, headers=headers,
# #                                connector=connector)
# #     async with retry_client.get(url) as response:
# #         text = await response.text()
# #         # await write_to_file('text', text)
# #         await retry_client.close()
# #         print(text)
# #         return text
# #         # logger.error(f'Referer {referer} :: URL {url} ERROR REQUEST', exc_info=True)
# #
# # async def fetch_retry_download(url, referer=None):
# #     headers = await get_headers(url)
# #     headers['User-Agent'] = random.choice(agent_list)
# #     connector = ProxyConnector.from_url(f'socks5://{random.choice(socks_lits)}')
# #     retry_options = RetryOptions(attempts=10, statuses=statuses, max_timeout=5.0)
# #     retry_client = RetryClient(raise_for_status=False, retry_options=retry_options, headers=headers,
# #                                connector=connector)
# #     async with retry_client.get(url) as response:
# #         text = await response.content.read()
# #         await retry_client.close()
# #
# #
# #         return text
# #
# #
# # async def write_to_file(file, text):
# #     async with aiofiles.open(file, 'a') as f:
# #         await f.write(text)
#
# async def fetch_retry(url):
#     header['User-Agent'] = random.choice(new_lits)
#     connector = ProxyConnector.from_url(f'socks5://{random.choice(socks_lits)}')
#     async with RetryClient() as client:
#         async with client.get(url) as response:
#             text = await response.text()
#             return text
#             # soup = BS(text, 'lxml')
#             # link = soup.find_all('a', {'href': re.compile(r'undef/card/download.aspx\?fileid.+0')})
#             # try:
#             #     return link
#             # except Exception as e:
#             #     logger.error(f'{url} :: ERROR GETTING LIST WITH HREF FILE\n{e}')
#
#
# async def fetch(url) -> list:
#     header['User-Agent'] = random.choice(new_lits)
#     connector = ProxyConnector.from_url(f'socks5://{random.choice(socks_lits)}')
#     async with aiohttp.ClientSession(headers=header, connector=connector) as session:
#         async with session.get(url) as response:
#             try:
#                 text = await response.text()
#             except:
#                 text = await fetch_retry(url)
#             soup = BS(text, 'lxml')
#             link = soup.find_all('a', {'href': re.compile(r'undef/card/download.aspx\?fileid.+0')})
#             try:
#                 return link
#             except Exception as e:
#                 logger.error(f'{url} :: ERROR GETTING LIST WITH HREF FILE\n{e}')
#
#
# async def write_to_file(file, text):
#     async with aiofiles.open(file, 'w') as f:
#         await f.write(text)
#
#
# # async def add_to_db(file_name, _path, link, status='active'):
# #     table = 'files_links'
# #     async with aiosqlite.connect('download_files') as db:
# #         await db.execute(f"""CREATE TABLE IF NOT EXISTS {table} (
# #             name TEXT,
# #             link TEXT,
# #             full_path TEXT,
# #             status TEXT
# #
# #         )""")
# #         await db.commit()
# #         cursor = await db.execute(f' SELECT link FROM {table} WHERE link = "{link}" ')
# #         row = await cursor.fetchone()
# #         if row is None:
# #             await asyncio.sleep(0.01)
# #             async with db.execute(f" INSERT INTO {table} VALUES (?, ?, ?, ?) ", (file_name, link, _path, status)):
# #                 await db.commit()
#
#
# async def main(_urls, file_id, referer):
#     if _urls:
#         lst = list()
#         tasks = []
#         for url in _urls:
#             await asyncio.sleep(0.01)
#             try:
#                 links = await fetch(url)
#             except Exception as e:
#                 # links = await fetch(url)
#                 logger.error(f'{referer} :: FILE WAS NOT ADD TO DATA BASE {e}')
#                 return None
#             for link in links:
#                 await asyncio.sleep(0.01)
#                 link = BS(str(link), features='lxml')
#                 text_link = link.get_text()
#                 name_on_server = _dir.name_file_on_server(file_id, text_link)
#                 if len(name_on_server) > 72:
#                     name_on_server = name_on_server[-45:-1:1]
#                 link_file = re.sub(r'\s', '', dedent_func(link.find('a').get('href')))
#                 link_file = _url.parse_url(_url.url_join(data_origin_url, link_file))
#                 path_on_server = ''
#                 if pathlib.Path(text_link.replace(' ', '')).suffix in lst_exet:
#                     _dir.create_dir()
#                     path_on_server = _dir.name_in_column_files(name_on_server)
#                     tasks.append(add_to_db(text_link, _dir.return_absolute_path(name_on_server), link_file))
#                 lst.append({'original_name': text_link,
#                             'link': path_on_server,
#                             'link_etp': link_file})
#
#         await asyncio.gather(*tasks)
#         return lst
#
# # urls = MAIN_LST
