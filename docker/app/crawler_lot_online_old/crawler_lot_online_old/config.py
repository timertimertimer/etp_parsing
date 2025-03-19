from general_utils.config import format_parse_date, relative_download_path, absolute_download_path

main_data_origin = 'https://www.lot-online.ru/'
domains = ['rad', 'confiscate', 'lease', 'privatization', 'arrested']
data_origin = {}
path_absolute = {}
path_relative = {}
for domain in domains:
    data_origin[domain] = f'https://{domain}.lot-online.ru/'
    path_absolute[domain] = f'{absolute_download_path}/etp_lot_online_{domain}'
    path_relative[domain] = f'{relative_download_path}/etp_lot_online_{domain}'
form_data = {
    'saleTypeId': '3001',
    'applicationSubmitStart': format_parse_date(30, '%d/%m/%Y'),
    'applicationSubmitStop': '',
    'biddingStart': '',
    'biddingStop': '',
    'tenderType': '',
    'nonElectronic': '',
    'country': '1001',
    'region': '',
    'category': '',
    'keyWords': '',
    'tenderLotFilter': 'TENDER',
    'tenderStatusSet': '',
    'lotStatusSet': '',
    'profileId': '',
    '_search': 'false',
    'rows': '100',
    'page': '1',
    'sidx': '',
    'sord': 'asc'
}
