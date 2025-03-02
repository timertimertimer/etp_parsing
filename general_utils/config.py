from datetime import datetime, timedelta
from pathlib import PurePath
from random import choice

project_main_dir = PurePath(__file__).parent.parent

absolute_download_path = project_main_dir / 'set_main_path_to_download'
relative_download_path = project_main_dir / 'set_relative_path_to_download'

with open(f'{absolute_download_path}', 'r') as f:
    absolute_download_path = PurePath(''.join(f.readlines()).strip().replace('\n', ''))
with open(f'{relative_download_path}', 'r') as f:
    relative_download_path = PurePath(''.join(f.readlines()).strip().replace('\n', ''))

data_path = project_main_dir / 'data'
config_file = 'config.ini'
config_path = data_path / config_file
proxy_file = 'proxy.txt'
socks_file = 'socks_5.txt'
user_agent = 'user-agent.txt'
api_keys = 'api_keys.json'
indexes = 'index.json'
create_tables_queries = 'create_tables.sql'
path_to_proxy = data_path / proxy_file
path_to_socks5 = data_path / socks_file
path_user_agent = data_path / user_agent
api_key_path = data_path / api_keys
indexes_path = data_path / indexes
create_tables_queries_path = data_path / create_tables_queries
with open(f'{path_user_agent}', 'r') as f:
    lines = f.readlines()
agent_list = [i.replace('\\n', '').strip() for i in lines]

with open(f'{path_to_socks5}', 'r') as f:
    lines = f.readlines()
socks_list = [i.replace('\\n', '').strip() for i in lines]


def format_parse_date(days_: int, time_format=None):
    time_delta1 = timedelta(days=days_)
    _date_now = datetime.now()
    _start_date = _date_now - time_delta1
    if time_format is None:
        time_format = "%d.%m.%Y"
    else:
        time_format = time_format
    return _start_date.strftime(time_format)


start_date = format_parse_date(30)

headers = {
    'Accept': '*/*',
    'Accept-Encoding': 'gzip, deflate, br, zstd',
    'Accept-Language': 'ru-RU,ru;q=0.9',
    'Cache-Control': 'no-cache',
    'Connection': 'keep-alive',
    'DNT': '1',
    'Pragma': 'no-cache',
    'Sec-Fetch-Dest': 'document',
    'Sec-Fetch-Mode': 'navigate',
    'Sec-Fetch-Site': 'same-origin',
    'Sec-Fetch-User': '?1',
    'Upgrade-Insecure-Request': '1',
    'User-Agent': choice(agent_list)
}

lst_exet = [
    '.jpeg', '.png', '.jpg', '.bmp',
    '.JPG', '.JPEG', 'jpg', 'jpeg', 'JPG', 'JPEG'
]
lst_exet_files = [
    '.jpeg', '.png', '.jpg', '.bmp', '.docx', '.doc', '.pdf',
    '.JPG', '.JPEG', '.PNG' 'jpg', 'jpeg', 'JPG', 'JPEG', '.PNG', '.PDF', '.DOC', '.DOCX'
]
lst_exet_archive = ['.rar', '.zip', '.7z', '.RAR', '.ZIP', '.7Z', '.Rar', '.Zip']
lst_exeption = [
    'reshenie', 'protocol', 'протокол', 'решение',
    'Reshenie', 'Protocol', 'Протокол', 'Решение', 'ПРОТОКОЛ'
]
trash_resources = ["image", 'stylesheet', 'audio', 'font', 'xhr', 'fetch', 'eventsource', 'websocket', 'media', 'ping']
