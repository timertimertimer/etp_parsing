# -*- coding: utf-8 -*-
import logging

import pandas as pd
from bs4 import BeautifulSoup as BS
from icecream import ic
from scrapy import FormRequest, Request
from scrapy.spidermiddlewares.httperror import HttpError
from scrapy.spiders import CrawlSpider
from scrapy_splash import SplashRequest, SlotPolicy
from twisted.internet.error import DNSLookupError
from twisted.internet.error import TimeoutError, TCPTimedOutError
import json
import xmltodict
import pprint

from ..items import SberbankItemLoader, CrawlerSberbankItem
from ..locators.locator_spider import LocatorSpider
from ..settings import DEFAULT_REQUESTS_HEADERS
from ..trades.app import ComposeTrades
from ..utils.config import *
from ..utils.data_for_requests import script_lua_first_req, xml_data, script_trading, script_lot, script_lot_nojs, \
    simle_script_lua, simle2_script_lua, headers, xml_request_data
from ..utils.get_data_from_table import DbConnectCheckLots
from ..utils.manage_spider import *
from ..utils.work_with_text_and_number import dedent_func
from ..utils.working_with_time import increase_time_days, format_time, return_parse_date
from ..utils.working_with_url import UrlConfig

logger = logging.getLogger(__name__)

lst_links = list()
pp = pprint.PrettyPrinter(indent=4)


