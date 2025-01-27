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

with open(f'{path_to_socks5}', 'r') as f:
    lines = f.readlines()
socks_list = [i.replace('\\n', '').strip() for i in lines]


def format_parse_date():
    time_delta1 = timedelta(days=1)
    _date_now = datetime.now()
    _start_date = _date_now - time_delta1
    return _start_date.strftime("%d.%m.%Y")


def format_parse_date_plus():
    time_delta1 = timedelta(days=1)
    _date_now = datetime.now()
    _start_date = _date_now + time_delta1
    return _start_date.strftime("%d.%m.%Y")


start_time = format_parse_date()
end_request = format_parse_date_plus()

tables = {
    'table_torgi_gov_bankrot': 'lots_torgigov_bankrot',
    'table_torgi_gov_government': 'lots_torgigov_government'
}

_data_origin = {
    'torgi_gov': 'https://torgi.gov.ru/'
}

bankrot_link = {
    'torgi_bankrot': 'https://torgi.gov.ru/lotSearch1.html?bidKindId=13'
}

government_link = {
    'torgi_government': 'https://torgi.gov.ru/lotSearch1.html?bidKindId=8'
}

path_absolute = {
    'torgi_gov_bankrot': f'{set_absolute}/etp_torgigov_bankrot',
    'torgi_gov_government': f'{set_absolute}/etp_torgigov_government'
}

path_relative = {
    'torgi_gov_bankrot': f'{set_relative}/etp_torgigov_bankrot',
    'torgi_gov_government': f'{set_relative}/etp_torgigov_government'
}

lst_exet = ['.jpeg', '.png', '.jpg', '.bmp',
            '.JPG', '.JPEG', '.PNG' 'jpg', 'jpeg', 'JPG', 'JPEG', 'PNG']

lst_exet_archive = ['.rar', '.zip', '.7z', '.RAR', '.ZIP']

lst_exet_files = ['.jpeg', '.png', '.jpg', '.bmp', '.docx', '.doc', '.pdf',
                  '.JPG', '.JPEG', '.PNG' 'jpg', 'jpeg', 'JPG', 'JPEG', '.PNG', '.PDF', '.DOC', '.DOCX']

lst_exeption = ['reshenie', 'protocol', 'Reshenie', 'Protocol', 'Протокол', 'протокол', 'Решение', 'решение',
                'ПРОТОКОЛ']
