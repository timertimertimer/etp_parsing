from general_utils.config import absolute_download_path, relative_download_path

stop_page = 10


# part of link to lots page (full path looks like -> https://xn-----6kcbaifbn4di5abenic8aq7kvd6a.xn--p1ai/etp/trade/inner-view-lots.html?perspective=inline&id=102042924&page=1(&_=1608883239180) the
#  last numbers generate automatic and it's not necessary )
link_path_to_lots = '/etp/trade/inner-view-lots.html?perspective=inline&id='

tables = {
    'table_etp_profit_ru': 'lots_etp_profit_ru',
    'table_ausib': 'lots_ausib',
    'table_seltim': 'lots_seltim',
    'table_atctrade': 'lots_atctrade',
    'table_regtorg': 'lots_regtorg',
    'table_aukcioncenter': 'lots_aukcioncenter',
    'table_torgidv': 'lots_torgidv',
    'table_ptp_center': 'lots_ptp_center',
    'table_trade_place_vetp': 'lots_trade_place_vetp'
}

_data_origin = {
    'etp_profit_ru': 'https://www.etp-profit.ru/index.html',
    'ausib': 'https://ausib.ru/index.html',
    'seltim': 'https://www.seltim.ru/index.html',
    'atctrade': 'https://atctrade.ru/index.html',
    'regtorg': 'https://www.regtorg.com/index.html',
    'aukcioncenter': 'https://aukcioncenter.ru/index.html',
    'torgidv': 'https://torgidv.ru/index.html',
    'ptp_center': 'https://ptp-center.ru/index.html',
    'trade_place_vetp': 'https://xn-----6kcbaifbn4di5abenic8aq7kvd6a.xn--p1ai/index.html',
}

_serp_link = {
    'etp_profit_ru': 'https://www.etp-profit.ru/etp/trade/list.html',
    'ausib': 'https://ausib.ru/etp/trade/list.html',
    'seltim': 'https://www.seltim.ru/etp/trade/list.html',
    'atctrade': 'https://atctrade.ru/etp/trade/list.html',
    'regtorg': 'https://regtorg.com/etp/trade/list.html',
    'aukcioncenter': 'https://aukcioncenter.ru/etp/trade/list.html',
    'torgidv': 'https://torgidv.ru/etp/trade/list.html',
    'ptp_center': 'https://ptp-center.ru/etp/trade/list.html',
    'trade_place_vetp': 'https://торговая-площадка-вэтп.рф/etp/trade/list.html',
}

_lot_link = {
    'etp_profit_ru': 'https://www.etp-profit.ru/etp/trade/inner-view-lots.html?perspective=inline&id=',
    'ausib': 'https://ausib.ru/etp/trade/inner-view-lots.html?perspective=inline&id=',
    'seltim': 'https://www.seltim.ru/etp/trade/inner-view-lots.html?perspective=inline&id=',
    'atctrade': 'https://atctrade.ru/etp/trade/inner-view-lots.html?perspective=inline&id=',
    'regtorg': 'https://www.regtorg.com/etp/trade/inner-view-lots.html?perspective=inline&id=',
    'aukcioncenter': 'https://aukcioncenter.ru/etp/trade/inner-view-lots.html?perspective=inline&id=',
    'torgidv': 'https://torgidv.ru/etp/trade/inner-view-lots.html?perspective=inline&id=',
    'ptp_center': 'https://ptp-center.ru/etp/trade/inner-view-lots.html?perspective=inline&id=',
    'trade_place_vetp': 'https://торговая-площадка-вэтп.рф/etp/trade/inner-view-lots.html?perspective=inline&id=',
}

_doc_link = {
    'etp_profit_ru': 'https://www.etp-profit.ru/edoc/attachments/list.html?perspective=inline&id=',
    'ausib': 'https://ausib.ru/edoc/attachments/list.html?perspective=inline&id=',
    'seltim': 'https://www.seltim.ru/edoc/attachments/list.html?perspective=inline&id=',
    'atctrade': 'https://atctrade.ru/edoc/attachments/list.html?perspective=inline&id=',
    'regtorg': 'https://www.regtorg.com/edoc/attachments/list.html?perspective=inline&id=',
    'aukcioncenter': 'https://aukcioncenter.ru/edoc/attachments/list.html?perspective=inline&id=',
    'torgidv': 'https://torgidv.ru/edoc/attachments/list.html?perspective=inline&id=',
    'ptp_center': 'https://ptp-center.ru/edoc/attachments/list.html?perspective=inline&id=',
    'trade_place_vetp': 'https://торговая-площадка-вэтп.рф/edoc/attachments/list.html?perspective=inline&id=',
}

url_file = {
    'etp_profit_ru': 'https://www.etp-profit.ru',
    'ausib': 'https://ausib.ru',
    'seltim': 'https://www.seltim.ru',
    'atctrade': 'https://atctrade.ru',
    'regtorg': 'https://www.regtorg.com',
    'aukcioncenter': 'https://aukcioncenter.ru',
    'torgidv': 'https://torgidv.ru',
    'ptp_center': 'https://ptp-center.ru',
    'trade_place_vetp': 'https://xn-----6kcbaifbn4di5abenic8aq7kvd6a.xn--p1ai',
}

path_absolute = {
    'etp_profit_ru': f'{absolute_download_path}/etp_etp_profit_ru',
    'ausib': f'{absolute_download_path}/etp_ausib',
    'seltim': f'{absolute_download_path}/etp_seltim',
    'atctrade': f'{absolute_download_path}/etp_atctrade',
    'regtorg': f'{absolute_download_path}/etp_regtorg',
    'aukcioncenter': f'{absolute_download_path}/etp_aukcioncenter',
    'torgidv': f'{absolute_download_path}/etp_torgidv',
    'ptp_center': f'{absolute_download_path}/etp_ptp_center',
    'trade_place_vetp': f'{absolute_download_path}/etp_trade_place_vetp',
}

path_relative = {
    'etp_profit_ru': f'{relative_download_path}/etp_etp_profit_ru',
    'ausib': f'{relative_download_path}/etp_ausib',
    'seltim': f'{relative_download_path}/etp_seltim',
    'atctrade': f'{relative_download_path}/etp_atctrade',
    'regtorg': f'{relative_download_path}/etp_regtorg',
    'aukcioncenter': f'{relative_download_path}/etp_aukcioncenter',
    'torgidv': f'{relative_download_path}/etp_torgidv',
    'ptp_center': f'{relative_download_path}/etp_ptp_center',
    'trade_place_vetp': f'{relative_download_path}/etp_trade_place_vetp',
}