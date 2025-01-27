from pathlib import PurePosixPath
from random import choice
import os
import re
from datetime import datetime, timedelta
from os import environ, path

from scrapy.utils.conf import closest_scrapy_cfg

proj_root = closest_scrapy_cfg()
home_dir = environ['HOME']
project_main_dir = PurePosixPath(proj_root).parent.parent.name + '/'
proxy_file = 'proxy_all.txt'
user_agent = 'user-agent.txt'
path_to_proxy = path.join(home_dir, project_main_dir) + proxy_file
path_user_agent = path.join(home_dir, project_main_dir) + user_agent
with open(f'{path_user_agent}', 'r') as f:
    lines = f.readlines()
agent_list = [i.replace('\\n', '').strip() for i in lines]

def format_parse_date():
    time_delta1 = timedelta(days=1)
    date_now = datetime.now()
    start_date = date_now - time_delta1
    return start_date.strftime("%Y-%m-%d")


SPLASH_URL_MSG = 'http://localhost:8054'
SPLASH_DOWNLOAD = 'http://0.0.0.0:8055'
ROOT_DIR = ''.join(re.findall('^/home/\w+/?', os.getcwd()))

start_link = 'https://bankrot.fedresurs.ru'
message_page = f'{start_link}/Messages.aspx'
param = {'attempt': '1'}
post_privat_office = 'ctl00$cphBody$upMessages'
# %Y-%m-%d ex '2020-11-05'
start_time_from = format_parse_date()
#start_time_from = '2017-01-01'
periods_ = 2
time_delta = 0
format_period = 'D'

headers_brow = {
    "User-Agent": choice(agent_list),
}

connect_db = {
    'table': 'fedresurs_messages'
}

absolute_path_to_download = ''
relative_path = '/downloads/fedresurs_msg'

# cookie names
asp = 'asp.net_sessionid'
bankrot = 'bankrotcookie'
fedresurs = 'fedresurscookie'

announce_msg_trade = 'Объявление о проведении торгов'
canceled_msg_ad = 'Сообщение об отмене сообщения об объявлении торгов или сообщения о результатах торгов'
public_tender_msg = 'Сообщение о результатах торгов'
modified_message_msg = 'Сообщение об изменении объявления о проведении торгов'
report_of_valuer = 'Отчет оценщика об оценке имущества должника'

escape_words = '(аннулировано, заблокировано)'
