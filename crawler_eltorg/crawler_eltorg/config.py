from random import choice
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


USER_AGENT = choice(agent_list)

start_time = format_parse_date(1)

db_connect = {
    'table_name': 'lots_eltorg',
    'unique_fields': ['lot_id']  # поля, которые уникальны для каждого лота
}

page_limits = {
    'page_start': 0,  # страница начала парсинга (включительно)
    'page_stop': 20  # страница остановки парсинга (включительно)
}
headers_brow = {
    "User-Agent": USER_AGENT,
}

path_absolute = f'{set_absolute}/etp_eltorg'
relative_path = f'{set_relative}/etp_eltorg'
base_dir = f'{set_absolute}'  # путь к папке downloads
etp_folder = '/etp_eltorg'

createTable_query = 'CREATE TABLE IF NOT EXISTS %s (' % db_connect['table_name'] + \
                    'id BIGINT AUTO_INCREMENT PRIMARY KEY,' + \
                    'data_origin text,' + \
                    'trading_id varchar(255),' + \
                    'trading_link text,' + \
                    'trading_number varchar(255),' + \
                    'trading_type text,' + \
                    'trading_form text,' + \
                    'trading_org text,' + \
                    'trading_org_inn tinytext,' + \
                    'trading_org_contacts text COLLATE utf8mb4_bin,' + \
                    'msg_number varchar(255),' + \
                    'case_number varchar(255),' + \
                    'debtor_inn tinytext,' + \
                    'arbit_manager text,' + \
                    'arbit_manager_inn tinytext,' + \
                    'arbit_manager_org text,' + \
                    'status varchar(255),' + \
                    'lot_id varchar(255),' + \
                    'lot_link text,' + \
                    'lot_number smallint,' + \
                    'short_name mediumtext,' + \
                    'lot_info mediumtext,' + \
                    'property_information mediumtext,' + \
                    'start_date_requests timestamp NULL DEFAULT NULL,' + \
                    'end_date_requests timestamp NULL DEFAULT NULL,' + \
                    'start_date_trading timestamp NULL DEFAULT NULL,' + \
                    'end_date_trading timestamp NULL DEFAULT NULL,' + \
                    'start_price double,' + \
                    'step_price double,' + \
                    'periods mediumtext COLLATE utf8mb4_bin,' + \
                    'files mediumtext COLLATE utf8mb4_bin,' + \
                    'created_at timestamp) ' + \
                    'ENGINE=INNODB,' + \
                    'CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;'
