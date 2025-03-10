from general_utils.config import *


def return_auction_link(_data_origin):
    auction_link = 'public/auctions-all/'
    return _data_origin + auction_link


def return_offer_link(_data_origin):
    offer_link = 'public/public-offers-all/'
    return _data_origin + offer_link


def return_compet_link(_data_origin):
    competition_link = 'public/contests-all/'
    return _data_origin + competition_link


start_date = format_parse_date(30, '%Y-%m-%d 0:0:-1')
data_origin = {
    'alfalot': 'https://bankrupt.alfalot.ru/',
    'arbbitlot': 'https://torgi.arbbitlot.ru/',
    'arbitat': 'http://arbitat.ru/',
    'bepspb': 'https://bepspb.ru/',
    'centrr': 'https://bankrupt.centerr.ru/',
    'etpu': 'https://bankrupt.etpu.ru/',
    'etpugra': 'http://etpugra.ru/',
    'ets24': 'http://bankrupt.ets24.ru/',
    'gloriaservice': 'https://gloriaservice.ru/',
    'meta_invest': 'http://meta-invest.ru/',
    'propertytrade': 'https://propertytrade.ru/',
    'selt_online': 'https://selt-online.ru/',
    'tender_one': 'https://bankrupt.tender.one/',
    'tendergarant': 'http://tendergarant.com/',
    'torgibankrot': 'https://torgibankrot.ru/',
    'utender': 'http://utender.ru/',
    'utpl': 'https://bankrupt.utpl.ru/',
    'zakazrf': 'http://bankrot.zakazrf.ru/',
}

path_absolute = dict()
path_relative = dict()
for name in data_origin.keys():
    path_absolute[name] = f'{absolute_download_path}/etp_{name}'
    path_relative[name] = f'{relative_download_path}/etp_{name}'
