from scrapy import Request, FormRequest, Spider
from crawler_tenderstandartru.utils.config import _data_origin, _auction_trades, _offer_trades, _competition_trades, \
    search_url
from crawler_tenderstandartru.utils.headers import header as hd
from icecream import ic
from ..trades.app import Combo
import logging
from ..utils.search_param_data_auction import search_param as sp
from scrapy.spidermiddlewares.httperror import HttpError
from twisted.internet.error import DNSLookupError, TCPTimedOutError
from ..utils.work_with_text_and_number import make_float
from ..items import CrawlerTenderstandartruItem, CrawlerTenderstandartruItemLoader, CrawlerTransferTenderstandartruItem
from ..utils.working_with_time import return_parse_date
from abc import ABC
from itertools import chain
from ..utils.get_data_from_table import DbConnectCheckLots

__all__ = ['logging',
           'Request', 'FormRequest', 'Spider',
           '_data_origin', '_auction_trades', '_offer_trades', '_competition_trades',
           'hd',
           'ic',
           'Combo', 'sp', 'search_url',
           'HttpError', 'DNSLookupError', 'TCPTimedOutError',
           'make_float', 'return_parse_date',
           'CrawlerTenderstandartruItem', 'CrawlerTenderstandartruItemLoader', 'CrawlerTransferTenderstandartruItem',
           'chain', 'ABC', 'DbConnectCheckLots'
           ]
