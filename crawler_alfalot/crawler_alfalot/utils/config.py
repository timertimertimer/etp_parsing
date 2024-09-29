from datetime import datetime, timedelta
from os import environ, path
from pathlib import PurePosixPath
from scrapy.utils.conf import closest_scrapy_cfg

proj_root = closest_scrapy_cfg()
home_dir = environ['HOME']
project_main_dir = PurePosixPath(proj_root).parent.parent.name + '/'
proxy_file = 'proxy_all.txt'
socks_file = 'socks_5.txt'
user_agent = 'user-agent.txt'

set_absolute_path = path.join(home_dir, project_main_dir) + 'set_main_path_to_download'
set_relative_path = path.join(home_dir, project_main_dir) + 'set_relative_path_to_download'

with open(f'{set_absolute_path}', 'r') as f:
    set_absolute = ''.join(f.readlines()).strip().replace('\n', '')
with open(f'{set_relative_path}', 'r') as f:
    set_relative = ''.join(f.readlines()).strip().replace('\n', '')

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
        time_format = "%Y-%-m-%-d"
    else:
        time_format = time_format
    return _start_date.strftime(time_format)


tables = {
    'table_alfalot': 'lots_alfalot',
}

start_time = '0:0:-1'
start_date = format_parse_date(1)
start_date_post = ' '.join([start_date, start_time])

data_origin = {
    'alfalot': 'https://bankrupt.alfalot.ru/',
}


def return_auction_link(_data_origin):
    auction_link = 'public/auctions-all/'
    return _data_origin + auction_link


def return_offer_link(_data_origin):
    offer_link = 'public/public-offers-all/'
    return _data_origin + offer_link


def return_compet_link(_data_origin):
    competition_link = 'public/contests-all/'
    return _data_origin + competition_link


path_absolute = {
    'alfalot': f'{set_absolute}/etp_alfalot',
}

path_relative = {
    'alfalot': f'{set_relative}/etp_alfalot',
}

lst_exet = ['.jpeg', '.png', '.jpg', '.bmp',
            '.JPG', '.JPEG', '.PNG' 'jpg', 'jpeg', 'JPG', 'JPEG', 'PNG']

lst_exet_archive = ['.rar', '.zip', '.7z', '.RAR', '.ZIP', '.7Z', '.Rar', '.Zip']

lst_exet_files = ['.jpeg', '.png', '.jpg', '.bmp', '.docx', '.doc', '.pdf',
                  '.JPG', '.JPEG', '.PNG' 'jpg', 'jpeg', 'JPG', 'JPEG', 'PNG', '.PDF', '.DOC', '.DOCX']
