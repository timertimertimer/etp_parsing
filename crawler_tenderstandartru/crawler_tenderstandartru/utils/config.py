from datetime import datetime, timedelta
from os import environ, path
from pathlib import PurePosixPath
from scrapy.utils.conf import closest_scrapy_cfg

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


def format_parse_date(days_: int, time_format=None):
    time_delta1 = timedelta(days=days_)
    _date_now = datetime.now()
    _start_date = _date_now - time_delta1
    if time_format is None:
        time_format = "%d.%m.%Y"
    else:
        time_format = time_format
    return _start_date.strftime(time_format)


start_date = format_parse_date(35) + ' 00:00'

data_origin = {
    'au_pro': 'https://au-pro.ru/',
    'tenderstandart': 'https://tenderstandart.ru/',
    'torggroup': 'https://bankrot.torggroup.org/',
    'viomitra': 'https://bankrot.viomitra.ru/'
}

trades = ['Trade/AuctionTrades', 'Trade/PublicOfferTrades', 'Trade/CompetitionTrades']

path_absolute = {
    'au_pro': f'{set_absolute}/etp_au_pro',
    'tenderstandart': f'{set_absolute}/etp_tenderstandartru',
    'torggroup': f'{set_absolute}/etp_torggroup',
    'viomitra': f'{set_absolute}/etp_viomitra'
}

path_relative = {
    'au_pro': f'{set_relative}/etp_au_pro',
    'tenderstandart': f'{set_relative}/etp_tenderstandartru',
    'torggroup': f'{set_relative}/etp_torggroup',
    'viomitra': f'{set_relative}/etp_viomitra'
}

tables = {
    'au_pro': 'lots_au_pro',
    'tenderstandart': 'lots_tenderstandart',
    'torggroup': 'lots_torggroup',
    'viomitra': 'lots_viomitra',
}

lst_exet = ['.jpeg', '.png', '.jpg', '.bmp',
            '.JPG', '.JPEG', '.PNG' 'jpg', 'jpeg', 'JPG', 'JPEG', 'PNG']

lst_exet_archive = ['.rar', '.zip', '.7z', '.RAR', '.ZIP']

lst_exet_files = ['.jpeg', '.png', '.jpg', '.bmp', '.docx', '.doc', '.pdf',
                  '.JPG', '.JPEG', '.PNG' 'jpg', 'jpeg', 'JPG', 'JPEG', '.PNG', '.PDF', '.DOC', '.DOCX']

lst_exeption = ['reshenie', 'protocol', 'Reshenie', 'Protocol', 'Протокол', 'протокол', 'Решение', 'решение',
                'ПРОТОКОЛ']