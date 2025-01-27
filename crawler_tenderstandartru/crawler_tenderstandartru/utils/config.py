from general_utils.config import format_parse_date, absolute_download_path, relative_download_path

start_date = format_parse_date(30, '%d.%m.%Y %H:%M')

data_origin = {
    'au_pro': 'https://au-pro.ru/',
    'tenderstandart': 'https://tenderstandart.ru/',
    'torggroup': 'https://bankrot.torggroup.org/',
    'viomitra': 'https://bankrot.viomitra.ru/'
}

trades = ['Trade/AuctionTrades', 'Trade/PublicOfferTrades', 'Trade/CompetitionTrades']

path_absolute = {
    'au_pro': f'{absolute_download_path}/etp_au_pro',
    'tenderstandart': f'{absolute_download_path}/etp_tenderstandartru',
    'torggroup': f'{absolute_download_path}/etp_torggroup',
    'viomitra': f'{absolute_download_path}/etp_viomitra'
}

path_relative = {
    'au_pro': f'{relative_download_path}/etp_au_pro',
    'tenderstandart': f'{relative_download_path}/etp_tenderstandartru',
    'torggroup': f'{relative_download_path}/etp_torggroup',
    'viomitra': f'{relative_download_path}/etp_viomitra'
}

tables = {
    'au_pro': 'lots_au_pro',
    'tenderstandart': 'lots_tenderstandart',
    'torggroup': 'lots_torggroup',
    'viomitra': 'lots_viomitra',
}