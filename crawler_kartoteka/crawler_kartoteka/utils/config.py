from datetime import datetime, timedelta
from os import environ, path
from pathlib import PurePosixPath
from random import choice

from scrapy.utils.conf import closest_scrapy_cfg

proj_root = closest_scrapy_cfg()
home_dir = environ['HOME']
project_main_dir = PurePosixPath(proj_root).parent.parent.name + '/'

set_absolute_path = path.join(home_dir, project_main_dir) + 'set_main_path_to_download'
set_relative_path = path.join(home_dir, project_main_dir) + 'set_relative_path_to_download'

with open(f'{set_absolute_path}', 'r') as f:
    set_absolute = ''.join(f.readlines()).strip().replace('\n', '')
with open(f'{set_relative_path}', 'r') as f:
    set_relative = ''.join(f.readlines()).strip().replace('\n', '')

proxy_file = 'proxy.txt'
socks_file = 'socks_5.txt'
user_agent = 'user-agent.txt'
path_to_proxy = path.join(home_dir, project_main_dir) + proxy_file
path_to_socks5 = path.join(home_dir, project_main_dir) + socks_file
path_user_agent = path.join(home_dir, project_main_dir) + user_agent
with open(f'{path_user_agent}', 'r') as f:
    lines = f.readlines()
agent_list = [i.replace('\\n', '').strip() for i in lines]


def format_parse_date(days_: int, time_format=None):
    time_delta1 = timedelta(days=days_)
    _date_now = datetime.now()
    _start_date = _date_now - time_delta1
    if time_format is None:
        time_format = "%d.%m.%Y"
    else:
        time_format = time_format
    return _start_date.strftime(time_format)


data_origin_url = 'https://www.kartoteka.ru/'
main_url = 'https://www.kartoteka.ru/bankruptcy2'
time_delta = 7
start_time_from = format_parse_date(time_delta)
connect_db = {
    'table': 'lots_kartoteka'
}

headers_brow = {
    "User-Agent": choice(agent_list),
}
path_absolute = f'{set_absolute}/etp_kartoteka'
path_relative = f'{set_relative}/etp_kartoteka'
lst_exet = ['.jpeg', '.png', '.jpg', '.bmp',
            '.JPG', '.JPEG', 'jpg', 'jpeg', 'JPG', 'JPEG']
lst_exet_files = ['.jpeg', '.png', '.jpg', '.bmp', '.docx', '.doc', '.pdf',
                  '.JPG', '.JPEG', '.PNG' 'jpg', 'jpeg', 'JPG', 'JPEG', '.PNG', '.PDF', '.DOC', '.DOCX']

lst_exet_archive = ['.rar', '.zip', '.7z', '.RAR', '.ZIP', '.7Z', '.Rar', '.Zip']
lst_exeption = ['reshenie', 'protocol', 'Reshenie', 'Protocol', 'Протокол', 'протокол', 'Решение', 'решение',
                'ПРОТОКОЛ']

trash_resources = ["image", 'stylesheet', 'audio', 'font', 'xhr', 'fetch', 'eventsource', 'websocket', 'media', 'ping']