from general_utils.config import format_parse_date, absolute_download_path, relative_download_path

data_origin_url = 'https://sales.lot-online.ru'
main_page_url = 'https://sales.lot-online.ru/e-auction/mainpage.xhtml'
category_url = 'https://sales.lot-online.ru/e-auction/lots.xhtml'
first_part_url_lot = 'https://sales.lot-online.ru/e-auction/'
url_for_post_download = 'https://sales.lot-online.ru/e-auction/auctionLotProperty.xhtml'
file_param = "?pfdrid_c=true"

# %Y-%m-%d
start_time_from = format_parse_date(1, '%Y-%m-%d')
# format period
# W - week
# D - day
format_period = 'D'
# periods - how many weeks or days been iteration - FREQUENCY (freq)
periods_ = 1
time_delta = 1

Referer = 'https://sales.lot-online.ru/e-auction/mainpage.xhtml'
Referer_lot = 'https://sales.lot-online.ru/e-auction/lots.xhtml'
absolute_path_to_download = f'{absolute_download_path}/etp_lot_online'
relative_path = f'{relative_download_path}/etp_lot_online'

# prime_cookies for download files


prime_cookies = 'primefaces.download=true; '

list_error_link = [
    'https://sales.lot-online.ru/e-auction/auctionLotProperty.xhtml?parm=lotUnid%3D960000318172%3Bmode%3Djust',


    ]
