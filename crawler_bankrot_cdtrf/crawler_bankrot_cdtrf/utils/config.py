from general_utils.config import absolute_download_path, relative_download_path, format_parse_date

start_date = format_parse_date(30)
data_origin_url = 'https://bankrot.cdtrf.ru/'
trade_page = 'https://bankrot.cdtrf.ru/public/undef/card/tradel.aspx'
trade_page_file = 'https://bankrot.cdtrf.ru/public/undef/card/'

trade_type_offer = '3'
trade_auction = '1'
trade_competition_ = '2'

absolute_path = f'{absolute_download_path}/etp_bankrot_cd'
relative_path = f'{relative_download_path}/etp_bankrot_cd'

lst_auction = [
    'https://bankrot.cdtrf.ru/public/undef/card/trade.aspx?id=052050',
    'https://bankrot.cdtrf.ru/public/undef/card/trade.aspx?id=052047'
]

lst_offer = []
