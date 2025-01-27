from general_utils.config import absolute_download_path, relative_download_path, format_parse_date

data_origin_url = 'https://m-ets.ru/'
url_start = 'https://m-ets.ru/search'
absolute_path = f'{absolute_download_path}/etp_mets_ru'
relative_path = f'{relative_download_path}/etp_mets_ru'

pattern_without_hash = r'https.+m-ets.+generalView.+id=\d+'
pattern_trade_links = r'https.+mets.+View.+id=\d+.(lot1)$'
start_date = format_parse_date(1)
