from general_utils.config import format_parse_date, absolute_download_path, relative_download_path

start_time_from = format_parse_date(30, '%d/%m/%Y')
domains = ['rad', 'confiscate', 'lease', 'privatization', 'arrested', 'bankruptcy', 'private_property']
tables = {}
main_data_origin = 'https://www.lot-online.ru/'
data_origin = {}
path_absolute = {}
path_relative = {}
for domain in domains:
    tables[domain] = f'lots_lot_online_{domain}'
    data_origin[domain] = f'https://{domain}.lot-online.ru/'
    path_absolute[domain] = f'{absolute_download_path}/etp_lot_online_{domain}'
    path_relative[domain] = f'{relative_download_path}/etp_lot_online_{domain}'

# https://catalog.lot-online.ru/index.php?dispatch=categories.view&category_id=9876&features_hash=172-186357&filter_fields[is_archive]=all
hashes = {
    'bankruptcy': '172-186359',
    'private_property': '172-186357',
}
catalog_formdata = {
    'dispatch': 'categories.view',
    'category_id': '9876',
    'features_hash': '',
    'filter_fields[is_archive]': 'all',
    'sort_by': 'timestamp',
    'sort_order': 'desc',
    'layout': 'short_list',
    'result_ids': 'pagination_contents',
    'items_per_page': '96',
    'page': '1',
    'is_ajax': '1'
}

form_data = {
    'saleTypeId': '3001',
    'applicationSubmitStart': start_time_from,
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

start_date = format_parse_date(1)
