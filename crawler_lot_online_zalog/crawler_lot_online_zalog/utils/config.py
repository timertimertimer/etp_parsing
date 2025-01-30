from general_utils.config import absolute_download_path, relative_download_path

# URLS
data_origin_url = 'https://sales.lot-online.ru'
start_url = 'https://sales.lot-online.ru/e-auction/mainpage.xhtml'
# start_url = 'https://httpbin.org/ip'
Referer = 'https://sales.lot-online.ru/e-auction/mainpage.xhtml'
url_for_post_download = 'https://sales.lot-online.ru/e-auction/auctionLotProperty.xhtml'

# path_absolute = {
#     'sales_lot_online_zalog': '/home/admin/web/78.24.219.218/public_html/downloads/etp_lot_online_zalog'
# }
#
# path_relative = {
#     'sales_lot_online_zalog': '/downloads/etp_lot_online_zalog'
# }
absolute_path = f'{absolute_download_path}/etp_lot_online_zalog'
relative_path = f'{relative_download_path}/etp_lot_online_zalog'
# prime_cookies for download files


prime_cookies = 'primefaces.download=true; '
pattern_start_end_request = r'Период приёма заявок .* (\d{1,2}.\d{1,2}.\d{2,4}\s\d{1,2}:\d{1,2}\W\d{1,2}.\d{1,2}.\d{2,4}\s\d{1,2}:\d{1,2})'
pattern_start_end_trading = r'Время проведения процедуры при отсутствии предложен.{,10} по цене\s.{,20}\s(\d{1,2}.\d{1,2}.\d{2,4}\s\d{1,2}:\d{1,2}\W\d{1,2}.\d{1,2}.\d{2,4}\s\d{1,2}:\d{1,2})'
pattern_start_end_trading2 = r'Время проведения процедуры\W+(\d{1,2}.\d{1,2}.\d{2,4}\s\d{1,2}:\d{1,2}\W\d{1,2}.\d{1,2}.\d{2,4}\s\d{1,2}:\d{1,2})'
