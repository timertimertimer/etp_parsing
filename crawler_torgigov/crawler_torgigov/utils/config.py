from general_utils.config import format_parse_date, absolute_download_path, relative_download_path

start_date = format_parse_date(30, '%Y-%m-%d')
formdata = {
    'biddType': '229FZ',
    'pubFrom': start_date,
    'byFirstVersion': 'true',
    'withFacets': 'true',
    'size': '10',
    'page': '0'
}

data_origin = 'https://torgi.gov.ru/'
search_link = 'https://torgi.gov.ru/new/api/public/notices/search'
trade_link = 'https://torgi.gov.ru/new/api/public/notices/noticeNumber'
path_absolute = f'{absolute_download_path}/etp_torgigov'
path_relative = f'{relative_download_path}/etp_torgigov'
