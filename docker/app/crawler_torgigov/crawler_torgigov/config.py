from general_utils.config import format_parse_date

start_date = format_parse_date(7, '%Y-%m-%d')
categories = {
    '22': 'Транспорт',
    '7': 'Недвижимость',
    '2': 'Земельные участки',
    '5':  'Акции и доли',
    '6':  'Права пользования и лицензии',
}
formdata = {
    'lotStatus': 'PUBLISHED,APPLICATIONS_SUBMISSION',
    'catCode': '',
    'matchPhrase': 'false',
    'pubFrom': start_date,
    'byFirstVersion': 'true',
    'withFacets': 'true',
    'size': '10',
    'page': '0'
}

data_origin = 'https://torgi.gov.ru/'
search_link = 'https://torgi.gov.ru/new/api/public/notices/search'
trade_link = 'https://torgi.gov.ru/new/api/public/notices/noticeNumber'
