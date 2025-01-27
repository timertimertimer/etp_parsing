from general_utils.config import absolute_download_path, relative_download_path, format_parse_date

data_origin = 'http://eurtp.ru/'
path_absolute = f'{absolute_download_path}/etp_eurtp'
path_relative = f'{relative_download_path}/etp_eurtp'
start_date = format_parse_date(7, '%m/%d/%Y 00:00:00')
end_date = format_parse_date(0, '%m/%d/%Y 00:00:00')
categories = [
    'https://eurtp.ru/Home/AuctionOpen',
    'https://eurtp.ru/Home/AuctionClose',
    'https://eurtp.ru/Home/Competition',
    'https://eurtp.ru/Home/PublicOffering'
]
