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
        time_format = "%Y-%-m-%-d"
    else:
        time_format = time_format
    return _start_date.strftime(time_format)


tables = {
    'table_alfalot': 'lots_alfalot',
    'table_arbitat': 'lots_arbitat',
    'table_arbbitlot': 'lots_arbbitlot',
    'table_bankrot_zakazrf': 'lots_bankrot_zakazrf',
    'table_bankrupt_alfalot': 'lots_bankrupt_alfalot',
    'table_bankrupt_centrr': 'lots_bankrupt_centrr',
    'table_bankrupt_electro_torgi': 'lots_bankrupt_elec_tor',
    'table_bankrupt_etpu': 'lots_bankrupt_etpu',
    'table_bepspb': 'lots_bepspb',
    'table_ets24': 'lots_ets24',
    'table_etp_bankrotstvo': 'lots_etp_bankrotstvo',
    'table_etpugra': 'lots_etpugra',
    'table_gloriaservice': 'lots_gloriaservice',
    'table_meta_invest': 'lots_meta_invest',
    'table_propertytrade': 'lots_propertytrade',
    'table_tender_ug': 'lots_tender_ug',
    'table_tendergarant': 'lots_tendergarant',
    'table_torgibankrot': 'lots_torgibankrot',
    'table_uralbidin': 'lots_uralbidin',
    'table_utender': 'lots_utender',
    'table_utpl': 'lots_utpl',
    'table_vertrades': 'lots_vertrades'
}

start_time = '0:0:-1'
start_date = format_parse_date(30)

start_date_post = start_date + ' ' + start_time

data_origin = {
    'alfalot': 'https://bankrupt.alfalot.ru/',
    'arbitat': 'http://arbitat.ru/',
    'arbbitlot': 'https://torgi.arbbitlot.ru/',
    'bankrot_zakazrf': 'http://bankrot.zakazrf.ru/',
    'bankrupt_alfalot': 'https://bankrupt.alfalot.ru/',
    'bankrupt_centrr': 'https://bankrupt.centerr.ru/',
    'bankrupt_electro_torgi': 'https://bankrupt.electro-torgi.ru/',
    'bankrupt_etpu': 'https://bankrupt.etpu.ru/',
    'bepspb': 'https://bepspb.ru/',
    'etp_bankrotstvo': 'https://www.etp-bankrotstvo.ru/',
    'ets24': 'http://bankrupt.ets24.ru/',
    'etpugra': 'http://etpugra.ru/',
    'gloriaservice': 'https://gloriaservice.ru/',
    'meta_invest': 'http://meta-invest.ru/',
    'propertytrade': 'https://propertytrade.ru/',
    'tender_ug': 'https://bankrupt.tender.one/',
    'tendergarant': 'http://tendergarant.com/',
    'torgibankrot': 'https://torgibankrot.ru/',
    'uralbidin': 'https://uralbidin.ru/',
    'utender': 'http://utender.ru/',
    'utpl': 'https://bankrupt.utpl.ru/',
    'vertrades': 'https://vertrades.ru/bankrupt/'
}


def return_auction_link(_data_origin):
    auction_link = 'public/auctions-all/'
    return _data_origin + auction_link


def return_offer_link(_data_origin):
    offer_link = 'public/public-offers-all/'
    return _data_origin + offer_link


def return_compet_link(_data_origin):
    competition_link = 'public/contests-all/'
    return _data_origin + competition_link


path_absolute = {
    'alfalot': f'{set_absolute}/etp_alfalot',
    'arbitat': f'{set_absolute}/etp_arbitat',
    'arbbitlot': f'{set_absolute}/etp_arbbitlot',
    'bankrot_zakazrf': f'{set_absolute}/etp_bankrot_zakazrf',
    'bankrupt_alfalot': f'{set_absolute}/etp_bankrupt_alfalot',
    'bankrupt_centrr': f'{set_absolute}/etp_bankrupt_centrr',
    'bankrupt_electro_torgi': f'{set_absolute}/etp_bankrupt_electro_torgi',
    'bankrupt_etpu': f'{set_absolute}/etp_bankrupt_etpu',
    'bepspb': f'{set_absolute}/etp_bepspb',
    'ets24': f'{set_absolute}/etp_ets24',
    'etp_bankrotstvo': f'{set_absolute}/etp_bepspb',
    'etpugra': f'{set_absolute}/etp_etpugra',
    'gloriaservice': f'{set_absolute}/etp_gloriaservice',
    'meta_invest': f'{set_absolute}/etp_meta_invest',
    'propertytrade': f'{set_absolute}/etp_propertytrade',
    'tender_ug': f'{set_absolute}/etp_bankrupt_tender_one',
    'tendergarant': f'{set_absolute}/etp_tendergarant',
    'torgibankrot': f'{set_absolute}/etp_torgibankrot',
    'uralbidin': f'{set_absolute}/etp_uralbidin',
    'utender': f'{set_absolute}/etp_utender',
    'utpl': f'{set_absolute}/etp_utpl',
    'vertrades': f'{set_absolute}/etp_vertrades'
}

path_relative = {
    'alfalot': f'{set_relative}/etp_alfalot',
    'arbitat': f'{set_relative}/etp_arbitat',
    'arbbitlot': f'{set_relative}/etp_arbbitlot',
    'bankrot_zakazrf': f'{set_relative}/etp_bankrot_zakazrf',
    'bankrupt_alfalot': f'{set_relative}/etp_bankrupt_alfalot',
    'bankrupt_centrr': f'{set_relative}/etp_bankrupt_centrr',
    'bankrupt_electro_torgi': f'{set_relative}/etp_bankrupt_electro_torgi',
    'bankrupt_etpu': f'{set_relative}/etp_bankrupt_etpu',
    'bepspb': f'{set_relative}/etp_bepspb',
    'ets24': f'{set_relative}/etp_ets24',
    'etp_bankrotstvo': f'{set_relative}/etp_bepspb',
    'etpugra': f'{set_relative}/etp_etpugra',
    'gloriaservice': f'{set_relative}/etp_gloriaservice',
    'meta_invest': f'{set_relative}/etp_meta_invest',
    'propertytrade': f'{set_relative}/etp_propertytrade',
    'tender_ug': f'{set_relative}/etp_bankrupt_tender_one',
    'tendergarant': f'{set_relative}/etp_tendergarant',
    'torgibankrot': f'{set_relative}/etp_torgibankrot',
    'uralbidin': f'{set_relative}/etp_uralbidin',
    'utender': f'{set_relative}/etp_utender',
    'utpl': f'{set_relative}/etp_utpl',
}

lst_exet = ['.jpeg', '.png', '.jpg', '.bmp',
            '.JPG', '.JPEG', '.PNG' 'jpg', 'jpeg', 'JPG', 'JPEG', 'PNG']

lst_exet_archive = ['.rar', '.zip', '.7z', '.RAR', '.ZIP', '.7Z', '.Rar', '.Zip']

lst_exet_files = ['.jpeg', '.png', '.jpg', '.bmp', '.docx', '.doc', '.pdf',
                  '.JPG', '.JPEG', '.PNG' 'jpg', 'jpeg', 'JPG', 'JPEG', 'PNG', '.PDF', '.DOC', '.DOCX']
