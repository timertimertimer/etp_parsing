# -*- coding: utf-8 -*-
import re

from scrapy.spiders import CrawlSpider
from scrapy_splash import SplashRequest, SplashFormRequest, SlotPolicy
from scrapy.spidermiddlewares.httperror import HttpError
from bs4 import BeautifulSoup as BS
from twisted.internet.error import DNSLookupError
from twisted.internet.error import TimeoutError, TCPTimedOutError
import pandas as pd
import time

from ..items import CrawlerMetsItem, MetsItemLoader
from ..trades.combo import ComposeTrades
from ..locators.spider_locators import LocatorSpider
from ..utils.config import url_start, start_time_from, periods_, time_delta, data_origin_url, format_period
from ..utils.get_data_from_table import DbConnectCheckLots
from ..utils.manage_spider import *
from ..utils.data_for_requests import data_search, script_lua, script_lua_lot
from ..utils.working_with_time import *
from ..utils.working_with_url import UrlConfig
import logging
from ..settings import DEFAULT_REQUESTS_HEADERS
from icecream import ic

logger = logging.getLogger(__name__)


class MetsSpider(CrawlSpider, ComposeTrades):
    name = 'mets'
    #     http_user = 'parser'
    #     http_pass = 'gs:0Kh7%bD5$gBh}'
    # allowed_domains = ['m-ets.ru']
    start_url = url_start

    def __init__(self, *a, **kw):
        super(MetsSpider).__init__(*a, **kw)
        self.loc = LocatorSpider
        self.url = UrlConfig()
        self.db_check = DbConnectCheckLots()
        self.previous_lots = self.db_check.get_latest_lot()

    def start_requests(self):
        yield SplashRequest(self.start_url, self.parse_main, endpoint='execute',
                            cache_args=['lua_source'], args={'lua_source': script_lua},
                            slot_policy=SlotPolicy.PER_DOMAIN, splash_headers=DEFAULT_REQUESTS_HEADERS,
                            session_id=1,
                            errback=self.errback_httpbin)

    def parse_main(self, response):
        """get response set periods to parse and set dates to query data"""
        sid = response.xpath(self.loc.sid_loc).get()
        sid = BS(str(sid), features='lxml').get_text()
        date_range = pd.date_range(start_time_from, periods=periods_, freq=format_period)
        trade_links = set()
        for start_time in date_range:
            start_time = start_time.strftime('%d.%m.%Y')
            data_search['submit'] = sid
            data_search['date_nach_ot'] = start_time
            data_search['date_nach_do'] = ''  # f'{increase_time_days(start_time, time_delta)}'
            time.sleep(1.0)
            yield SplashFormRequest(url=response.url, formdata=data_search, method='GET',
                                    callback=self.parse_serp, errback=self.errback_httpbin,
                                    meta={'current_page': 1,
                                          'data_search': data_search, 'trade_links': trade_links, 'count_response': 0},
                                    endpoint='execute',
                                    cache_args=['lua_source'], args={'lua_source': script_lua},
                                    slot_policy=SlotPolicy.PER_DOMAIN,
                                    session_id=1
                                    )

    def parse_serp(self, response):
        logger.info(f'{response.url}')
        trade_links = response.meta['trade_links']
        time.sleep(1.0)
        amount_page = response.xpath(self.loc.count_pagination_loc).get()
        # logger.info(f'{amount_page}!!!!!!!!!!!!!')
        links_to_trade = response.xpath(self.loc.link_to_trade_loc).getall()
        count_response = response.meta['count_response']
        current_page = response.meta['current_page']
        while count_response < 5:
            if amount_page:
                amount_page = int(amount_page)
                break
            elif True:
                break
            elif count_response < 5:
                count_response += 1
                yield SplashFormRequest(url=response.url, formdata=data_search, method='GET',
                                        callback=self.parse_serp, errback=self.errback_httpbin,
                                        meta={'current_page': current_page,
                                              'data_search': response.meta['data_search'],
                                              'trade_links': response.meta['trade_links'],
                                              'count_response': count_response},
                                        endpoint='execute',
                                        cache_args=['lua_source'], args={'lua_source': script_lua},
                                        slot_policy=SlotPolicy.PER_DOMAIN,
                                        session_id=1
                                        )
            else:
                logger.critical('ERROR PAGINATION')
                count_response = 100
                amount_page = 0

        for link in links_to_trade:
            link = BS(str(link), features='lxml').find('a').get('href')
            link = self.url.url_join(data_origin_url, link)
            link = ''.join(re.sub(r'\#lot\d+', '', link)).strip()
            # if l  not None
            if link:
                link = re.sub(r'&.+$', '', link).strip()
                trade_links.add(link)
        _data_search = response.meta['data_search']
        if amount_page > 1 and int(current_page) < amount_page:
            current_page = int(current_page) + 1
            _data_search['page'] = str(current_page)
            url_pagination = re.sub(r'&page=\d+$', '', response.url)
            url_pagination = url_pagination + '&page=' + _data_search['page']
            time.sleep(0.5)
            yield SplashRequest(url_pagination, callback=self.parse_serp, errback=self.errback_httpbin,
                                meta={'current_page': current_page, 'data_search': _data_search,
                                      'trade_links': trade_links, 'count_response': count_response},
                                endpoint='execute',
                                cache_args=['lua_source'], args={'lua_source': script_lua},
                                slot_policy=SlotPolicy.PER_DOMAIN,
                                session_id=1,
                                splash_headers={
                                    ':authority': 'm-ets.ru',
                                    ':method': 'GET',
                                    ':path': '/alive',
                                    ':scheme': 'https',
                                    'accept': '*/*',
                                    'accept-encoding': 'gzip, deflate, br',
                                    'accept-language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7',
                                    'pragma': 'no-cache',
                                    'referer': response.url,
                                    'sec-fetch-dest': 'empty',
                                    'sec-fetch-mode': 'cors',
                                    'sec-fetch-site': 'same-origin',
                                    'User-Agent': response.request.headers['User-Agent'],
                                    'x-requested-with': 'XMLHttpRequest'

                                })

        else:
            trade_links = set(trade_links)
            for link in trade_links:
                yield SplashRequest(url=self.url.parse_url(link), dont_filter=True,
                                    callback=self.sort_trades, errback=self.errback_httpbin, endpoint='execute',
                                    cache_args=['lua_source'], args={'lua_source': script_lua_lot},
                                    slot_policy=SlotPolicy.PER_DOMAIN, magic_response=True, method='GET',
                                    session_id=1, splash_headers={
                        ':authority': 'm-ets.ru',
                        ':method': 'GET',
                        ':path': '/search',
                        ':scheme': 'https',
                        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
                        'accept-encoding': 'gzip, deflate, br',
                        'accept-language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7',
                        'referer': response.url,
                        'upgrade-insecure-requests': '1',
                        'User-Agent': DEFAULT_REQUESTS_HEADERS['User-Agent']
                    })

    # def start_requests(self):
    #    test_link_lst = ['https://mets.ru/generalView?id=252319022']
    #    for link in test_link_lst:
    #        yield SplashRequest(url=link, dont_filter=True,
    #                            callback=self.sort_trades, errback=self.errback_httpbin, endpoint='execute',
    #                            cache_args=['lua_source'], args={'lua_source': script_lua_lot},
    #                            slot_policy=SlotPolicy.PER_DOMAIN, magic_response=True, method='GET',
    #                            session_id=1, splash_headers={
    #                ':authority': 'm-ets.ru',
    #                ':method': 'GET',
    #                ':path': '/generalView?id=249837739',
    #                ':scheme': 'https',
    #                'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
    #                'accept-encoding': 'gzip, deflate, br',
    #                'accept-language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7',
    #
    #                'upgrade-insecure-requests': '1',
    #               'User-Agent': DEFAULT_REQUESTS_HEADERS['User-Agent']
    #           })

    def sort_trades(self, response):
        comp = ComposeTrades(response_=response)
        trading_type_ = comp.offer.trading_number
        trading_type = sort_trading_type(trading_type_)
        trading_form = get_trading_form(trading_type_)
        if str(trading_type) == 'auction':
            return self.parse_auction(response=response,
                                      trading_type=trading_type, trading_form=trading_form)

        if str(trading_type) == 'competition':
            return self.parse_auction(response=response,
                                      trading_type=trading_type, trading_form=trading_form)

        if str(trading_type) == 'offer':
            return self.parse_offer(response=response,
                                    trading_type=trading_type, trading_form=trading_form)

    def parse_auction(self, response, trading_type, trading_form):
        """getting data from trade - auction"""
        comp = ComposeTrades(response_=response)
        for lot_name in comp.offer.count_lots:
            lot_name = comp.offer.get_lot_title(lot_name)
            loader = MetsItemLoader(CrawlerMetsItem(), response=response)
            loader.add_value('data_origin', comp.offer.data_origin)
            loader.add_value('trading_id', comp.offer.trading_id)
            loader.add_value('trading_link', comp.offer.trading_link)
            loader.add_value('trading_number', comp.offer.trading_number)
            loader.add_value('trading_type', trading_type)
            loader.add_value('trading_form', trading_form)
            trading_number = loader.get_collected_values('trading_number')
            loader.add_value('trading_org', comp.offer.trading_org)
            loader.add_value('trading_org_inn', None)
            loader.add_value('trading_org_contacts',
                             comp.offer.trading_org_contacts)
            loader.add_value('msg_number', comp.offer.msg_number)
            loader.add_value('case_number', comp.offer.case_number)
            loader.add_value('debtor_inn', comp.offer.debitor_inn)
            loader.add_value('arbit_manager', comp.offer.arbitr_manager_org)
            loader.add_value('arbit_manager_inn', comp.offer.arbitr_inn)
            loader.add_value('arbit_manager_org', comp.offer.arbitr_org)
            # PARSE LOT
            lot_number = comp.offer.lot_number(lot_name)
            loader.add_value('status', comp.offer.status(lot_number))
            loader.add_value('lot_link', str(
                response.url) + '#lot' + lot_number)
            data_lot = (re.sub(r'&lot=\d+$', '', str(response.url)), lot_number)
            if data_lot not in self.previous_lots:
                loader.add_value('lot_number', lot_number)
                loader.add_value('short_name', comp.offer.short_name(lot_number))
                loader.add_value('lot_info', comp.offer.lot_info(lot_number))
                loader.add_value('property_information',
                                 comp.offer.property_info(lot_number))
                loader.add_value('start_price', comp.offer.start_price(lot_number))
                loader.add_value('step_price', comp.auc.step_price(trading_number, lot_number))
                loader.add_value('start_date_requests',
                                 comp.auc.start_date_request)
                loader.add_value('end_date_requests',
                                 comp.auc.end_date_request)
                loader.add_value('start_date_trading',
                                 comp.auc.start_date_trading)
                loader.add_value('end_date_trading',
                                 comp.auc.end_date_trading)
                loader.add_value('periods', None)
                files_lot = comp.offer.download_lot_files(comp.offer.trading_id, lot_number)
                files_general = comp.offer.download_general_files(comp.offer.trading_id)
                loader.add_value('files', {'general': files_general, 'lot': files_lot})
                loader.add_value('created_at', return_parse_date())
                yield loader.load_item()

    def parse_offer(self, response, trading_type, trading_form):
        """getting data from trade - offer"""
        comp = ComposeTrades(response_=response)
        for lot_name in comp.offer.count_lots:
            lot_name = comp.offer.get_lot_title(lot_name)
            loader = MetsItemLoader(CrawlerMetsItem(), response=response)
            loader.add_value('data_origin', comp.offer.data_origin)
            loader.add_value('trading_id', comp.offer.trading_id)
            loader.add_value('trading_link', comp.offer.trading_link)
            loader.add_value('trading_number', comp.offer.trading_number)
            loader.add_value('trading_type', trading_type)
            loader.add_value('trading_form', trading_form)
            loader.add_value('trading_org', comp.offer.trading_org)
            loader.add_value('trading_org_inn', None)
            loader.add_value('trading_org_contacts',
                             comp.offer.trading_org_contacts)
            loader.add_value('msg_number', comp.offer.msg_number)
            loader.add_value('case_number', comp.offer.case_number)
            loader.add_value('debtor_inn', comp.offer.debitor_inn)
            loader.add_value('arbit_manager', comp.offer.arbitr_manager_org)
            loader.add_value('arbit_manager_inn', comp.offer.arbitr_inn)
            loader.add_value('arbit_manager_org', comp.offer.arbitr_org)
            # PARSE LOT
            lot_number = comp.offer.lot_number(lot_name)
            loader.add_value('status', comp.offer.status(lot_number))
            loader.add_value('lot_link', str(
                response.url) + '#lot' + lot_number)
            data_lot = (re.sub(r'&lot=\d+$', '', str(response.url)), lot_number)
            if data_lot not in self.previous_lots:
                loader.add_value('lot_number', lot_number)
                loader.add_value('short_name', comp.offer.short_name(lot_number))
                loader.add_value('lot_info', comp.offer.lot_info(lot_number))
                loader.add_value('property_information',
                                 comp.offer.property_info(lot_number))
                loader.add_value('start_price', comp.offer.start_price(lot_number))
                loader.add_value('start_date_requests',
                                 comp.offer.start_date_request(lot_number))
                loader.add_value('end_date_requests',
                                 comp.offer.end_date_request(lot_number))
                loader.add_value('start_date_trading',
                                 comp.offer.start_date_request(lot_number))
                loader.add_value('end_date_trading',
                                 comp.offer.end_date_request(lot_number))
                loader.add_value('periods', comp.offer.get_period(lot_number))
                files_lot = comp.offer.download_lot_files(comp.offer.trading_id, lot_number)
                files_general = comp.offer.download_general_files(comp.offer.trading_id)
                loader.add_value('files', {'general': files_general, 'lot': files_lot})
                loader.add_value('created_at', return_parse_date())
                yield loader.load_item()

    def errback_httpbin(self, failure):
        # logs failures

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
