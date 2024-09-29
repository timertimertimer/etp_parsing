# -*- coding: utf-8 -*-
import copy
import re
from abc import ABC
import logging
from icecream import ic
from scrapy.spidermiddlewares.httperror import HttpError
from scrapy.spiders import CrawlSpider
from scrapy.utils.python import to_unicode
from scrapy_splash import SplashRequest, SlotPolicy, SplashFormRequest
from twisted.internet.error import DNSLookupError, TCPTimedOutError
from crawler_lot_online_zalog.utils.headers import headers as hd
from scrapy import FormRequest, Request
from ..utils.get_data_from_table import DbConnectCheckLots
from ..settings import DEFAULT_REQUESTS_HEADERS
from ..utils import data_for_requests as dfr
from ..utils.config import start_url, data_origin_url, url_for_post_download
from ..manage_spider.app import Combo
from ..utils.post_data.common_data import data_switcher, param_with_type, data_next_page
from ..items import CrawlerZalogItem, CrawlerZalogItemLoader
from ..utils.working_with_text_cookies_num import cookie_parser
from ..utils.working_with_time import return_servertime, return_parse_date

logger = logging.getLogger(__name__)


class LotOnlineZalogSpider(CrawlSpider, ABC):
    name = 'lot_online_zalog'

    def __init__(self, category, subcategory):
        super(LotOnlineZalogSpider).__init__()
        self.category = category
        self.subcat = subcategory
        self.db_check = DbConnectCheckLots()
        self.previous_lots = self.db_check.get_latest_lot()

    def start_requests(self):
        yield SplashRequest(to_unicode(start_url), self.request_for_open_category,
                            endpoint='execute',
                            cache_args=['lua_source'], args={'lua_source': dfr.script_lua},
                            slot_policy=SlotPolicy.PER_DOMAIN, splash_headers=DEFAULT_REQUESTS_HEADERS,
                            session_id=1, encoding='utf-8',
                            errback=self.errback_httpbin)

    # def request_to_link(self, response):
    #     """"""
    #     combo = Combo(response_=response)
    #     link = 'https://sales.lot-online.ru/e-auction/auctionLotProperty.xhtml?parm=lotUnid%3D960000308100%3Bmode%3Djust'
    #     cookie = response.data['cookies'][0]
    #     cookie = cookie['name'] + '=' + cookie['value']
    #     attempt = 1
    #     hd.headers_lot['Cookie'] = cookie
    #     hd.headers_lot['Referer'] = response.url
    #     view_value = combo.search.get_view_state()
    #     yield Request(url=link, callback=self.sort_type_of_trade,
    #                   cookies=cookie_parser(cookie),
    #                   headers=hd.headers_lot,
    #                   cb_kwargs={'cookie': cookie, 'url_lot': link, 'attempt': attempt, 'view': view_value},
    #                   errback=self.errback_httpbin)

    def request_for_open_category(self, response):
        """ get cookie, get ViewState and do request to category """
        combo = Combo(response_=response)
        cookie = response.data['cookies'][0]
        cookie = cookie['name'] + '=' + cookie['value']
        header = copy.deepcopy(hd.headers_category)
        header['Referer'] = response.url
        header['Cookie'] = cookie
        view_value = combo.search.get_view_state()
        if view_value:
            time_rad = return_servertime()
            form_data = combo.search.retrun_special_post_data(self.category, view_value, time_rad)
            yield FormRequest(response.url, callback=self.filter_tender, formdata=form_data,
                              headers=header, cookies=cookie_parser(cookie), dont_filter=True,
                              cb_kwargs={'cookie': cookie, 'view_value': view_value, 'header': header})

    def filter_tender(self, response, cookie, view_value, header):
        """ do request to activate filter  """
        data_switcher['formMain:inputServerTime'] = return_servertime()
        data_switcher['javax.faces.ViewState'] = view_value
        yield FormRequest(response.url, callback=self.itterate_through_sub_category, formdata=data_switcher,
                          headers=header, cookies=cookie_parser(cookie), dont_filter=True,
                          cb_kwargs={'cookie': cookie, 'view_value': view_value, 'header': header})

    def itterate_through_sub_category(self, response, cookie, view_value, header):
        """ choose and itterate subcategory according main category """
        combo = Combo(response)
        subcategory = combo.search.choose_correct_subcat_data(self.category, self.subcat)
        time_rad = return_servertime()
        subcategory['formMain:inputServerTime'] = time_rad
        subcategory['javax.faces.ViewState'] = view_value
        yield FormRequest(response.url, callback=self.make_requests_with_form_param, formdata=subcategory,
                          headers=header, cookies=cookie_parser(cookie), dont_filter=True,
                          cb_kwargs={'cookie': cookie,
                                     'header': header,
                                     'view_value': view_value,
                                     'subcategory': subcategory,
                                     'name_subcat': subcategory['javax.faces.source'], }, errback=self.errback_httpbin)

    def make_requests_with_form_param(self, response, cookie, subcategory, name_subcat, header, view_value):
        """ param with subcategory data """
        combo = Combo(response_=response)
        extended_filter_data = copy.deepcopy(param_with_type)
        view_state = combo.search.get_view_state_xlm(response.text)
        extended_filter_data['javax.faces.ViewState'] = view_state
        extended_filter_data['formMain:inputServerTime'] = return_servertime()
        header['Accept'] = 'application/xml, text/xml, */*; q=0.01'
        unique_links = set()
        yield FormRequest(response.url, callback=self.parse_serp, formdata=extended_filter_data,
                          headers=header, cookies=cookie_parser(cookie), dont_filter=True, body=response.body,
                          cb_kwargs={'unique_links': unique_links, 'view_value': view_value, 'cookie': cookie,
                                     'header': header},
                          errback=self.errback_httpbin)

    async def parse_serp(self, response, view_value, cookie, header, unique_links: set):
        """ get links to lots and follow pagination """
        combo = Combo(response_=response)
        links_to_lots = combo.search.get_trading_links()
        next_page = combo.search.get_next_button()
        for link in links_to_lots:
            link = response.urljoin(link)
            unique_links.add(link)
        if next_page:
            data_next_page['javax.faces.ViewState'] = view_value
            data_next_page['formMain:inputServerTime'] = return_servertime()
            yield FormRequest(response.url, callback=self.parse_serp, formdata=data_next_page,
                              dont_filter=True,
                              cookies=cookie_parser(cookie),
                              headers=header,
                              cb_kwargs={'unique_links': unique_links, 'view_value': view_value, 'cookie': cookie,
                                         'header': header},
                              errback=self.errback_httpbin)
        else:
            for link in unique_links:
                if (link,) not in self.previous_lots:
                    attempt = 1
                    hd.headers_lot['Cookie'] = cookie
                    hd.headers_lot['Referer'] = response.url
                    yield Request(url=link, callback=self.sort_type_of_trade,
                                  cookies=cookie_parser(cookie),
                                  headers=hd.headers_lot,
                              cb_kwargs={'cookie': cookie, 'url_lot': link, 'attempt': attempt, 'view': view_value},
                              errback=self.errback_httpbin)

    async def sort_type_of_trade(self, response, url_lot, attempt, cookie, view):
        """get response and run function according trading type"""
        combo = Combo(response_=response)
        trading_type = combo.lot.sort_trading_type()
        if str(trading_type) == 'auction':
            return self.parse_auction(response=response, trading_type=trading_type, cookie_=cookie,
                                      url_lot=url_lot, attempt=attempt, view=view)
        if str(trading_type) == 'offer':
            return self.parse_offer(response=response, trading_type=trading_type, cookie_=cookie,
                                    url_lot=url_lot, attempt=attempt, view=view)

    async def parse_auction(self, response, trading_type, cookie_, url_lot, attempt, view):
        """ parse lot of auction type """
        combo = Combo(response_=response)
        if view_value := combo.search.get_view_state():
            view_value = view_value
        else:
            view_value = view
        loader = CrawlerZalogItemLoader(CrawlerZalogItem(), response=response)
        short_name = combo.lot.short_name()
        match = re.match(r'.+?аренд.+', short_name, re.IGNORECASE)
        match1 = re.match(r'^arend.+', short_name, re.IGNORECASE)
        if not match and not match1:
            loader.add_value('data_origin', data_origin_url)
            loader.add_value('trading_id', combo.lot.trade_id)
            loader.add_value('trading_link', response.url)
            loader.add_value('trading_number', combo.lot.trading_number())
            loader.add_value('trading_type', trading_type)
            loader.add_value('trading_form', 'open')
            loader.add_value('trading_org', combo.lot.get_org_name())
            loader.add_value('trading_org_contacts', combo.lot.get_full_org_contacts())
            loader.add_value('status', 'active')
            loader.add_value('category', combo.lot.retrun_category(self.category, self.subcat))
            loader.add_value('index', None)
            loader.add_value('encumbrance', 'Нет')
            loader.add_value('description_encumbrance', None)
            loader.add_value('lot_number', combo.lot.lot_number())
            loader.add_value('short_name', combo.lot.short_name())
            loader.add_value('lot_info', combo.lot.lot_info())
            loader.add_value('property_information', combo.lot.property_info())
            loader.add_value('start_date_requests', combo.lot.start_date_request_auc())
            loader.add_value('end_date_requests', combo.lot.end_date_request_auc())
            loader.add_value('start_date_trading', combo.lot.start_date_trading_auc())
            loader.add_value('end_date_trading', combo.lot.end_date_trading_auc())
            loader.add_value('quantity', None)
            loader.add_value('unit', None)
            loader.add_value('deposit', combo.lot.get_deposit())
            loader.add_value('start_price', combo.lot.start_price())
            loader.add_value('step_price', combo.lot.step_price())
            body = response.body.decode('utf-8')
            general_files = combo.downspider.download_general(url_for_post_download,
                                                              combo.lot.trading_number(),
                                                              cookies=cookie_ + '; primefaces.download=true'.strip(),
                                                              view=view_value,
                                                              body=body)
            lot_file = combo.downspider.download_lot_img(url_id=combo.lot.trading_number(), lot_num='1',
                                                         cookie=cookie_ + '; primefaces.download=true'.strip(),
                                                         )
            loader.add_value('files', {'general': general_files, 'lot': lot_file})
            header = copy.deepcopy(hd.headers_category)
            header['Referer'] = response.url
            header['Cookie'] = cookie_
            if param_addres := combo.downspider.get_address_block(body_=body, view_value=view_value):
                yield FormRequest(response.url, callback=self.parse_address,
                                  formdata=param_addres,
                                  headers=header, cookies=cookie_parser(cookie_),
                                  cb_kwargs={'loader': loader, 'attempt': attempt,
                                             'url_lot': url_lot, 'view': view_value,
                                             'cookie': cookie_})
            else:
                if loader.get_collected_values('short_name') is None:
                    loader.add_value('short_name', 'Лот - ' + ''.join(loader.get_collected_values('lot_number')))
                loader.add_value('created_at', return_parse_date())
                yield loader.load_item()

    async def parse_offer(self, response, trading_type, cookie_, url_lot, attempt, view):
        """ parse lot of auction type """
        combo = Combo(response_=response)
        if view_value := combo.search.get_view_state():
            view_value = view_value
        else:
            view_value = view
        loader = CrawlerZalogItemLoader(CrawlerZalogItem(), response=response)
        short_name = combo.lot.short_name()
        match = re.match(r'.+?аренд.+', short_name, re.IGNORECASE)
        match1 = re.match(r'^arend.+', short_name, re.IGNORECASE)
        if not match and not match1:
            loader.add_value('data_origin', data_origin_url)
            loader.add_value('trading_id', combo.lot.trade_id)
            loader.add_value('trading_link', response.url)
            loader.add_value('trading_number', combo.lot.trading_number())
            loader.add_value('trading_type', trading_type)
            loader.add_value('trading_form', 'open')
            loader.add_value('trading_org', combo.lot.get_org_name())
            loader.add_value('trading_org_contacts', combo.lot.get_full_org_contacts())
            loader.add_value('category', combo.lot.retrun_category(self.category, self.subcat))
            loader.add_value('status', 'active')
            loader.add_value('index', None)
            loader.add_value('encumbrance', 'Нет')
            loader.add_value('description_encumbrance', None)
            loader.add_value('lot_number', combo.lot.lot_number())
            loader.add_value('short_name', combo.lot.short_name())
            loader.add_value('lot_info', combo.lot.lot_info())
            loader.add_value('property_information', combo.lot.property_info())
            loader.add_value('start_date_requests', combo.lot.start_date_request)
            loader.add_value('end_date_requests', combo.lot.end_date_request)
            loader.add_value('start_date_trading', combo.lot.start_date_trading)
            loader.add_value('end_date_trading', combo.lot.end_date_trading)
            loader.add_value('start_price', combo.lot.start_price())
            loader.add_value('periods', combo.lot.return_periods)
            loader.add_value('quantity', None)
            loader.add_value('unit', None)
            loader.add_value('deposit', combo.lot.get_deposit())
            body = response.body.decode('utf-8')
            general_files = combo.downspider.download_general(url_for_post_download,
                                                              combo.lot.trading_number(),
                                                              cookies=cookie_ + '; primefaces.download=true'.strip(),
                                                              view=view_value,
                                                              body=body)
            lot_file = combo.downspider.download_lot_img(url_id=combo.lot.trading_number(), lot_num='1',
                                                         cookie=cookie_ + '; primefaces.download=true'.strip(),
                                                         )
            loader.add_value('files', {'general': general_files, 'lot': lot_file})
            header = copy.deepcopy(hd.headers_category)
            header['Referer'] = response.url
            header['Cookie'] = cookie_
            if param_addres := combo.downspider.get_address_block(body_=body, view_value=view_value):
                yield FormRequest(response.url, callback=self.parse_address,
                                  formdata=param_addres,
                                  headers=header, cookies=cookie_parser(cookie_),
                                  cb_kwargs={'loader': loader, 'attempt': attempt,
                                             'url_lot': url_lot, 'view': view_value,
                                             'cookie': cookie_})
            else:
                if loader.get_collected_values('short_name') is None:
                    loader.add_value('short_name', 'Лот - ' + ''.join(loader.get_collected_values('lot_number')))
                loader.add_value('created_at', return_parse_date())
                yield loader.load_item()

    async def parse_address(self, response, loader, attempt, url_lot, cookie, view):
        """ parse address and complete lot """
        combo = Combo(response_=response)
        body_ = response.body.decode('utf-8')
        loader.add_value('address', combo.downspider.get_address(body_))
        loader.add_value('detailed_address', combo.downspider.get_detaled_address(body_))
        check_address = loader.get_collected_values('address')
        check_det_address = loader.get_collected_values('detailed_address')
        if len(check_address) == 0 and len(check_det_address) == 0 and attempt < 4:
            logger.info(f'This is attempt number {attempt} and response url - {response.url}')
            attempt += 1
            hd.headers_lot['Cookie'] = cookie
            hd.headers_lot['Referer'] = response.url
            yield Request(url=url_lot, callback=self.sort_type_of_trade,
                          cookies=cookie_parser(cookie),
                          headers=hd.headers_lot, dont_filter=True,
                          cb_kwargs={'cookie': cookie, 'url_lot': url_lot, 'attempt': attempt, 'view': view},
                          errback=self.errback_httpbin)
        else:
            if loader.get_collected_values('short_name') is None:
                loader.add_value('short_name', 'Лот - ' + ''.join(loader.get_collected_values('lot_number')))
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
