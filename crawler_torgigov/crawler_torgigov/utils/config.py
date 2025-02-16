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
# tables = {
#     'table_torgi_gov_bankrot': 'lots_torgigov_bankrot',
#     'table_torgi_gov_government': 'lots_torgigov_government'
# }

data_origin = 'https://torgi.gov.ru/'
search_link = 'https://torgi.gov.ru/new/api/public/notices/search'
trade_link = 'https://torgi.gov.ru/new/api/public/notices/noticeNumber'
path_absolute = f'{absolute_download_path}/etp_torgigov'
path_relative = f'{relative_download_path}/etp_torgigov'
# bankrot_link = {
#     'torgi_bankrot': 'https://torgi.gov.ru/lotSearch1.html?bidKindId=13'
# }

# government_link = {
#     'torgi_government': 'https://torgi.gov.ru/lotSearch1.html?bidKindId=8'
# }

# path_absolute = {
#     'torgi_gov_bankrot': f'{set_absolute}/etp_torgigov_bankrot',
#     'torgi_gov_government': f'{set_absolute}/etp_torgigov_government'
# }
#
# path_relative = {
#     'torgi_gov_bankrot': f'{set_relative}/etp_torgigov_bankrot',
#     'torgi_gov_government': f'{set_relative}/etp_torgigov_government'
# }