class SberbankNewSpider(CrawlSpider, ComposeTrades):
    name = 'sberbank_new'
    start_urls = ['https://utp.sberbank-ast.ru/Bankruptcy/SearchQuery/BidList']

    def __init__(self, *args, **kwargs):
        super(SberbankNewSpider).__init__(*args, **kwargs)
        self.loc = LocatorSpider
        self.u_ = UrlConfig
        self.db_check = DbConnectCheckLots()
        self.previous_lots = self.db_check.get_latest_lot()

    def start_requests(self):
        date_range = pd.date_range(start_time_from, periods=periods_, freq=format_period)
        for start_date in date_range:
            start_date = start_date.strftime('%d.%m.%Y %H:%M')
            end_date = increase_time_days(start_date, time_delta)
            yield FormRequest(
                self.start_urls[0], self.make_second_request, formdata={
                    'xmlData': xml_request_data.format(start_date=start_date, end_date=end_date, total=100),
                    'orgId': '0', 'buId': '0', 'personId': '0', 'buMainId': '0', 'personMainId': '0'
                }, meta={'start_date': start_date, 'end_date': end_date}
            )

    def make_second_request(self, response, **kwargs):
        soup = BS(json.loads(response.text)['data']['Data']['tableXml'], 'lxml-xml')
        data = xmltodict.parse(str(soup))['datarow']
        total = int(data['total']['value'])
        yield FormRequest(
            self.start_urls[0], self.parse_table, formdata={
                'xmlData': xml_request_data.format(
                    start_date=response.meta['start_date'], end_date=response.meta['end_date'], total=total
                ), 'orgId': '0', 'buId': '0', 'personId': '0', 'buMainId': '0', 'personMainId': '0'
            },
        )

    def parse_table(self, response):
        soup = BS(json.loads(response.text)['data']['Data']['tableXml'], 'lxml-xml')
        data = xmltodict.parse(str(soup))['datarow']
        trades = set(lot['_source']['objectHrefTerm'] for lot in data['hits'])
        for trade in trades:
            path = trade.removeprefix('https://utp.sberbank-ast.ru')
            yield FormRequest(
                'https://utp.sberbank-ast.ru/api/Processing/main', self.parse_trade, method='POST',
                body=json.dumps({'actionCode': path, 'windowCode': path, 'actionType': 'template'}),
                meta={'trade': trade}
            )

    def parse_trade(self, response):
        trading_link = response.meta['trade']
        data = json.loads(response.text)
        combo = ComposeTrades(data, trading_link)
        lst_link_to_lots = list()
        try:
            lst_dict_lot_links = data['Purchase']['BidsPanel']['Bids']['Bid']
        except:
            lst_dict_lot_links = None
            logger.error(f'{trading_link} :: INVALID DATA LOT OR NO LOT')
        if isinstance(lst_dict_lot_links, list):
            lst_link_to_lots = list(map(lambda x: x['BidId'], lst_dict_lot_links))
        if isinstance(lst_dict_lot_links, dict):
            lst_link_to_lots = data['Purchase']['BidsPanel']['Bids']['Bid']['BidId'].split()
        for link in lst_link_to_lots:
            _link = re.sub(part_path_to_trade, part_path_to_lot, response.meta['trade'])
            _link = re.sub(r'\d+$', link, _link)
            loader = SberbankItemLoader(CrawlerSberbankItem(), response=response)
            loader.add_value('data_origin', data_origin_url)
            loader.add_value('trading_id', combo.auc.trading_id)
            loader.add_value('trading_link', trading_link)
            loader.add_value('trading_number', combo.auc.trading_number_auc)
            loader.add_value('trading_type', combo.auc.trading_type_auc)
            loader.add_value('trading_form', combo.auc.trading_form_auc)
            loader.add_value('msg_number', combo.auc.get_msg_number)
            loader.add_value('trading_org', combo.auc.trading_org_auc)
            loader.add_value('trading_org_inn', combo.auc.trading_org_inn)
            loader.add_value('trading_org_contacts', combo.auc.trading_org_contacts)
            loader.add_value('case_number', combo.auc.get_case_number)
            loader.add_value('debtor_inn', combo.auc.get_debitor_inn)
            loader.add_value('arbit_manager', combo.auc.get_arbitr_manager)
            loader.add_value('arbit_manager_inn', combo.auc.get_arbitr_manager_inn)
            loader.add_value('arbit_manager_org', combo.auc.get_arbitr_manager_org)
            if combo.auc.trading_type_auc == 'auction':
                loader.add_value('start_date_requests', combo.auc.get_start_date_requests)
                loader.add_value('end_date_requests', combo.auc.get_end_date_requests)
                loader.add_value('start_date_trading', combo.auc.get_start_date_trading)
                loader.add_value('end_date_trading', combo.auc.get_end_date_trading)
            url = _link
            if url not in self.previous_lots:
                files_general = combo.offer.download_general(
                    combo.auc.trading_id, data['Purchase']['PurchaseinfoPanel']['ContractInfo']['contractdoc']['file']
                )
                path = url.removeprefix('https://utp.sberbank-ast.ru')
                yield FormRequest(
                    'https://utp.sberbank-ast.ru/api/Processing/main', self.parse_lot, method='POST',
                    body=json.dumps({'actionCode': path, 'windowCode': path, 'actionType': 'template'}),
                    meta={'lot': url},
                    cb_kwargs={'loader': loader, 'files': files_general}
                )

    def parse_lot(self, response, loader, files):
        lot_link = response.meta['lot']
        data = json.loads(response.text)
        combo = ComposeTrades(data, lot_link)
        loader.add_value('lot_id', combo.auc.get_lot_id)
        loader.add_value('lot_link', lot_link)
        loader.add_value('lot_number', combo.auc.get_lot_number)
        loader.add_value('short_name', combo.auc.get_short_name)
        loader.add_value('lot_info', combo.auc.get_lot_info)
        loader.add_value('property_information', combo.auc.get_property_info)
        if loader.get_output_value('trading_type') == 'auction':
            loader.add_value('start_price', combo.auc.get_start_price)
            loader.add_value('step_price', combo.auc.get_step_price)
        else:
            loader.add_value('start_date_requests', combo.offer.start_date_request)
            loader.add_value('end_date_requests', combo.offer.end_date_request)
            loader.add_value('start_date_trading', combo.offer.start_date_trading)
            loader.add_value('end_date_trading', combo.offer.end_date_trading)
            loader.add_value('start_price', combo.offer.start_price)
            loader.add_value('periods', combo.offer.get_periods)
        docs = data['BidView']['Bids']['BidDebtorInfo'].get('BidAdditionalDocEDS', [])
        if docs:
            docs = [docs['file']] if isinstance(docs['file'], dict) else docs['file']
        photos = data['BidView']['Bids']['BidDebtorInfo'].get('BidPicture', [])
        if photos:
            photos = [photos['file']] if isinstance(photos['file'], dict) else photos['file']
        files_lot = combo.offer.download_general(combo.auc.get_lot_id, docs + photos)
        loader.add_value('files', {'general': files, 'lot': files_lot})
        loader.add_value('created_at', return_parse_date())
        yield loader.load_item()

    def errback_httpbin(self, failure):
        self.logger.error(repr(failure))
        if failure.check(HttpError):
            response = failure.value.response
            self.logger.error("HttpError occurred on %s", response.url)

        elif failure.check(DNSLookupError):
            request = failure.request
            self.logger.error("DNSLookupError occurred on %s", request.url)

        elif failure.check(TimeoutError, TCPTimedOutError):
            request = failure.request
            self.logger.error("TimeoutError occurred on %s", request.url)
