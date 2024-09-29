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


start_time = format_parse_date(1)
stop_page = 10


# part of link to lots page (full path looks like -> https://xn-----6kcbaifbn4di5abenic8aq7kvd6a.xn--p1ai/etp/trade/inner-view-lots.html?perspective=inline&id=102042924&page=1(&_=1608883239180) the
#  last numbers generate automatic and it's not necessary )
link_path_to_lots = '/etp/trade/inner-view-lots.html?perspective=inline&id='

tables = {
    'table_etp_profit_ru': 'lots_etp_profit_ru',
    'table_ausib': 'lots_ausib',
    'table_seltim': 'lots_seltim',
    'table_atctrade': 'lots_atctrade',
    'table_regtorg': 'lots_regtorg',
    'table_aukcioncenter': 'lots_aukcioncenter',
    'table_torgidv': 'lots_torgidv',
    'table_ptp_center': 'lots_ptp_center',
    'table_trade_place_vetp': 'lots_trade_place_vetp'
}

_data_origin = {
    'etp_profit_ru': 'https://www.etp-profit.ru/index.html',
    'ausib': 'https://ausib.ru/index.html',
    'seltim': 'https://www.seltim.ru/index.html',
    'atctrade': 'https://atctrade.ru/index.html',
    'regtorg': 'https://www.regtorg.com/index.html',
    'aukcioncenter': 'https://aukcioncenter.ru/index.html',
    'torgidv': 'https://torgidv.ru/index.html',
    'ptp_center': 'https://ptp-center.ru/index.html',
    'trade_place_vetp': 'https://xn-----6kcbaifbn4di5abenic8aq7kvd6a.xn--p1ai/index.html',
}

_serp_link = {
    'etp_profit_ru': 'https://www.etp-profit.ru/etp/trade/list.html',
    'ausib': 'https://ausib.ru/etp/trade/list.html',
    'seltim': 'https://www.seltim.ru/etp/trade/list.html',
    'atctrade': 'https://atctrade.ru/etp/trade/list.html',
    'regtorg': 'https://www.regtorg.com/etp/trade/list.html',
    'aukcioncenter': 'https://aukcioncenter.ru/etp/trade/list.html',
    'torgidv': 'https://torgidv.ru/etp/trade/list.html',
    'ptp_center': 'https://ptp-center.ru/etp/trade/list.html',
    'trade_place_vetp': 'https://торговая-площадка-вэтп.рф/etp/trade/list.html',
}

_lot_link = {
    'etp_profit_ru': 'https://www.etp-profit.ru/etp/trade/inner-view-lots.html?perspective=inline&id=',
    'ausib': 'https://ausib.ru/etp/trade/inner-view-lots.html?perspective=inline&id=',
    'seltim': 'https://www.seltim.ru/etp/trade/inner-view-lots.html?perspective=inline&id=',
    'atctrade': 'https://atctrade.ru/etp/trade/inner-view-lots.html?perspective=inline&id=',
    'regtorg': 'https://www.regtorg.com/etp/trade/inner-view-lots.html?perspective=inline&id=',
    'aukcioncenter': 'https://aukcioncenter.ru/etp/trade/inner-view-lots.html?perspective=inline&id=',
    'torgidv': 'https://torgidv.ru/etp/trade/inner-view-lots.html?perspective=inline&id=',
    'ptp_center': 'https://ptp-center.ru/etp/trade/inner-view-lots.html?perspective=inline&id=',
    'trade_place_vetp': 'https://торговая-площадка-вэтп.рф/etp/trade/inner-view-lots.html?perspective=inline&id=',
}

_doc_link = {
    'etp_profit_ru': 'https://www.etp-profit.ru/edoc/attachments/list.html?perspective=inline&id=',
    'ausib': 'https://ausib.ru/edoc/attachments/list.html?perspective=inline&id=',
    'seltim': 'https://www.seltim.ru/edoc/attachments/list.html?perspective=inline&id=',
    'atctrade': 'https://atctrade.ru/edoc/attachments/list.html?perspective=inline&id=',
    'regtorg': 'https://www.regtorg.com/edoc/attachments/list.html?perspective=inline&id=',
    'aukcioncenter': 'https://aukcioncenter.ru/edoc/attachments/list.html?perspective=inline&id=',
    'torgidv': 'https://torgidv.ru/edoc/attachments/list.html?perspective=inline&id=',
    'ptp_center': 'https://ptp-center.ru/edoc/attachments/list.html?perspective=inline&id=',
    'trade_place_vetp': 'https://торговая-площадка-вэтп.рф/edoc/attachments/list.html?perspective=inline&id=',
}

url_file = {
    'etp_profit_ru': 'https://www.etp-profit.ru',
    'ausib': 'https://ausib.ru',
    'seltim': 'https://www.seltim.ru',
    'atctrade': 'https://atctrade.ru',
    'regtorg': 'https://www.regtorg.com',
    'aukcioncenter': 'https://aukcioncenter.ru',
    'torgidv': 'https://torgidv.ru',
    'ptp_center': 'https://ptp-center.ru',
    'trade_place_vetp': 'https://xn-----6kcbaifbn4di5abenic8aq7kvd6a.xn--p1ai',
}

path_absolute = {
    'etp_profit_ru': f'{set_absolute}/etp_etp_profit_ru',
    'ausib': f'{set_absolute}/etp_ausib',
    'seltim': f'{set_absolute}/etp_seltim',
    'atctrade': f'{set_absolute}/etp_atctrade',
    'regtorg': f'{set_absolute}/etp_regtorg',
    'aukcioncenter': f'{set_absolute}/etp_aukcioncenter',
    'torgidv': f'{set_absolute}/etp_torgidv',
    'ptp_center': f'{set_absolute}/etp_ptp_center',
    'trade_place_vetp': f'{set_absolute}/etp_trade_place_vetp',
}

path_relative = {
    'etp_profit_ru': f'{set_relative}/etp_etp_profit_ru',
    'ausib': f'{set_relative}/etp_ausib',
    'seltim': f'{set_relative}/etp_seltim',
    'atctrade': f'{set_relative}/etp_atctrade',
    'regtorg': f'{set_relative}/etp_regtorg',
    'aukcioncenter': f'{set_relative}/etp_aukcioncenter',
    'torgidv': f'{set_relative}/etp_torgidv',
    'ptp_center': f'{set_relative}/etp_ptp_center',
    'trade_place_vetp': f'{set_relative}/etp_trade_place_vetp',
}

lst_exet = ['.jpeg', '.png', '.jpg', '.bmp',
            '.JPG', '.JPEG', '.PNG' 'jpg', 'jpeg', 'JPG', 'JPEG', 'PNG']

lst_exet_archive = ['.rar', '.zip', '.7z', '.RAR', '.ZIP', '.7Z', '.Rar', '.Zip']

lst_exet_files = ['.jpeg', '.png', '.jpg', '.bmp', '.docx', '.doc', '.pdf',
                  '.JPG', '.JPEG', '.PNG' 'jpg', 'jpeg', 'JPG', 'JPEG', 'PNG', '.PDF', '.DOC', '.DOCX']
# 103182268 102901071
# bad_links_list = ['https://ausib.ru/trade/view/purchase/general.html?id=103165770',
#                   'https://ausib.ru/trade/view/purchase/general.html?id=102935693']
