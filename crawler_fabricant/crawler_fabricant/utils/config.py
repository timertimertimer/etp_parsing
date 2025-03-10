from general_utils.config import absolute_download_path, relative_download_path, start_date

data_origin_url = 'https://www.fabrikant.ru/'
start_url = 'https://www.fabrikant.ru/trades/procedure/search/?filter_id=6'
absolute_path = f'{absolute_download_path}/etp_fabricant'
relative_path = f'{relative_download_path}/etp_fabricant'
formdata = {
    'type': '1',
    'org_type': 'org',
    'currency': '0',
    'date_type': 'date_publication',
    'date_from': f'{start_date}',
    'ensure': 'all',
    'filter_id': '6',
    'okpd2_embedded': '1',
    'okdp_embedded': '1',
    'active': '',
    'count_on_page': '40'
}
