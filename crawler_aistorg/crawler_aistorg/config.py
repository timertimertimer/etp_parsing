from os import environ, path
from datetime import datetime, timedelta
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

main_url = 'http://www.aistorg.ru'
url_reestr = 'http://www.aistorg.ru/reestr/auctions/bankrot/?PAGEN_1={}'

start_page = 1
finish_page = 2
paginator_ = 1


pattern_trade_links = r'\/reestr\/.+\/.+\/\d+\/'
pattern_lot_links = r'/reestr\/.+/bankrot\/lots\/\?id=\d+.*lot_id=\d+'
pattern_next_page = None
pattern_periods = None

absolute_path_to_download = f'{set_absolute}/etp_aistorg'
relative_path = f'{set_relative}/etp_aistorg'
lst_ext = ['.jpeg', '.png', '.jpg', '.bmp', '.JPG', '.JPEG', '.PNG']
connect_db = {
    'table': 'lots_aistorg'

}

script_lua = """
         function main(splash)
         splash:on_request(function(request)
             if request.url:find('css') then
                 request.abort()
             end 
             end)
             splash.images_enabled=false
             splash.js_enabled=false
             splash.private_mode_enabled = false
             splash:init_cookies(splash.args.cookies)
             assert(splash:go{
             splash.args.url,
             headers=splash.args.headers,
             http_method=splash.args.http_method,
             body=splash.args.body,
             })
             assert(splash:wait(4))
             local entries = splash:history()
             local last_response = entries[#entries].response
             return {
                 url = splash:url(),
                 headers = last_response.headers,
                 http_status = last_response.status,
                 cookies = splash:get_cookies(),
                 html = splash:html(),
                 }
         end
                 """

def format_parse_date(days_: int, time_format=None):
    time_delta1 = timedelta(days=days_)
    _date_now = datetime.now()
    _start_date = _date_now - time_delta1
    if time_format is None:
        time_format = "%d.%m.%Y"
    else:
        time_format = time_format
    return _start_date.strftime(time_format)