from os import environ, path
from pathlib import PurePosixPath
from datetime import datetime, timedelta

from scrapy.utils.conf import closest_scrapy_cfg

home_dir = environ['HOME']
proj_root = closest_scrapy_cfg()
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

# URLS
data_origin_url = 'https://sales.lot-online.ru'
start_url = 'https://sales.lot-online.ru/e-auction/mainpage.xhtml'
# start_url = 'https://httpbin.org/ip'
Referer = 'https://sales.lot-online.ru/e-auction/mainpage.xhtml'
url_for_post_download = 'https://sales.lot-online.ru/e-auction/auctionLotProperty.xhtml'

db_tables = {
    'zalog_sales': 'lots_sales_lot_online',
}

# path_absolute = {
#     'sales_lot_online_zalog': '/home/admin/web/78.24.219.218/public_html/downloads/etp_lot_online_zalog'
# }
#
# path_relative = {
#     'sales_lot_online_zalog': '/downloads/etp_lot_online_zalog'
# }
absolute_path_to_download = f'{set_absolute}/etp_lot_online_zalog'
relative_path = f'{set_relative}/etp_lot_online_zalog'
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
pattern_start_end_request = r'Период приёма заявок .* (\d{1,2}.\d{1,2}.\d{2,4}\s\d{1,2}:\d{1,2}\W\d{1,2}.\d{1,2}.\d{2,4}\s\d{1,2}:\d{1,2})'
pattern_start_end_trading = r'Время проведения процедуры при отсутствии предложен.{,10} по цене\s.{,20}\s(\d{1,2}.\d{1,2}.\d{2,4}\s\d{1,2}:\d{1,2}\W\d{1,2}.\d{1,2}.\d{2,4}\s\d{1,2}:\d{1,2})'
pattern_start_end_trading2 = r'Время проведения процедуры\W+(\d{1,2}.\d{1,2}.\d{2,4}\s\d{1,2}:\d{1,2}\W\d{1,2}.\d{1,2}.\d{2,4}\s\d{1,2}:\d{1,2})'


def format_parse_date(days_: int, time_format=None):
    time_delta1 = timedelta(days=days_)
    _date_now = datetime.now()
    _start_date = _date_now - time_delta1
    if time_format is None:
        time_format = "%Y-%m-%d"
    else:
        time_format = time_format
    return _start_date.strftime(time_format)
