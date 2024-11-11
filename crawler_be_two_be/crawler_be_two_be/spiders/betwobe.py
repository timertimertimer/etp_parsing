# -*- coding: utf-8 -*-
import copy
import logging
from abc import ABC
from itertools import chain

import pandas as pd
from icecream import ic
from scrapy.spidermiddlewares.httperror import HttpError
from scrapy.spiders import Spider
from scrapy_splash import SplashRequest, SlotPolicy
from twisted.internet.error import DNSLookupError, TCPTimedOutError

from ..utils.data_for_requests import script_lua_nojs, script_lua_nojs2
from ..items import CrawlerBeTwoBeItem, CrawlerBeTwoBeItemLoader, CrawlerBeTwoBeTransferItem
from ..manage_spider.app import Combo
from ..settings import DEFAULT_REQUEST_HEADERS
from ..utils.config import start_time_from, periods_, freq_, time_delta, _data_origin
# from crawler_be_two_be.settings import DEFAULT_REQUEST_HEADERS
from ..utils.param_query import param_auc_redirect
from ..utils.work_with_text_and_number import cookie_parser, return_main_cookies
from ..utils.working_with_time import increase_time_days, return_parse_date

logger = logging.getLogger(__name__)


class BetwobeSpider(Spider, ABC):
    name = 'betwobe'
    start_url = 'https://b2b-center.ru/market/'

    COUNT_MAX = 50

    custom_settings = {
        'CLOSESPIDER_PAGECOUNT': COUNT_MAX
    }

    # def start_requests(self):
    #     for u in ['https://www.b2b-center.ru/market/kvartira-ploshchadiu-70-3-kv-m-raspolozhennaia-na-6-etazhe-v-zhilom-dome/tender-2491500/#btid=2&sqh=0fdd2537747b341ec9978afba7c76c021c5cdfb2&tsid=2491500015']:
    #         yield SplashRequest(u, self.parse_auction,
    #                             endpoint='execute',
    #                             cache_args=['lua_source'], args={'lua_source': script_lua_nojs},
    #                             slot_policy=SlotPolicy.PER_DOMAIN, dont_send_headers=True,
    #                             errback=self.errback_httpbin)

    def start_requests(self):
        yield SplashRequest(self.start_url, self.start_requests_query,
                            endpoint='execute',
                            cache_args=['lua_source'], args={'lua_source': script_lua_nojs, 'headers': DEFAULT_REQUEST_HEADERS},
                            slot_policy=SlotPolicy.PER_DOMAIN,
                            errback=self.errback_httpbin)

    def start_requests_query(self, response):
        """ make quests for week period """
        combo = Combo(response_=response)
        date_range = pd.date_range(start_time_from, periods=periods_, freq=freq_)
        for start_time in date_range:
            start_time = start_time.strftime('%d.%m.%Y')
            date_to = f'{increase_time_days(start_time, time_delta)}'
            link = combo.search.get_link_redirect_query(start_date=start_time, date_end=date_to,
                                                        param_=param_auc_redirect)
            logger.info(f'Start_date {start_time}, Time to {date_to}')
            yield SplashRequest(url=link, callback=self.parse_search_page,
                                endpoint='execute', dont_filter=True,
                                cache_args=['lua_source'], args={'lua_source': script_lua_nojs, 'headers': DEFAULT_REQUEST_HEADERS},
                                slot_policy=SlotPolicy.PER_DOMAIN,
                                errback=self.errback_httpbin, cb_kwargs={'current_page': 1, 'start': start_time,
                                                                         'end_time': date_to})

    def parse_search_page(self, response, current_page, start, end_time):
        """ parse page with result after query and get links to tading page """
        combo = Combo(response_=response)
        links_to_trading_page = combo.search.get_links_to_trading_page()
        cookie = response.data['cookies']
        cookie = return_main_cookies(cookie)
        for link in links_to_trading_page:
            yield SplashRequest(url=link, callback=self.parse_auction, errback=self.errback_page2,
                                endpoint='execute', dont_filter=True,
                                cache_args=['lua_source'], args={'lua_source': script_lua_nojs2, 'headers': DEFAULT_REQUEST_HEADERS},
                                slot_policy=SlotPolicy.PER_DOMAIN,
                                cookies=cookie_parser(cookie)
                                )
        if pagi := combo.search.check_if_pagination():
            next_page = combo.search.next_page(pagi)
            if next_page > current_page:
                current_page += 1
                param = copy.deepcopy(param_auc_redirect)
                param['from'] = int(current_page) * 10
                link = combo.search.get_link_redirect_query(start_date=start, date_end=end_time,
                                                            param_=param)
                yield SplashRequest(url=link, callback=self.parse_search_page,
                                    endpoint='execute', dont_filter=True,
                                    cache_args=['lua_source'], args={'lua_source': script_lua_nojs, 'headers': DEFAULT_REQUEST_HEADERS},
                                    slot_policy=SlotPolicy.PER_DOMAIN,
                                    errback=self.errback_httpbin,
                                    cb_kwargs={'current_page': current_page, 'start': start,
                                               'end_time': end_time})
        # with open('response.txt', 'w') as f:
        #     f.write(response.body.decode('utf-8'))

    def parse_auction(self, response):
        combo = Combo(response_=response)
        transfer = CrawlerBeTwoBeTransferItem()
        transfer['data_origin'] = _data_origin['b2b']
        transfer['trading_id'] = combo.trade.get_trading_id()
        transfer['trading_link'] = response.url
        transfer['trading_number'] = combo.trade.get_trading_number()
        transfer['trading_type'] = 'auction'
        transfer['trading_form'] = combo.trade.get_trading_form()
        transfer['msg_number'] = combo.trade.get_msg_number()
        transfer['case_number'] = combo.trade.get_case_number()
        transfer['debtor_inn'] = combo.trade.get_debtor_inn()
        transfer['arbit_manager'] = combo.trade.get_arbitr_name()
        transfer['arbit_manager_inn'] = combo.trade.get_arbitr_inn()
        transfer['arbit_manager_org'] = combo.trade.get_arbitr_company()
        transfer['property_information'] = combo.trade.get_property_info()
        transfer['start_date_requests'] = combo.trade.get_start_date_request_auc()
        transfer['end_date_requests'] = combo.trade.get_end_date_request_auc()
        transfer['start_date_trading'] = combo.trade.get_start_date_trading_auc()
        general_docs = combo.general.download_general(_id=''.join(transfer['trading_id']))
        list_with_general_file_names = combo.general.lst_files_names(**general_docs)
        link_to_organizer = combo.trade.get_organizer_link()
        url_to_lot = combo.trade.get_url_lot_tab()
        yield SplashRequest(url=link_to_organizer, callback=self.organizer_page, errback=self.errback_page2,
                            endpoint='execute', dont_filter=True,
                            cache_args=['lua_source'], args={'lua_source': script_lua_nojs2, 'headers': DEFAULT_REQUEST_HEADERS},
                            slot_policy=SlotPolicy.PER_DOMAIN,
                            cb_kwargs={'url_to_lot': url_to_lot,
                                       'transfer': transfer,
                                       'general_docs': general_docs,
                                       'general_names': list_with_general_file_names})

        # ic(combo.trade.get_organizer_link())

    def organizer_page(self, response, url_to_lot, transfer, general_docs, general_names):
        """ parse organizer page """
        combo = Combo(response_=response)
        transfer['trading_org'] = combo.org.get_name()
        transfer['trading_org_inn'] = combo.org.get_inn(arbitr_name=transfer['arbit_manager'],
                                                        arbitr_inn=transfer['arbit_manager_inn'])

        yield SplashRequest(url=url_to_lot, callback=self.parse_lot_tab, errback=self.errback_page2,
                            endpoint='execute', dont_filter=True,
                            cache_args=['lua_source'], args={'lua_source': script_lua_nojs2, 'headers': DEFAULT_REQUEST_HEADERS},
                            slot_policy=SlotPolicy.PER_DOMAIN,  cb_kwargs={'transfer': transfer,
                                                                                                  'general_docs': general_docs,
                                                                                                  'general_names': general_names})

    def parse_lot_tab(self, response, transfer, general_docs, general_names):
        """ parse tab with lots links. Fetch links & follow to lot page """
        combo = Combo(response_=response)
        links = combo.lt.get_links_to_lot()
        for link in links:
            link = combo.trade.complete_link_to_lot(link)
            yield SplashRequest(url=link, callback=self.parse_auction_lot, errback=self.errback_page2,
                                endpoint='execute', dont_filter=True,
                                cache_args=['lua_source'], args={'lua_source': script_lua_nojs2, 'headers': DEFAULT_REQUEST_HEADERS},
                                slot_policy=SlotPolicy.PER_DOMAIN,
                                cb_kwargs={'transfer': transfer, 'general_docs': general_docs,
                                           'general_names': general_names})

        if next_page := combo.lt.pagination_tab_lots():
            yield SplashRequest(url=next_page, callback=self.parse_lot_tab, errback=self.errback_page2,
                                endpoint='execute', dont_filter=True,
                                cache_args=['lua_source'], args={'lua_source': script_lua_nojs2, 'headers': DEFAULT_REQUEST_HEADERS},
                                slot_policy=SlotPolicy.PER_DOMAIN,
                                cb_kwargs={'transfer': transfer,
                                           'general_docs': general_docs,
                                           'general_names': general_names})

    def parse_auction_lot(self, response, transfer, general_docs, general_names):
        """ parse auction lot. after fetch data from lot page go to organizer page """
        combo = Combo(response_=response)
        lot_number = combo.auc.get_lot_number()
        lot_docs = combo.lotdoc.download_lot_files(name_general_lst=general_names,
                                                   _id=''.join(transfer['trading_id']), lot_number=lot_number)
        total_docs = dict(chain(general_docs.items(),
                                lot_docs.items()))
        loader = CrawlerBeTwoBeItemLoader(CrawlerBeTwoBeItem(), response=response)
        loader.add_value('data_origin', transfer['data_origin'])
        loader.add_value('trading_id', transfer['trading_id'])
        loader.add_value('trading_link', transfer['trading_link'])
        loader.add_value('trading_number', transfer['trading_number'])
        loader.add_value('trading_type', transfer['trading_type'])
        loader.add_value('trading_form', transfer['trading_form'])
        loader.add_value('trading_org', transfer['trading_org'])
        loader.add_value('trading_org_inn', transfer['trading_org_inn'])
        loader.add_value('msg_number', transfer['msg_number'])
        loader.add_value('case_number', transfer['case_number'])
        loader.add_value('debtor_inn', transfer['debtor_inn'])
        loader.add_value('arbit_manager', transfer['arbit_manager'])
        loader.add_value('arbit_manager_inn', transfer['arbit_manager_inn'])
        loader.add_value('arbit_manager_org', transfer['arbit_manager_org'])
        loader.add_value('arbit_manager_org', transfer['arbit_manager_org'])
        loader.add_value('lot_id', combo.offer.lot_id_numbers())
        loader.add_value('lot_link', response.url)
        loader.add_value('lot_number', lot_number)
        loader.add_value('short_name', combo.auc.get_short_name())
        loader.add_value('lot_info', combo.auc.get_lot_info())
        loader.add_value('property_information', transfer['property_information'])
        loader.add_value('start_date_requests', transfer['start_date_requests'])
        loader.add_value('end_date_requests', transfer['end_date_requests'])
        loader.add_value('start_date_trading', transfer['start_date_trading'])
        loader.add_value('end_date_trading', None)
        loader.add_value('start_price', combo.auc.get_start_price_auc())
        loader.add_value('files', total_docs)
        loader.add_value('created_at', return_parse_date())
        yield loader.load_item()

    def errback_httpbin(self, failure):
        # logs failures

        self.logger.error(repr(failure))

        if failure.check(HttpError):
            response = failure.value.response
            self.logger.error("HttpError occurred on %s", response.url, )

        elif failure.check(DNSLookupError):
            request = failure.request
            self.logger.error("DNSLookupError occurred on %s", request.url)

        elif failure.check(TimeoutError, TCPTimedOutError):
            request = failure.request
            self.logger.error("TimeoutError occurred on %s", request.url)

    def errback_page2(self, failure):
        yield dict(
            main_url=failure.request.cb_kwargs['main_url'],
        )
