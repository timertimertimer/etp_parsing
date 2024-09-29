from datetime import datetime, timedelta
from os import environ, path
from pathlib import PurePosixPath
from random import choice

from scrapy.utils.conf import closest_scrapy_cfg


proj_root = closest_scrapy_cfg()
home_dir = environ['HOME']
project_main_dir = PurePosixPath(proj_root).parent.parent.name + '/'
proxy_file = 'proxy_elit.txt'
socks_file = 'socks_5.txt'
user_agent = 'user-agent.txt'
path_to_proxy = path.join(home_dir, project_main_dir) + proxy_file
path_to_socks5 = path.join(home_dir, project_main_dir) + socks_file
path_user_agent = path.join(home_dir, project_main_dir) + user_agent
with open(f'{path_user_agent}', 'r') as f:
    lines = f.readlines()
agent_list = [i.replace('\\n', '').strip() for i in lines]

set_absolute_path = path.join(home_dir, project_main_dir) + 'set_main_path_to_download'
set_relative_path = path.join(home_dir, project_main_dir) + 'set_relative_path_to_download'

with open(f'{set_absolute_path}', 'r') as f:
    set_absolute = ''.join(f.readlines()).strip().replace('\n', '')
with open(f'{set_relative_path}', 'r') as f:
    set_relative = ''.join(f.readlines()).strip().replace('\n', '')


data_origin_url = 'https://www.akosta.info/'
search_link = 'https://www.akosta.info/akosta/lots.xhtml'

common_link = 'https://www.akosta.info/akosta/auctionCard.xhtml'
debtor_link = 'https://www.akosta.info/akosta/auctionCardDeb.xhtml'
lot_link = 'https://www.akosta.info/akosta/auctionCardLots.xhtml'
_link_post_period = 'https://www.akosta.info/akosta/lotCard.xhtml'


# PSW = os.environ['DBPASS']
def format_parse_date(days_: int, time_format=None):
    time_delta1 = timedelta(days=days_)
    _date_now = datetime.now()
    _start_date = _date_now - time_delta1
    if time_format is None:
        time_format = "%d.%m.%Y"
    else:
        time_format = time_format
    return _start_date.strftime(time_format)


connect_db = {

    'table': 'lots_akosta'

}
start_time = format_parse_date(1)
end_time = ''
start_page = 1
# page include current number
end_page = 3

# %d.%m.%y
# start_date_parse = '05.01.2017'
# end_date_parse = '01.06.2017'

absolute_path_to_download = f'{set_absolute}/etp_akosta'
relative_path = f'{set_relative}/etp_akosta'
lst_exet = ['.jpeg', '.png', '.jpg', '.bmp',
            '.JPG', '.JPEG', 'jpg', 'jpeg', 'JPG', 'JPEG',
            '.docx', '.doc', '.DOC', '.DOXC', '.pdf', '.PDF', '.rar', '.RAR', '.zip', '.ZIP', '.7z', '.7Z',
            '.rtf', '.xlsx',
            '.xls', '.XLS', '.XLSX'
            ]

lst_exet_archive = ['.rar', '.zip', '.7z']

lst_exet_files = ['.jpeg', '.png', '.jpg', '.bmp', '.docx', '.doc',
                  '.pdf', '.JPG', '.JPEG', '.PNG' 'jpg', 'jpeg', 'JPG', 'JPEG', 'PNG', '.PDF', '.DOC', '.DOCX',
                  '.rtf', '.xlsx',
                  '.xls', '.XLS', '.XLSX']



headers_brow = {
    "User-Agent": choice(agent_list),
}
