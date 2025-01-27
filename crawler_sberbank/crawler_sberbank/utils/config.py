from general_utils.config import format_parse_date, absolute_download_path, relative_download_path

data_origin_url = 'https://utp.sberbank-ast.ru'
main_url_start = 'https://utp.sberbank-ast.ru/Bankruptcy/List/BidList'
part_path_to_trade = r'PurchaseView'
part_path_to_lot = r'BidView'
time_delta = 7
start_date = format_parse_date(time_delta, time_format='%Y-%m-%d')
# format period
# W - week
# D - day
format_period = 'D'
# periods - how many weeks or days been iteration - FREQUENCY (freq)
periods_ = 1
Referer = 'https://utp.sberbank-ast.ru/Bankruptcy/List/BidList'
absolute_path = f'{absolute_download_path}/etp_sberbank'
relative_path = f'{relative_download_path}/etp_sberbank'
pattern_lots_links = r' <objectHrefTerm>(.*?)</objectHrefTerm>'
first_part_link = 'https://utp.sberbank-ast.ru/Bankruptcy/File/DownloadFile?fid='
