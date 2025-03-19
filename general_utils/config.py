import csv
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

config_file_name = 'config.ini'
proxy_file_name = 'proxy.txt'
socks_file_name = 'socks_5.txt'
user_agent_file_name = 'user-agent.txt'
api_keys_file_name = 'api_keys.json'
indexes_file_name = 'index.json'
lot_classifiers_file_name = 'lot_classifiers.csv'
data_path = project_main_dir / 'data'
config_path = data_path / config_file_name
proxy_path = data_path / proxy_file_name
socks5_proxy_path = data_path / socks_file_name
user_agent_path = data_path / user_agent_file_name
api_key_path = data_path / api_keys_file_name
indexes_path = data_path / indexes_file_name
lot_classifiers_path = data_path / lot_classifiers_file_name
with open(f'{user_agent_path}', 'r') as f:
    lines = f.readlines()
user_agents = [i.replace('\\n', '').strip() for i in lines]

with open(f'{socks5_proxy_path}', 'r') as f:
    lines = f.readlines()
socks5_proxies = [i.replace('\\n', '').strip() for i in lines]

lot_classifiers_name_to_code = dict()
lot_classifiers_code_to_name = dict()
with open(f'{lot_classifiers_path}', 'r', encoding='utf-8-sig') as f:
    reader: csv.DictReader = csv.DictReader(f, delimiter=';')
    for row in reader:
        lot_classifiers_code_to_name[row['Код']] = row['Наименование']
        lot_classifiers_name_to_code[row['Наименование']] = row['Код']


def format_parse_date(days_: int, time_format=None):
    time_delta1 = timedelta(days=days_)
    _date_now = datetime.now()
    _start_date = _date_now - time_delta1
    if time_format is None:
        time_format = "%d.%m.%Y"
    else:
        time_format = time_format
    return _start_date.strftime(time_format)


days = 30
start_date = format_parse_date(days)

headers = {
    'Accept': '*/*',
    'Accept-Encoding': 'gzip, deflate, br, zstd',
    'Accept-Language': 'ru-RU,ru;q=0.9',
    'Cache-Control': 'no-cache',
    'Connection': 'keep-alive',
    # 'DNT': '1',
    'Pragma': 'no-cache',
    'Sec-Fetch-Dest': 'document',
    'Sec-Fetch-Mode': 'navigate',
    'Sec-Fetch-Site': 'same-origin',
    'Sec-Fetch-User': '?1',
    'Upgrade-Insecure-Request': '1',
    'User-Agent': choice(user_agents)
}

image_formats = [
    '.jpeg', '.png', '.jpg', '.bmp',
    '.JPG', '.JPEG', 'jpg', 'jpeg', 'JPG', 'JPEG', '.PNG'
]
image_and_doc_formats = image_formats + [
    '.docx', '.doc', '.pdf', '.rtf',
    '.PDF', '.DOC', '.DOCX', '.RTF'
]
archive_formats = ['.rar', '.zip', '.7z', '.RAR', '.ZIP', '.7Z', '.Rar', '.Zip']
allowable_formats = image_and_doc_formats + archive_formats
trash_resources = ["image", 'stylesheet', 'audio', 'font', 'xhr', 'fetch', 'eventsource', 'websocket', 'media', 'ping']

download_files_from_get_url = True
write_log_to_file = True
