from datetime import datetime, timedelta
from os import environ, path
from pathlib import PurePosixPath

from scrapy.utils.conf import closest_scrapy_cfg

home_dir = environ['HOME']
proj_root = closest_scrapy_cfg()
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


def format_parse_date(days=1, time_format=None):
    time_delta1 = timedelta(days)
    _date_now = datetime.now()
    if time_format is None:
        time_format = "%d.%m.%Y"
    else:
        time_format = time_format
    _start_date = _date_now - time_delta1
    return _start_date.strftime(time_format)


start_time = format_parse_date()
end_request = ''


# part of link to lots page (full path looks like -> https://xn-----6kcbaifbn4di5abenic8aq7kvd6a.xn--p1ai/etp/trade/inner-view-lots.html?perspective=inline&id=102042924&page=1(&_=1608883239180) the
#  last numbers generate automatic and it's not necessary )
link_path_to_lots = '/etp/trade/inner-view-lots.html?perspective=inline&id='

tables = {
    'table_nistp': 'lots_nistpru',
}

_data_origin = {
    'nistp_ru': 'http://nistp.ru/'
}

_trade_link = {
    'nistp': 'http://nistp.ru/bankrot'
}

path_absolute = {
    'nistp': f'{set_absolute}/etp_nistp'
}

path_relative = {
    'nistp': f'{set_relative}/etp_nistp'
}

lst_exet = ['.jpeg', '.png', '.jpg', '.bmp',
            '.JPG', '.JPEG', '.PNG' 'jpg', 'jpeg', 'JPG', 'JPEG', 'PNG']

lst_exet_archive = ['.rar', '.zip', '.7z', '.RAR', '.ZIP']

lst_exet_files = ['.jpeg', '.png', '.jpg', '.bmp', '.docx', '.doc', '.pdf',
                  '.JPG', '.JPEG', '.PNG' 'jpg', 'jpeg', 'JPG', 'JPEG', '.PNG', '.PDF', '.DOC', '.DOCX']

lst_exeption = ['reshenie', 'protocol', 'Reshenie', 'Protocol', 'Протокол', 'протокол', 'Решение', 'решение',
                'ПРОТОКОЛ']

#bad_links_list = ['http://nistp.ru/bankrot/trade_view.php?trade_nid=202636',
