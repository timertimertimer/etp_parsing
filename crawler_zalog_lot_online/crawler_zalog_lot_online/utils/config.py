from general_utils.config import absolute_download_path, relative_download_path, start_date

# URLS
start_url = 'https://zalog.lot-online.ru'
go_to_urls = {
    'sbrf': 'https://zalog.lot-online.ru/sbrf',
    'rshb': 'https://zalog.lot-online.ru/rshb',
    'rad': 'https://zalog.lot-online.ru/rad',
}
organization_ids = {
    'sbrf': '754001',
    'rshb': '17711002',
    'rad': '763001',
}
data_pagination = {
    'keyWords': '',
    'publicationDateFrom': start_date,
    'publicationDateTo': '',
    'organization': '',
    'organizationId': '',
    'propertyTypeId': '',
    'priceFrom': '0',
    'priceTo': '10000000000',
    'countryCode': '',
    'regionCode': '',
    'districtCode': '',
    'cityCode': '',
    'propertyList': [],
    'metroName': '',
    'page': '1'
}
pagination_url = 'https://zalog.lot-online.ru/collateral/catalog.rest'

path_absolute = {
    'sbrf': f'{absolute_download_path}/etp_zalog_lot_online_sbrf',
    'rshb': f'{absolute_download_path}/etp_zalog_lot_online_rshb',
    'rad': f'{absolute_download_path}/etp_zalog_lot_online_rad',
}
path_relative = {
    'sbrf': f'{relative_download_path}/etp_zalog_lot_online_sbrf',
    'rshb': f'{relative_download_path}/etp_zalog_lot_online_rshb',
    'rad': f'{relative_download_path}/etp_zalog_lot_online_rad',
}
