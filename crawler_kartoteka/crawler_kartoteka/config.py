from general_utils.config import absolute_download_path, relative_download_path

data_origin_url = 'https://www.kartoteka.ru/'
main_url = 'https://www.kartoteka.ru/bankruptcy2'

path_absolute = f'{absolute_download_path}/etp_kartoteka'
path_relative = f'{relative_download_path}/etp_kartoteka'

form_data = {
    'rows-per-page': '15',
    'rows-per-page-current': '15',
    'type-of-bidding': '0',
    'in-lot': '0',
    'only-favorites': '0',
    'has-image': '0',
    'check-mode': '0',
    'in-search': '0',
    'is-sold': '0',
    'exact': 'off'
}
