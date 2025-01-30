# -*- coding: utf-8 -*-
import logging
from abc import ABC
from scrapy.utils.python import to_unicode
import pandas as pd
from bs4 import BeautifulSoup as BS
from scrapy import FormRequest, Request
from scrapy.spidermiddlewares.httperror import HttpError
from scrapy.spiders import CrawlSpider
from scrapy_splash import SplashRequest, SplashFormRequest, SlotPolicy
from twisted.internet.error import DNSLookupError
from twisted.internet.error import TimeoutError, TCPTimedOutError

from general_utils import CrawlerBankruptItem, CrawlerBankruptItemLoader
from general_utils.location import Region
from ..locators.spider_locators import LocatorSpider
from ..trades.app import ComposeTrade
from ..utils import data_for_requests as dfr
from ..utils.get_data_from_table import DbConnectCheckLots
from ..utils.config import *
from ..utils.manage_spider import sort_trading_type, get_trading_form
from ..utils.work_with_text_and_number import dedent_func, cookie_parser
from ..utils.working_with_time import increase_time_days, return_servertime, return_parse_date
from ..utils.working_with_url import UrlConfig

logger = logging.getLogger(__name__)


class LotOnlineRuSpider(CrawlSpider, ABC):
    name = 'lot_online_ru'
    days_increase = time_delta

    def __init__(self, *a, **kw):
        super(LotOnlineRuSpider).__init__(*a, **kw)
        self.loc = LocatorSpider
        self.url = UrlConfig
        self.db_check = DbConnectCheckLots()
        self.previous_lots = self.db_check.get_latest_lot()

    def start_requests(self):
        date_range = pd.date_range(start_time_from, periods=periods_, freq=format_period)
        for start_time in date_range:
            logger.info(f'THIS IS START TIME PUBLICATION - {start_time}')
            start_time = start_time.strftime('%d.%m.%Y')
            time_to = increase_time_days(start_time, self.days_increase)
            logger.info(f'THIS IS END TIME PUBLICATION - {time_to}')
            yield SplashRequest(to_unicode(main_page_url), self.activate_form_for_request,
                                endpoint='execute',
                                cache_args=['lua_source'], args={'lua_source': dfr.script_lua},
                                slot_policy=SlotPolicy.PER_DOMAIN,
                                session_id=1, encoding='utf-8',
                                meta={'start_time': start_time, 'time_to': time_to},
                                errback=self.errback_httpbin)

    def activate_form_for_request(self, response):
        status_code = response.status
        if status_code != 200:
            logger.error(f"{response.url} :: status_code - {status_code}")
        start_time = response.meta['start_time']
        time_to = response.meta['time_to']
        body = response.body.decode('utf-8')
        soup = BS(str(body), features='lxml')
        try:
            view_value = soup.find('input', id='j_id1:javax.faces.ViewState:0')['value']
        except Exception as ex:
            logger.critical(f'{response.url} \n\n {response.text} \n{ex}\n', exc_info=True)
            return None
        server_time = soup.find('input', id='formMain:inputServerTime')['value']
        dfr.form_data['formMain:inputServerTime'] = server_time
        dfr.data_switcher['javax.faces.ViewState'] = view_value
        cookie = response.data['cookies'][0]
        cookie = cookie['name'] + '=' + cookie['value']
        yield SplashFormRequest(response.url, callback=self.parse_data_for_next_req, formdata=dfr.data_switcher,
                                method="POST",
                                dont_filter=True,
                                meta={'view': view_value, 'server_time': server_time},
                                endpoint='execute',
                                cache_args=['lua_source'], args={'lua_source': dfr.script_lua_2},
                                slot_policy=SlotPolicy.PER_DOMAIN,
                                splash_headers={'Accept': 'application/xml, text/xml, */*; q=0.01',
                                                'Accept-Encoding': 'gzip, deflate, br',
                                                'Accept-Language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7',
                                                'Connection': 'keep-alive',
                                                'Cookie': cookie,
                                                'Faces-Request': 'partial/ajax',
                                                'Host': 'sales.lot-online.ru',
                                                'Origin': data_origin_url,
                                                'Pragma': 'no-cache',
                                                'Referer': response.url,
                                                'Sec-Fetch-Site': 'same-origin',
                                                'Sec-Fetch-Mode': 'cors',
                                                'Sec-Fetch-Dest': 'empty',

                                                'X-Requested-With': 'XMLHttpRequest'
                                                },
                                session_id=1,
                                cb_kwargs={'start_time': start_time, 'time_to': time_to, 'cookie': cookie},
                                errback=self.errback_httpbin)

    def parse_data_for_next_req(self, response, start_time, time_to, cookie):
        status_code = response.status
        if status_code != 200:
            logger.error(f"{response.url} :: status_code - {status_code}")
        cookie = cookie
        dfr.form_data['formMain:auctionDatePlanBID_input'] = start_time
        dfr.form_data['formMain:auctionDatePlanEID_input'] = time_to
        dfr.form_data['javax.faces.ViewState'] = response.meta['view']
        dfr.form_data['formMain:inputServerTime'] = return_servertime()
        unique_links = set()
        yield FormRequest(response.url, callback=self.parse_serp, formdata=dfr.form_data,
                          dont_filter=True,
                          cookies=cookie_parser(cookie),
                          headers={'Accept': 'application/xml, text/xml, */*; q=0.01',
                                   'Accept-Encoding': 'gzip, deflate, br',
                                   'Accept-Language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7',
                                   'Connection': 'keep-alive',
                                   'Cookie': cookie,
                                   'Faces-Request': 'partial/ajax',
                                   'Host': 'sales.lot-online.ru',
                                   'Origin': data_origin_url,
                                   'Pragma': 'no-cache',
                                   'Referer': response.url,
                                   'Sec-Fetch-Site': 'same-origin',
                                   'Sec-Fetch-Mode': 'cors',
                                   'Sec-Fetch-Dest': 'empty',
                                   'X-Requested-With': 'XMLHttpRequest'
                                   },
                          cb_kwargs={'unique_links': unique_links, 'cookie': cookie,
                                     'start_time': start_time, 'time_to': time_to,
                                     'view': response.meta['view']},
                          errback=self.errback_httpbin)

    def parse_serp(self, response, unique_links, cookie, start_time, time_to, view):
        status_code = response.status
        combo = ComposeTrade(response_=response)
        if status_code != 200:
            logger.error(f"{response.url} :: status_code - {status_code}")
        unique_links = unique_links
        links_to_lot = combo.serp.get_trading_links()
        next_page = combo.serp.get_next_button()
        for link in links_to_lot:
            try:
                link = self.url.url_join(first_part_url_lot, link)
                unique_links.add(link)
            except Exception as e:
                logger.error(f'INVALID DATA FETCHING LINKS {e}')
        if next_page:
            dfr.data_next_page['formMain:auctionDatePlanBID_input'] = start_time
            dfr.data_next_page['formMain:auctionDatePlanEID_input'] = time_to
            dfr.data_next_page['javax.faces.ViewState'] = view
            dfr.data_next_page['formMain:inputServerTime'] = return_servertime()
            yield FormRequest(response.url, callback=self.parse_serp, formdata=dfr.data_next_page,
                              dont_filter=True,
                              cookies=cookie_parser(cookie),
                              headers={'Accept': 'application/xml, text/xml, */*; q=0.01',
                                       'Accept-Encoding': 'gzip, deflate, br',
                                       'Accept-Language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7',
                                       'Connection': 'keep-alive',
                                       'Cookie': cookie,
                                       'Faces-Request': 'partial/ajax',
                                       'Host': 'sales.lot-online.ru',
                                       'Origin': data_origin_url,
                                       'Pragma': 'no-cache',
                                       'Referer': response.url,
                                       'Sec-Fetch-Site': 'same-origin',
                                       'Sec-Fetch-Mode': 'cors',
                                       'Sec-Fetch-Dest': 'empty',
                                       'X-Requested-With': 'XMLHttpRequest'
                                       },
                              cb_kwargs={'unique_links': unique_links, 'cookie': cookie,
                                         'start_time': start_time, 'time_to': time_to,
                                         'view': view},
                              errback=self.errback_httpbin)
        else:
            for link in unique_links:
                if (link,) not in self.previous_lots:
                    attempt = 1
                    yield Request(url=link, callback=self.sort_type_of_trade,
                                  cookies=cookie_parser(cookie),
                                  headers=dfr.headers_for_lot,
                                  cb_kwargs={'cookie': cookie, 'url_lot': link, 'attempt': attempt},
                                  errback=self.errback_httpbin)

    # def start_requests(self):
    #     for bad_link in list_error_link:
    #         attempt = 1
    #         yield SplashRequest(
    #             bad_link,
    #             self.sort_type_of_trade,
    #             endpoint='execute',
    #             cache_args=['lua_source'], args={'lua_source': dfr.script_lua_lot},
    #             slot_policy=SlotPolicy.PER_DOMAIN, splash_headers=dfr.headers_for_lot,
    #             session_id=2, encoding='utf-8',
    #             errback=self.errback_httpbin,
    #             cb_kwargs={'url_lot': bad_link, 'attempt': attempt, 'cookie': None})

    async def sort_type_of_trade(self, response, url_lot, attempt, cookie):
        """get response and run function according trading type"""
        # _div_tender contains information about trading type, periods and prices(auction)
        status_code = response.status
        if status_code != 200:
            logger.error(f"{response.url} :: status_code - {status_code}")
        try:
            if cookie is None:
                cookie = response.data['cookies'][0]
                cookie = cookie['name'] + '=' + cookie['value']
                # cookie = (list(filter(lambda x: "JSESSIONID" in str(x), response.data['cookies']))[0])
            else:
                cookie = cookie
        except Exception as e:
            logger.critical(f'{response.url} :: NO COOKIES !!!!!!!!!!!!!!!!!!!!!!{e}')
            return None
        div_tender = response.xpath(self.loc.div_tender_loc).get()
        soup = BS(str(div_tender), features='lxml')
        text = dedent_func([''.join(x.get_text()).strip() for x in soup][0])
        trade_type = sort_trading_type(text)
        if str(trade_type) == 'auction':
            return self.parse_lot_auction(response=response, text=text, trading_type=trade_type, cookie_=cookie,
                                          url_lot=url_lot, attempt=attempt)
        if str(trade_type) == 'offer':
            return self.parse_lot_offer(response=response, text=text, trading_type=trade_type, cookie_=cookie,
                                        url_lot=url_lot, attempt=attempt)
        if str(trade_type) == 'competition':
            return self.parse_lot_auction(response=response, text=text, trading_type=trade_type, cookie_=cookie,
                                          url_lot=url_lot, attempt=attempt)

    def parse_lot_offer(self, response, text, trading_type, cookie_, url_lot, attempt):
        status_code = response.status
        if status_code != 200:
            logger.error(f"{response.url} :: status_code - {status_code}")
        body = response.body.decode('utf-8')
        soup = BS(str(body), features='lxml')
        arbitr_cookies = cookie_ + '; primefaces.download=true'
        cookie = prime_cookies + cookie_
        view_value = soup.find('input', id='j_id1:javax.faces.ViewState:0')['value']
        combo = ComposeTrade(response_=response)
        loader = CrawlerBankruptItemLoader(CrawlerBankruptItem(), response=response)
        loader.add_value('data_origin', data_origin_url)
        loader.add_value('trading_id', combo.auc.trade_id)
        loader.add_value('trading_link', response.url)
        loader.add_value('trading_number', combo.auc.trading_number(text=text))
        loader.add_value('trading_type', trading_type)
        loader.add_value('trading_form', get_trading_form(text=text))
        loader.add_value('trading_org', combo.auc.trading_organizer)
        loader.add_value('trading_org_inn', None)
        loader.add_value('trading_org_contacts', combo.auc.organizer_contacts)
        loader.add_value('msg_number', combo.auc.msg_number)
        loader.add_value('case_number', combo.auc.case_number)
        loader.add_value('debtor_inn', combo.auc.debitor_inn)
        address = combo.auc.address
        region = None
        if address:
            region = Region.get_region(address)
        loader.add_value('address', address)
        loader.add_value('region', region)
        loader.add_value('status', combo.auc.status_lot)
        loader.add_value('lot_id', None)
        loader.add_value('lot_link', None)
        loader.add_value('lot_number', combo.auc.lot_number())
        loader.add_value('short_name', combo.auc.short_name())
        loader.add_value('lot_info', combo.auc.lot_info())
        loader.add_value('property_information', combo.auc.property_info)
        loader.add_value('start_date_requests', combo.offer.start_date_request)
        loader.add_value('end_date_requests', combo.offer.end_date_request)
        loader.add_value('start_date_trading', combo.offer.start_date_trading)
        loader.add_value('end_date_trading', combo.offer.end_date_trading)
        loader.add_value('start_price', combo.offer.start_price_offer)
        loader.add_value('periods', combo.offer.return_periods)
        # fetch and download files
        general_files = combo.auc.download_general(url_for_post_download,
                                                 combo.auc.trading_number(text), cookies=arbitr_cookies.strip(),
                                                 view=view_value,
                                                 body=body)
        lot_file = combo.auc.download_lot_img(url_id=combo.auc.trading_number(text), lot_num=combo.auc.lot_number(),
                                              cookie=arbitr_cookies.strip())
        loader.add_value('files', {'general': general_files, 'lot': lot_file})
        loader.add_value('created_at', return_parse_date())
        arbitr_title = combo.auc.return_title_arbitr_block
        yield FormRequest(response.url, callback=self.get_arbitr_information,
                          cookies=cookie_parser(cookie),
                          formdata=combo.auc.arbitr_data_post(view_value, body), dont_filter=True,
                          cb_kwargs={'loader': loader,
                                     'title': arbitr_title,
                                     'cookie': cookie,
                                     'attempt': attempt,
                                     'url_lot': url_lot},
                          errback=self.errback_httpbin)

    def parse_lot_auction(self, response, text, trading_type, cookie_, url_lot, attempt):
        status_code = response.status
        if status_code != 200:
            logger.error(f"{response.url} :: status_code - {status_code} - REQUEST TO AUCTION")
        body = response.body.decode('utf-8')
        soup = BS(str(body), features='lxml')
        arbitr_cookies = cookie_ + '; primefaces.download=true'
        cookie = prime_cookies + cookie_
        view_value = soup.find('input', id='j_id1:javax.faces.ViewState:0')['value']
        combo = ComposeTrade(response_=response)
        loader = CrawlerBankruptItemLoader(CrawlerBankruptItem(), response=response)
        loader.add_value('data_origin', data_origin_url)
        loader.add_value('trading_id', combo.auc.trade_id)
        loader.add_value('trading_link', response.url)
        loader.add_value('trading_number', combo.auc.trading_number(text=text))
        loader.add_value('trading_type', trading_type)
        loader.add_value('trading_form', get_trading_form(text=text))
        loader.add_value('trading_org', combo.auc.trading_organizer)
        loader.add_value('trading_org_inn', None)
        loader.add_value('trading_org_contacts', combo.auc.organizer_contacts)
        loader.add_value('msg_number', combo.auc.msg_number)
        loader.add_value('case_number', combo.auc.case_number)
        loader.add_value('debtor_inn', combo.auc.debitor_inn)
        address = combo.auc.address
        region = None
        if address:
            region = Region.get_region(address)
        loader.add_value('address', address)
        loader.add_value('region', region)
        loader.add_value('status', combo.auc.status_lot)
        loader.add_value('lot_id', None)
        loader.add_value('lot_link', None)
        loader.add_value('lot_number', combo.auc.lot_number())
        loader.add_value('short_name', combo.auc.short_name())
        loader.add_value('lot_info', combo.auc.lot_info())
        loader.add_value('property_information', combo.auc.property_info)
        loader.add_value('start_date_requests', combo.auc.start_date_request_auc(text=text))
        loader.add_value('end_date_requests', combo.auc.end_date_request_auc(text=text))
        loader.add_value('start_date_trading', combo.auc.start_date_trading_auc(text=text))
        loader.add_value('end_date_trading', combo.auc.end_date_trading_auc(text=text))
        loader.add_value('start_price', combo.offer.start_price_offer)
        loader.add_value('step_price', combo.auc.step_price(text=text))
        # fetch and download files
        general_files = combo.auc.download_general(url_for_post_download,
                                                 combo.auc.trading_number(text), cookies=arbitr_cookies.strip(),
                                                 view=view_value,
                                                 body=body)
        lot_file = combo.auc.download_lot_img(url_id=combo.auc.trading_number(text), lot_num=combo.auc.lot_number(),
                                              cookie=arbitr_cookies.strip())
        loader.add_value('files', {'general': general_files, 'lot': lot_file})
        loader.add_value('created_at', return_parse_date())
        arbitr_title = combo.auc.return_title_arbitr_block
        yield FormRequest(response.url, callback=self.get_arbitr_information,
                          cookies=cookie_parser(cookie),
                          formdata=combo.auc.arbitr_data_post(view_value, body), dont_filter=True,

                          cb_kwargs={'loader': loader,
                                     'title': arbitr_title,
                                     'cookie': cookie,
                                     'attempt': attempt,
                                     'url_lot': url_lot},
                          errback=self.errback_httpbin)

    async def get_arbitr_information(self, response, loader, title, cookie, attempt, url_lot):
        combo = ComposeTrade(response_=response)
        check_arbitr = combo.auc.arbitr_name(arbitr_title=title, url=url_lot)
        if check_arbitr is None and attempt < 4:
            logger.info(f'This is attempt number {attempt} and response url - {response.url}')
            attempt += 1
            yield Request(url=url_lot, callback=self.sort_type_of_trade,
                          cookies=cookie_parser(cookie),
                          headers=dfr.headers_for_lot, dont_filter=True,
                          cb_kwargs={'cookie': cookie, 'url_lot': url_lot, 'attempt': attempt},
                          errback=self.errback_httpbin)
        elif len(check_arbitr) > 0 or attempt == 4:
            if check_arbitr is None:
                logger.error(f'{response.url} :: ARBITR ERROR {loader.get_collected_values("trading_link")}')
            loader.add_value('arbit_manager', check_arbitr)
            loader.add_value('arbit_manager_inn', combo.auc.arbitr_inn)
            loader.add_value('arbit_manager_org', combo.auc.arbitr_org(arbitr_title=title))
            if loader.get_collected_values('short_name') is None:
                loader.add_value('short_name', 'Лот - ' + ''.join(loader.get_collected_values('lot_number')))
            yield loader.load_item()
        else:
            logger.critical(f'SOMETHING WENT WRONG WITH ATTEMPT ARBITR {url_lot}')

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
