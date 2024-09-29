from datetime import datetime, timedelta
from os import environ, path
from pathlib import PurePosixPath
from random import choice

from scrapy.utils.conf import closest_scrapy_cfg

referer = 'https://m-ets.ru/search'

data_origin_url = 'https://m-ets.ru/'
url_start = 'https://m-ets.ru/search'

proj_root = closest_scrapy_cfg()
home_dir = environ['HOME']
project_main_dir = PurePosixPath(proj_root).parent.parent.name + '/'
proxy_file = 'proxy.txt'
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
bot_name = 'sistematorg'
allowed_domain = 'sistematorg.com'
main_url = ['https://sistematorg.com']
main_url_list = 'https://sistematorg.com/tradelist.php?trade_number=&debtor_info=&arbitr_info=&app_start_from' \
                '=&app_start_to=&app_end_from=&app_end_to=&trade_type=%D0%9B%D1%8E%D0%B1%D0%BE%D0%B9&trade_state=%D0' \
                '%9B%D1%8E%D0%B1%D0%BE%D0%B9&pagenum={}'

lot_url_sis = 'https://sistematorg.com/trade_view.php?trade_nid={}'

reffer = 'https://sistematorg.com/'

start_page = 1
# number ex. 25 means that parse will fetch data before page 25(25 doesn't include)
# for parsing only one page, example- start_page = 1 finish_page = 2
finish_page = 5

connect_db = {
    'table': 'lots_sistematorg'

}
USER_AGENT = choice(agent_list)
headers_brow = {
    "User-Agent": USER_AGENT,
}

absolute_path_to_download = f'{set_absolute}/etp_sistematorg'
relative_path = f'{set_relative}/etp_sistematorg'
lst_exet = ['.jpeg', '.png', '.jpg', '.bmp', '.JPG', '.JPEG', '.PNG']

pattern_trade_links = '/trade_view.php\?trade_nid=\d+'


def format_parse_date(days_: int, time_format=None):
    time_delta1 = timedelta(days=days_)
    _date_now = datetime.now()
    _start_date = _date_now - time_delta1
    if time_format is None:
        time_format = "%Y-%m-%d"
    else:
        time_format = time_format
    return _start_date.strftime(time_format)
