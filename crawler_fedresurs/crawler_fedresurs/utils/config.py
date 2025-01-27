import os
import re
from os import path
from pathlib import PurePosixPath
from random import choice

from scrapy.utils.conf import closest_scrapy_cfg

proj_root = closest_scrapy_cfg()
home_dir = '/home/parser'
_path_config_ini = f'{home_dir}/etp_parsing'
project_main_dir = PurePosixPath(proj_root).parent.parent.name + '/'
proxy_file = 'proxy_all.txt'
user_agent = 'user-agent.txt'
path_to_proxy = path.join(home_dir, project_main_dir) + proxy_file
path_user_agent = path.join(home_dir, project_main_dir) + user_agent
with open(f'{path_user_agent}', 'r') as f:
    lines = f.readlines()
agent_list = [i.replace('\\n', '').strip() for i in lines]

SPLASH_URL_ARBITOR = 'http://localhost:8051'
SPLASH_URL_ORGANIZER = 'http://localhost:8052'
SPLASH_URL_DEBITOR = 'http://localhost:8053'

# path for directory
MAIN_DIR = ''.join(re.findall('^/home/\w+/?', os.getcwd()))
DIR_PROJECT = f'{MAIN_DIR}etp_parsing/crawler_fedresurs/'
DIR_ORGANIZER = f'{MAIN_DIR}etp_parsing/crawler_fedresurs/crawler_fedresurs/json_task_data/task_organizer'
DIR_DEBITR = f'{MAIN_DIR}etp_parsing/crawler_fedresurs/crawler_fedresurs/json_task_data/task_debitr'
DIR_ARBITOR = f'{MAIN_DIR}etp_parsing/crawler_fedresurs/crawler_fedresurs/json_task_data/task_arbitr'

TABLE_ARBITR = 'fedresurs_arbitrator'
TABLE_ORGANIZER = 'fedresurs_organizer'
TABLE_DEBITR = 'fedresurs_debtor'
connect_db = {
    'table_fedres_data': 'fedres_data'

}

start_link = 'https://bankrot.fedresurs.ru'
arbitr_link = 'https://bankrot.fedresurs.ru/ArbitrManagersList.aspx'
org_link = 'https://bankrot.fedresurs.ru/TradeOrganizers.aspx'
debitr_link = 'https://bankrot.fedresurs.ru/DebtorsSearch.aspx'
headers_brow = {
    "User-Agent": choice(agent_list),
}
ARBITR_NAME = 'arbitrator'
ORGANIZER_ALL = 'organizer'
ORG_NAME = 'organizer_name'
ORG_COMPANY = 'organizer_company'
DEBITR = 'debtor'

pattern_company_cut = ['ооо', 'общество с ограниченной ответственностью', 'ао', 'акционерное общество',
                       'акционерное общество открытого типа', 'открытое акционерное общество', 'оао',
                       'товарищество с ограниченной ответственностью', 'акционерное общество закрытого типа',
                       'закрытое акционерное общество', 'зао', 'публичное акционерное общество', 'пао',
                       'непубличное акционерное общество',
                       'некоммерческая организация', 'унитарное предприятие', 'общественная организация',
                       'государственная корпорация', 'фирма']
pattern_name_cut = ['индивидуальный предприниматель']

# cookie names
asp = 'asp.net_sessionid'
bankrot = 'bankrotcookie'
fedresurs = 'fedresurscookie'

