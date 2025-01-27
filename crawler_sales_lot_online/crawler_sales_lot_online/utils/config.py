from datetime import datetime, timedelta
from os import environ, path
from pathlib import PurePosixPath
from random import choice

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
    _start_date = _date_now + time_delta1
    if time_format is None:
        time_format = "%d.%m.%Y"
    else:
        time_format = time_format
    return _start_date.strftime(time_format)

data_origin_url = 'https://sales.lot-online.ru'
main_page_url = 'https://sales.lot-online.ru/e-auction/mainpage.xhtml'
category_url = 'https://sales.lot-online.ru/e-auction/lots.xhtml'
first_part_url_lot = 'https://sales.lot-online.ru/e-auction/'
url_for_post_download = 'https://sales.lot-online.ru/e-auction/auctionLotProperty.xhtml'
file_param = "?pfdrid_c=true"

# %Y-%m-%d
start_time_from = format_parse_date(1, '%Y-%m-%d')
# format period
# W - week
# D - day
format_period = 'D'
# periods - how many weeks or days been iteration - FREQUENCY (freq)
periods_ = 1
time_delta = 1
table = {

    'table': 'lots_lot_online'
}

headers_brow = {
    "User-Agent": choice(agent_list),
}
Referer = 'https://sales.lot-online.ru/e-auction/mainpage.xhtml'
Referer_lot = 'https://sales.lot-online.ru/e-auction/lots.xhtml'
absolute_path_to_download = f'{set_absolute}/etp_lot_online'
relative_path = f'{set_relative}/etp_lot_online'
lst_exet = ['.jpeg', '.png', '.jpg', '.bmp',
            '.JPG', '.JPEG', 'jpg', 'jpeg', 'JPG', 'JPEG',
            '.docx', '.doc', '.DOC', '.DOXC', '.pdf', '.PDF', '.rar', '.RAR', '.zip', '.ZIP', '.7z', '.7Z',
            '.rtf', '.xlsx',
            '.xls', '.XLS', '.XLSX'
            ]

lst_exet_img = ['.jpeg', '.png', '.jpg', '.bmp',
                '.JPG', '.JPEG', 'jpg', 'jpeg', 'JPG', 'JPEG'
                ]

lst_exet_archive = ['.rar', '.zip', '.7z']

lst_exet_files = ['.jpeg', '.png', '.jpg', '.bmp', '.docx', '.doc', '.pdf',
                  '.JPG', '.JPEG', '.PNG' 'jpg', 'jpeg', 'JPG', 'JPEG', 'PNG', '.PDF', '.DOC', '.DOCX', '.rtf', '.xlsx',
                  '.xls', '.XLS', '.XLSX']
# prime_cookies for download files


prime_cookies = 'primefaces.download=true; '

list_error_link = [
    'https://sales.lot-online.ru/e-auction/auctionLotProperty.xhtml?parm=lotUnid%3D960000318172%3Bmode%3Djust',


    ]
