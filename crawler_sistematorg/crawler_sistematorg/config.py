from general_utils.config import absolute_download_path, relative_download_path

referer = 'https://m-ets.ru/search'

data_origin_url = 'https://m-ets.ru/'
url_start = 'https://m-ets.ru/search'

bot_name = 'sistematorg'
allowed_domain = 'sistematorg.com'
main_url = ['https://sistematorg.com']
main_url_list = 'https://sistematorg.com/tradelist.php?trade_number=&debtor_info=&arbitr_info=&app_start_from' \
                '=&app_start_to=&app_end_from=&app_end_to=&trade_type=%D0%9B%D1%8E%D0%B1%D0%BE%D0%B9&trade_state=%D0' \
                '%9B%D1%8E%D0%B1%D0%BE%D0%B9&pagenum={}'

lot_url_sis = 'https://sistematorg.com/trade_view.php?trade_nid={}'
reffer = 'https://sistematorg.com/'

start_page = 1
# number ex. 25 means that parse will fetch data before page 25(25 doesn't include)
# for parsing only one page, example- start_page = 1 finish_page = 2
finish_page = 5

absolute_path_to_download = f'{absolute_download_path}/etp_sistematorg'
relative_path = f'{relative_download_path}/etp_sistematorg'

pattern_trade_links = '/trade_view.php\?trade_nid=\d+'
