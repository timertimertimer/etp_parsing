from general_utils.config import format_parse_date, absolute_download_path, relative_download_path

start_time_from = format_parse_date(30, '%d/%m/%Y')
domains = ['rad', 'confiscate', 'lease', 'privatization', 'arrested']
tables = {}
data_origin = {}
path_absolute = {}
path_relative = {}
for domain in domains:
    tables[domain] = f'lots_lot_online_{domain}'
    data_origin[domain] = f'https://{domain}.lot-online.ru/'
    path_absolute[domain] = f'{absolute_download_path}/etp_lot_online_{domain}'
    path_relative[domain] = f'{relative_download_path}/etp_lot_online_{domain}'
