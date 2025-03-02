from general_utils.config import absolute_download_path, relative_download_path

stop_page = 10

link_path_to_lots = '/etp/trade/inner-view-lots.html?perspective=inline&id='

_data_origin = {
    'etp_profit': 'https://www.etp-profit.ru/',
    'ausib': 'https://ausib.ru/',
    'seltim': 'https://www.seltim.ru/',
    'atctrade': 'https://atctrade.ru/',
    'regtorg': 'https://regtorg.com/',
    'aukcioncenter': 'https://aukcioncenter.ru/',
    'torgidv': 'https://torgidv.ru/',
    'ptp_center': 'https://ptp-center.ru/',
}

_serp_link = {
    'etp_profit': 'https://www.etp-profit.ru/etp/trade/list.html',
    'ausib': 'https://ausib.ru/etp/trade/list.html',
    'seltim': 'https://www.seltim.ru/etp/trade/list.html',
    'atctrade': 'https://atctrade.ru/etp/trade/list.html',
    'regtorg': 'https://regtorg.com/etp/trade/list.html',
    'aukcioncenter': 'https://aukcioncenter.ru/etp/trade/list.html',
    'torgidv': 'https://torgidv.ru/etp/trade/list.html',
    'ptp_center': 'https://ptp-center.ru/etp/trade/list.html',
}

_lot_link = {
    'etp_profit': 'https://www.etp-profit.ru/etp/trade/inner-view-lots.html?perspective=inline&id=',
    'ausib': 'https://ausib.ru/etp/trade/inner-view-lots.html?perspective=inline&id=',
    'seltim': 'https://www.seltim.ru/etp/trade/inner-view-lots.html?perspective=inline&id=',
    'atctrade': 'https://atctrade.ru/etp/trade/inner-view-lots.html?perspective=inline&id=',
    'regtorg': 'https://www.regtorg.com/etp/trade/inner-view-lots.html?perspective=inline&id=',
    'aukcioncenter': 'https://aukcioncenter.ru/etp/trade/inner-view-lots.html?perspective=inline&id=',
    'torgidv': 'https://torgidv.ru/etp/trade/inner-view-lots.html?perspective=inline&id=',
    'ptp_center': 'https://ptp-center.ru/etp/trade/inner-view-lots.html?perspective=inline&id=',
}

_doc_link = {
    'etp_profit': 'https://www.etp-profit.ru/edoc/attachments/list.html?perspective=inline&id=',
    'ausib': 'https://ausib.ru/edoc/attachments/list.html?perspective=inline&id=',
    'seltim': 'https://www.seltim.ru/edoc/attachments/list.html?perspective=inline&id=',
    'atctrade': 'https://atctrade.ru/edoc/attachments/list.html?perspective=inline&id=',
    'regtorg': 'https://www.regtorg.com/edoc/attachments/list.html?perspective=inline&id=',
    'aukcioncenter': 'https://aukcioncenter.ru/edoc/attachments/list.html?perspective=inline&id=',
    'torgidv': 'https://torgidv.ru/edoc/attachments/list.html?perspective=inline&id=',
    'ptp_center': 'https://ptp-center.ru/edoc/attachments/list.html?perspective=inline&id=',
}

url_file = {
    'etp_profit': 'https://www.etp-profit.ru',
    'ausib': 'https://ausib.ru',
    'seltim': 'https://www.seltim.ru',
    'atctrade': 'https://atctrade.ru',
    'regtorg': 'https://www.regtorg.com',
    'aukcioncenter': 'https://aukcioncenter.ru',
    'torgidv': 'https://torgidv.ru',
    'ptp_center': 'https://ptp-center.ru',
}

path_absolute = {
    'etp_profit': f'{absolute_download_path}/etp_etp_profit',
    'ausib': f'{absolute_download_path}/etp_ausib',
    'seltim': f'{absolute_download_path}/etp_seltim',
    'atctrade': f'{absolute_download_path}/etp_atctrade',
    'regtorg': f'{absolute_download_path}/etp_regtorg',
    'aukcioncenter': f'{absolute_download_path}/etp_aukcioncenter',
    'torgidv': f'{absolute_download_path}/etp_torgidv',
    'ptp_center': f'{absolute_download_path}/etp_ptp_center',
}

path_relative = {
    'etp_profit': f'{relative_download_path}/etp_etp_profit',
    'ausib': f'{relative_download_path}/etp_ausib',
    'seltim': f'{relative_download_path}/etp_seltim',
    'atctrade': f'{relative_download_path}/etp_atctrade',
    'regtorg': f'{relative_download_path}/etp_regtorg',
    'aukcioncenter': f'{relative_download_path}/etp_aukcioncenter',
    'torgidv': f'{relative_download_path}/etp_torgidv',
    'ptp_center': f'{relative_download_path}/etp_ptp_center',
}
