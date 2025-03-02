from general_utils.config import *

tables = {
    'table_alfalot': 'lots_alfalot',
    'table_arbitat': 'lots_arbitat',
    'table_arbbitlot': 'lots_arbbitlot',
    'table_bankrot_zakazrf': 'lots_bankrot_zakazrf',
    'table_bankrupt_alfalot': 'lots_bankrupt_alfalot',
    'table_bankrupt_centrr': 'lots_bankrupt_centrr',
    'table_bankrupt_electro_torgi': 'lots_bankrupt_elec_tor',
    'table_bankrupt_etpu': 'lots_bankrupt_etpu',
    'table_bepspb': 'lots_bepspb',
    'table_ets24': 'lots_ets24',
    'table_etp_bankrotstvo': 'lots_etp_bankrotstvo',
    'table_etpugra': 'lots_etpugra',
    'table_gloriaservice': 'lots_gloriaservice',
    'table_meta_invest': 'lots_meta_invest',
    'table_propertytrade': 'lots_propertytrade',
    'table_selt_online': 'lots_selt_online',
    'table_tender_one': 'lots_tender_one',
    'table_tendergarant': 'lots_tendergarant',
    'table_torgibankrot': 'lots_torgibankrot',
    'table_uralbidin': 'lots_uralbidin',
    'table_utender': 'lots_utender',
    'table_utpl': 'lots_utpl',
    'table_vertrades': 'lots_vertrades'
}

start_date = format_parse_date(30, '%Y-%m-%d 0:0:-1')

data_origin = {
    'alfalot': 'https://bankrupt.alfalot.ru/',
    'arbitat': 'http://arbitat.ru/',
    'arbbitlot': 'https://torgi.arbbitlot.ru/',
    'bankrot_zakazrf': 'http://bankrot.zakazrf.ru/',
    'bankrupt_alfalot': 'https://bankrupt.alfalot.ru/',
    'bankrupt_centrr': 'https://bankrupt.centerr.ru/',
    'bankrupt_electro_torgi': 'https://bankrupt.electro-torgi.ru/',
    'bankrupt_etpu': 'https://bankrupt.etpu.ru/',
    'bepspb': 'https://bepspb.ru/',
    'etp_bankrotstvo': 'https://www.etp-bankrotstvo.ru/',
    'ets24': 'http://bankrupt.ets24.ru/',
    'etpugra': 'http://etpugra.ru/',
    'gloriaservice': 'https://gloriaservice.ru/',
    'meta_invest': 'http://meta-invest.ru/',
    'propertytrade': 'https://propertytrade.ru/',
    'selt_online': 'https://selt-online.ru/',
    'tender_one': 'https://bankrupt.tender.one/',
    'tendergarant': 'http://tendergarant.com/',
    'torgibankrot': 'https://torgibankrot.ru/',
    'uralbidin': 'https://uralbidin.ru/',
    'utender': 'http://utender.ru/',
    'utpl': 'https://bankrupt.utpl.ru/',
    'vertrades': 'https://vertrades.ru/bankrupt/'
}

def return_auction_link(_data_origin):
    auction_link = 'public/auctions-all/'
    return _data_origin + auction_link


def return_offer_link(_data_origin):
    offer_link = 'public/public-offers-all/'
    return _data_origin + offer_link


def return_compet_link(_data_origin):
    competition_link = 'public/contests-all/'
    return _data_origin + competition_link


path_absolute = {
    'alfalot': f'{absolute_download_path}/etp_alfalot',
    'arbitat': f'{absolute_download_path}/etp_arbitat',
    'arbbitlot': f'{absolute_download_path}/etp_arbbitlot',
    'bankrot_zakazrf': f'{absolute_download_path}/etp_bankrot_zakazrf',
    'bankrupt_alfalot': f'{absolute_download_path}/etp_bankrupt_alfalot',
    'bankrupt_centrr': f'{absolute_download_path}/etp_bankrupt_centrr',
    'bankrupt_electro_torgi': f'{absolute_download_path}/etp_bankrupt_electro_torgi',
    'bankrupt_etpu': f'{absolute_download_path}/etp_bankrupt_etpu',
    'bepspb': f'{absolute_download_path}/etp_bepspb',
    'ets24': f'{absolute_download_path}/etp_ets24',
    'etp_bankrotstvo': f'{absolute_download_path}/etp_bepspb',
    'etpugra': f'{absolute_download_path}/etp_etpugra',
    'gloriaservice': f'{absolute_download_path}/etp_gloriaservice',
    'meta_invest': f'{absolute_download_path}/etp_meta_invest',
    'propertytrade': f'{absolute_download_path}/etp_propertytrade',
    'selt_online': f'{absolute_download_path}/etp_selt_online',
    'tender_one': f'{absolute_download_path}/etp_bankrupt_tender_one',
    'tendergarant': f'{absolute_download_path}/etp_tendergarant',
    'torgibankrot': f'{absolute_download_path}/etp_torgibankrot',
    'uralbidin': f'{absolute_download_path}/etp_uralbidin',
    'utender': f'{absolute_download_path}/etp_utender',
    'utpl': f'{absolute_download_path}/etp_utpl',
    'vertrades': f'{absolute_download_path}/etp_vertrades'
}

path_relative = {
    'alfalot': f'{relative_download_path}/etp_alfalot',
    'arbitat': f'{relative_download_path}/etp_arbitat',
    'arbbitlot': f'{relative_download_path}/etp_arbbitlot',
    'bankrot_zakazrf': f'{relative_download_path}/etp_bankrot_zakazrf',
    'bankrupt_alfalot': f'{relative_download_path}/etp_bankrupt_alfalot',
    'bankrupt_centrr': f'{relative_download_path}/etp_bankrupt_centrr',
    'bankrupt_electro_torgi': f'{relative_download_path}/etp_bankrupt_electro_torgi',
    'bankrupt_etpu': f'{relative_download_path}/etp_bankrupt_etpu',
    'bepspb': f'{relative_download_path}/etp_bepspb',
    'ets24': f'{relative_download_path}/etp_ets24',
    'etp_bankrotstvo': f'{relative_download_path}/etp_bepspb',
    'etpugra': f'{relative_download_path}/etp_etpugra',
    'gloriaservice': f'{relative_download_path}/etp_gloriaservice',
    'meta_invest': f'{relative_download_path}/etp_meta_invest',
    'propertytrade': f'{relative_download_path}/etp_propertytrade',
    'selt_online': f'{relative_download_path}/etp_selt_online',
    'tender_one': f'{relative_download_path}/etp_bankrupt_tender_one',
    'tendergarant': f'{relative_download_path}/etp_tendergarant',
    'torgibankrot': f'{relative_download_path}/etp_torgibankrot',
    'uralbidin': f'{relative_download_path}/etp_uralbidin',
    'utender': f'{relative_download_path}/etp_utender',
    'utpl': f'{relative_download_path}/etp_utpl',
}
