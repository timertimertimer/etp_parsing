from general_utils.config import format_parse_date

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
