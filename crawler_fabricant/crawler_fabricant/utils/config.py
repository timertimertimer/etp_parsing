from random import choice
from datetime import datetime, timedelta
from os import environ, path
from pathlib import PurePosixPath
from random import choice

from scrapy.utils.conf import closest_scrapy_cfg

main_url = 'http://www.selt-online.ru/'
url_main_pagination = 'http://bankruptcy.selt-online.ru/?page={}&ascending=False'
host_url = 'http://bankruptcy.selt-online.ru'
start_page = 1
stop_page = 5

proj_root = closest_scrapy_cfg()
home_dir = environ['HOME']
project_main_dir = PurePosixPath(proj_root).parent.parent.name + '/'

set_absolute_path = path.join(home_dir, project_main_dir) + 'set_main_path_to_download'
set_relative_path = path.join(home_dir, project_main_dir) + 'set_relative_path_to_download'

with open(f'{set_absolute_path}', 'r') as f:
    set_absolute = ''.join(f.readlines()).strip().replace('\n', '')
with open(f'{set_relative_path}', 'r') as f:
    set_relative = ''.join(f.readlines()).strip().replace('\n', '')

proxy_file = 'proxy_all.txt'
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


data_origin_url = 'https://www.fabrikant.ru'
main_url = 'https://www.fabrikant.ru/trades/procedure/search'
start_url = 'https://www.fabrikant.ru/trades/procedure/search/?filter_id=6'
# %Y-%m-%d
start_time_from = format_parse_date(2, time_format="%Y.%m.%d")
periods_ = 1
time_delta = 3
table = {

    'table': 'lots_fabricant'

}

headers_brow = {
    "User-Agent": choice(agent_list),
}
Referer = 'https://www.fabrikant.ru/trades/procedure/search/?filter_id=6'
absolute_path_to_download = f'{set_absolute}/etp_fabricant'
relative_path =  f'{set_relative}/etp_fabricant'
lst_exet = ['.jpeg', '.png', '.jpg', '.bmp', '.JPG', '.JPEG', 'jpg', 'jpeg', 'JPG', 'JPEG']
