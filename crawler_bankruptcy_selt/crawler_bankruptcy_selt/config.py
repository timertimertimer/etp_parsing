from datetime import datetime, timedelta
from os import environ, path
from pathlib import PurePosixPath
from random import choice

from scrapy.utils.conf import closest_scrapy_cfg

main_url = 'http://www.selt-online.ru/'
url_main_pagination = 'http://bankruptcy.selt-online.ru/?page={}&ascending=False'
host_url = 'http://bankruptcy.selt-online.ru'
start_page = 1
stop_page = 10

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
headers_brow = {
    "User-Agent": choice(agent_list),
}
USER_AGENT = headers_brow['User-Agent']
pattern_trade_links = r'/Trade/AnounsmentDetails/\d+'
pattern_next_page = r'page=\d+'
pattern_periods = r'(?P<start>\d+\.\d+\.\d{4}?) (?P<end>\d{1,2}\:\d{1,2}\:\d{1,2}?).+?(?P<price>\d+(,|.)\d{1,2} \руб.?\')'

absolute_path_to_download = f'{set_absolute}/etp_bankruptcy'
relative_path = f'{set_relative}/etp_bankruptcy'
lst_ext = ['.jpeg', '.png', '.jpg', '.bmp',
           '.JPG', '.JPEG', '.PNG' 'jpg', 'jpeg', 'JPG', 'JPEG', 'PNG']
connect_db = {
    'table': 'lots_bankruptcy'

}

def format_parse_date(days_: int, time_format=None):
    time_delta1 = timedelta(days=days_)
    _date_now = datetime.now()
    _start_date = _date_now - time_delta1
    if time_format is None:
        time_format = "%d.%m.%Y"
    else:
        time_format = time_format
    return _start_date.strftime(time_format)