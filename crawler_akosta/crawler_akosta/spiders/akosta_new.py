from itertools import chain
from scrapy.spidermiddlewares.httperror import HttpError
from scrapy.spiders import Spider
from scrapy import Request, FormRequest
from scrapy_splash import SplashRequest, SlotPolicy, SplashFormRequest
from twisted.internet.error import DNSLookupError, TCPTimedOutError, TimeoutError
from scrapy.utils.python import to_native_str, to_unicode
from ..manage_spider.app import Combo
from ..settings import DEFAULT_REQUESTS_HEADERS
from ..utils.data_for_requests import script_lua, script_lua_nojs
from ..utils.headers import HEADERS_TO_SERP_PAGE
from ..utils.post_data import post_data_pagination, post_data_to_trade, post_data_query, post_data_debitor, \
    post_data_lot_tab, post_data_unique_lot_page, post_data_period_offer_page, post_search_query
from ..utils.config import start_page, end_page, data_origin_url, search_link, start_time, common_link, debtor_link, \
    lot_link, _link_post_period
from ..utils.work_with_text_and_number import return_main_cookies, cookie_parser
from ..utils.working_with_time import return_servertime, return_parse_date
from ..items import CrawlerAkostaItem, CrawlerAkostaItemLoader, TransferAkostaItem
from ..utils.download import DownloadFiles
import copy
import logging
import json
from icecream import ic

logger = logging.getLogger(__name__)


class AkostaNewSpider(Spider):
    name = 'akosta_new'
    start_url = ['https://www.akosta.info/akosta/lots.xhtml']

    def __init__(self, *args, **kwargs):
        super(AkostaNewSpider, self).__init__(*args, **kwargs)
        self.down = DownloadFiles()

    def start_requests(self):
        yield SplashRequest(self.start_url[0], callback=self.get_data_and_cookies, endpoint='execute', session_id=1,
                            slot_policy=SlotPolicy.PER_DOMAIN,
                            cache_args=['lua_source'], args={'lua_source': script_lua})

    def get_data_and_cookies(self, response):
        """ get cookies and  get list with unique numbers
            and repeat request to the same page
        """
        combo = Combo(_response=response)
        cookie = response.data['cookies']
        cookie = return_main_cookies(cookie)
        my_data = combo.search.return_lst_unique_data()
        yield FormRequest.from_response(response, callback=self.query_requests, dont_filter=True,
                                        cb_kwargs={'lst': my_data, 'cookie': cookie})

    def query_requests(self, response, lst, cookie):
        """  """
        combo = Combo(_response=response)
        data: list = lst
        cookie = cookie
        viewstate = combo.pre.get_post_data_values('input', 'j_id1:javax.faces.ViewState:0')
        header = copy.deepcopy(HEADERS_TO_SERP_PAGE)
        header['Referer'] = response.url
        header['Cookie'] = cookie
        trade = str(data.pop(0))
        post_data_ = copy.deepcopy(post_search_query)
        post_data_['formMain:inputServerTime'] = return_servertime()
        post_data_['formMain:inputKeyWordId'] = str(trade).strip()
        post_data_['javax.faces.ViewState'] = ''.join(viewstate).strip()
        yield FormRequest(search_link, callback=self.redirect_search, formdata=post_data_,
                          headers=header,
                          dont_filter=True, meta={'dont_redirect': True, 'handle_httpstatus_list': [302]},
                          cb_kwargs={'trade': trade, 'cookie': cookie, 'list_trade': data})

    def redirect_search(self, response, trade, cookie, list_trade):
        header = copy.deepcopy(HEADERS_TO_SERP_PAGE)
        header['Referer'] = data_origin_url
        header['Cookie'] = cookie
        yield Request(search_link, callback=self.parse_serp,
                      headers=header,
                      # cookies=cookie_parser(cookie),
                      dont_filter=True,
                      cb_kwargs={'trade': trade, 'cookie': cookie, 'list_trade': list_trade})

    def parse_serp(self, response, trade, cookie, list_trade):
        """
        :param trade: trading_id
        :param list_trade: list with trading numbers
        :param cookie: current cookies
        :param response: response after request
        :return: yield post request to trade page
        """""
        combo = Combo(_response=response)
        viewstate = combo.pre.get_post_data_values('input', 'j_id1:javax.faces.ViewState:0')
        header = copy.deepcopy(HEADERS_TO_SERP_PAGE)
        header['Referer'] = search_link
        header['Cookie'] = cookie
        links_list = combo.pre.get_only_one_needed_id(trade)
        for link in links_list:
            post_data_to_trade['javax.faces.source'] = link[0]
            form_main = post_data_to_trade['javax.faces.source']
            post_data_to_trade[form_main] = form_main
            post_data_to_trade["formMain:inputServerTime"] = return_servertime()
            post_data_to_trade["formMain:inputKeyWordId"] = trade
            post_data_to_trade["javax.faces.ViewState"] = viewstate
            post_data_ = copy.deepcopy(post_data_to_trade)
            del post_data_to_trade[form_main]
            yield FormRequest(search_link, self.parse_redirect_page, formdata=post_data_,
                              cookies=cookie_parser(cookie), dont_filter=True,
                              headers=header, cb_kwargs={'header': header, 'cookie': cookie,
                                                         'trade': trade, 'real_trade': link[1]})
        if len(list_trade) > 0:
            yield Request(search_link, callback=self.query_requests, headers=header,
                          cookies=cookie_parser(cookie), dont_filter=True,
                          cb_kwargs={'lst': list_trade, 'cookie': cookie})

    async def parse_redirect_page(self, response, header, cookie, trade, real_trade):
        """ on page with redirect info - url to trade page """
        combo = Combo(_response=response)
        header['Referer'] = response.url
        header['Cookie'] = cookie
        url_to_trade = combo.main_.get_link_redirect(trade_=trade)
        if url_to_trade:
            yield Request(url_to_trade, callback=self.parse_trade_page, headers=header,
                          cookies=cookie_parser(cookie),
                          cb_kwargs={'header': header,
                                     'cookie': cookie,
                                     'trade': trade,
                                     'real_trade': real_trade})
        else:
            logger.error(f'{response.url} :: ERROR redirect link (first) {trade}')
            with open(f'error_redirect_first{trade}.txt', 'w') as f:
                f.write(response.text)

    async def parse_trade_page(self, response, header, cookie, trade, real_trade):
        """ parse trading page common info get new viewstate  and make requests to debtor tab(page)"""
        # with open('res.txt', 'w') as f:
        #     f.write(response.text)
        combo = Combo(_response=response)
        transfer = TransferAkostaItem()
        transfer['data_origin'] = data_origin_url
        transfer['trading_id'] = real_trade
        transfer['trading_link'] = response.url
        trading_type = combo.trade.get_trading_type()
        transfer['trading_type'] = trading_type
        transfer['trading_form'] = combo.trade.get_trading_form()
        transfer['trading_org'] = combo.trade.get_org_name()
        transfer['trading_org_inn'] = None
        transfer['trading_org_contacts'] = combo.trade.get_org_contacts()
        if trading_type in ('auction', 'competition'):
            transfer['start_date_requests'] = combo.main_.start_date_req_auc()
            transfer['end_date_requests'] = combo.main_.end_date_request_auc()
            transfer['start_date_trading'] = combo.main_.start_date_trading_auc()
            transfer['end_date_trading'] = combo.main_.end_date_trading_auc()

        # !!! DOCS !!!

        # HEADERS
        header['Referer'] = response.url
        header['Cookie'] = cookie
        header['Origin'] = 'https://www.akosta.info'
        header['Sec-Fetch-Site'] = 'same-origin'
        header['Content-Type'] = 'application/x-www-form-urlencoded'
        # url = combo.main_.get_debtor_info_link(response.url)
        new_view = combo.pre.get_post_data_values('input', 'j_id1:javax.faces.ViewState:0')
        post_data_debitor['formMain:inputServerTime'] = return_servertime()
        post_data_debitor['javax.faces.ViewState'] = new_view
        form_number_search = combo.deb.find_correct_form_number()
        post_data_debitor[form_number_search] = 'false'
        general_files = combo.main_.download_general(url=common_link, trade_id=''.join(transfer['trading_id']),
                                                     view=new_view,
                                                     cookies=cookie)

        yield FormRequest(common_link, callback=self.parse_debitor,
                          headers=header, dont_filter=True,
                          formdata=post_data_debitor, method='POST',
                          cookies=cookie_parser(cookie),
                          cb_kwargs={'header': header,
                                     'cookie': cookie,
                                     'transfer': transfer,
                                     'trading_type': trading_type,
                                     'files': general_files},
                          )

    async def parse_debitor(self, response, header, trading_type, cookie, transfer, files):
        """ parse debtor tab(page), get new viewstate  and make requests to lot tab(page) """
        transfer = transfer
        combo = Combo(_response=response)
        debtor_view_state = combo.pre.get_post_data_values('input', 'j_id1:javax.faces.ViewState:0')

        transfer['trading_number'] = combo.deb.get_trading_number()
        transfer['msg_number'] = combo.deb.get_msg_number()
        transfer['case_number'] = combo.deb.get_case_number()
        transfer['debtor_inn'] = combo.deb.get_debtor_inn()
        transfer['arbit_manager'] = combo.deb.get_arbitr_full_name()
        transfer['arbit_manager_inn'] = combo.deb.get_arbitr_inn()
        transfer['arbit_manager_org'] = combo.deb.get_arbitr_company()

        header['Referer'] = response.url
        header['Cookie'] = cookie
        header['Origin'] = 'https://www.akosta.info'
        header['Sec-Fetch-Site'] = 'same-origin'
        post_data_lot_tab['formMain:inputServerTime'] = return_servertime()
        post_data_lot_tab['javax.faces.ViewState'] = debtor_view_state
        yield FormRequest(debtor_link, callback=self.parse_lot_tab, headers=header, formdata=post_data_lot_tab,
                          cookies=cookie_parser(cookie), cb_kwargs={'header': header,
                                                                    'cookie': cookie,
                                                                    'transfer': transfer,
                                                                    'trading_type': trading_type,
                                                                    'files': files,
                                                                    'lots_id': None}, dont_filter=True,
                          )

    async def parse_lot_tab(self, response, header, trading_type, cookie, transfer, files, lots_id):
        """ fetch post data to all unique lot and make post request """
        combo = Combo(_response=response)

        header['Referer'] = response.url
        header['Cookie'] = cookie
        header['Origin'] = 'https://www.akosta.info'
        header['Sec-Fetch-Site'] = 'same-origin'

        lot_viewstate = combo.pre.get_post_data_values('input', 'j_id1:javax.faces.ViewState:0')
        post_lot = copy.deepcopy(post_data_unique_lot_page)
        if lots_id is None:
            count_lots = combo.trade.get_post_lot_data()
        else:
            count_lots = lots_id
        data_lot = count_lots.pop(0)
        # for a in combo.trade.get_post_lot_data():
        post_lot['javax.faces.source'] = data_lot
        post_lot[data_lot] = data_lot
        post_lot['formMain:inputServerTime'] = return_servertime()
        post_lot['javax.faces.ViewState'] = lot_viewstate
        lot_number = combo.trade.get_lot_number(_id=data_lot)
        yield FormRequest(lot_link, callback=self.parse_pre_lot_page, headers=header, formdata=post_lot,
                          cookies=cookie_parser(cookie), cb_kwargs={'header': header,
                                                                    'files': files,
                                                                    'cookie': cookie,
                                                                    'trading_type': trading_type,
                                                                    'transfer': transfer, 'lot_number': lot_number
                                                                    }, dont_filter=True
                          )
        # delete tempolary data from post form
        if len(count_lots) > 0:
            del post_lot[data_lot]
            yield FormRequest.from_response(response, callback=self.parse_lot_tab, headers=header,
                                            cookies=cookie_parser(cookie), cb_kwargs={'header': header,
                                                                                      'cookie': cookie,
                                                                                      'transfer': transfer,
                                                                                      'trading_type': trading_type,
                                                                                      'files': files,
                                                                                      'lots_id': count_lots},
                                            dont_filter=True)

    async def parse_pre_lot_page(self, response, header, cookie, transfer, trading_type, lot_number, files):
        """ get link to lot """
        combo = Combo(_response=response)
        header['Referer'] = response.url
        url_to_trade = combo.main_.get_link_redirect(trade_=response.url)
        if url_to_trade:
            if trading_type == 'offer':
                yield Request(url_to_trade, callback=self.parse_lot_offer, headers=header,
                              cookies=cookie_parser(cookie), dont_filter=True,
                              cb_kwargs={'cookie': cookie, 'transfer': transfer, 'url_to_trade': url_to_trade,
                                         'lot_number': lot_number, 'header': header, 'files': files})
            if trading_type == 'auction':
                yield Request(url_to_trade, callback=self.parse_lot_auction, headers=header,
                              cookies=cookie_parser(cookie), dont_filter=True,
                              cb_kwargs={'cookie': cookie, 'transfer': transfer, 'url_to_trade': url_to_trade,
                                         'lot_number': lot_number, 'files': files})

            if trading_type == 'competition':
                yield Request(url_to_trade, callback=self.parse_lot_auction, headers=header,
                              cookies=cookie_parser(cookie), dont_filter=True,
                              cb_kwargs={'cookie': cookie, 'transfer': transfer, 'url_to_trade': url_to_trade,
                                         'lot_number': lot_number, 'files': files})
        else:
            logger.error(f'{response.url} :: ERROR REDIRECT PAGE TO LOT')

    async def parse_lot_offer(self, response, url_to_trade, cookie, transfer, lot_number, header, files: list):
        """ parse lot with type - offer """
        combo = Combo(_response=response)
        header['Referer'] = response.url
        loader = CrawlerAkostaItemLoader(CrawlerAkostaItem(), response=response)
        loader.add_value('data_origin', transfer['data_origin'])
        loader.add_value('trading_id', transfer['trading_id'])
        loader.add_value('trading_link', transfer['trading_link'])
        loader.add_value('trading_type', transfer['trading_type'])
        loader.add_value('trading_form', transfer['trading_form'])
        loader.add_value('trading_org', transfer['trading_org'])
        loader.add_value('trading_org_inn', transfer['trading_org_inn'])
        loader.add_value('trading_org_contacts', transfer['trading_org_contacts'])
        loader.add_value('trading_number', transfer['trading_number'])
        loader.add_value('msg_number', transfer['msg_number'])
        loader.add_value('case_number', transfer['case_number'])
        loader.add_value('debtor_inn', transfer['debtor_inn'])
        loader.add_value('arbit_manager', transfer['arbit_manager'])
        loader.add_value('arbit_manager_inn', transfer['arbit_manager_inn'])
        loader.add_value('arbit_manager_org', transfer['arbit_manager_org'])
        loader.add_value('status', combo.auc.get_lot_status())
        loader.add_value('lot_id', None)
        loader.add_value('lot_link', response.url)
        loader.add_value('lot_number', lot_number)
        loader.add_value('short_name', combo.auc.get_short_name(lot_number))
        loader.add_value('lot_info', combo.auc.get_lot_info())
        loader.add_value('property_information', combo.auc.get_property_info())
        loader.add_value('start_price', combo.offer.get_start_price())
        lot_files = {'lot': []}
        _files = files
        gen = {'general': _files}
        total_files = dict(chain(gen.items(), lot_files.items()))
        loader.add_value('files', total_files)
        period_first_page = combo.offer.return_periods()
        total_pages_period = combo.offer.return_period_pagination()
        # total_pages_period & total are info about how many pages has pariod table
        if total_pages_period:
            total = copy.deepcopy(total_pages_period)
            del total_pages_period
        else:
            total = 1
        if total > 1:
            _form = copy.deepcopy(post_data_period_offer_page)
            rsl_selection = combo.pre.get_post_data_values(tag_html='input',
                                                           post_argument='formMain:dataRSList_selection')
            _form['formMain:dataRSList_selection'] = rsl_selection
            lot_viewstate2 = combo.pre.get_post_data_values('input', 'j_id1:javax.faces.ViewState:0')
            _form['javax.faces.ViewState'] = lot_viewstate2
            _form['formMain:inputServerTime'] = return_servertime()
            # param data depend from page number -> second page has value - 10
            _form['formMain:dataRSList_first'] = str(10 * 2 - 10)
            if combo.offer.get_refresh_form_j_idt55():
                _form['formMain:j_idt55'] = combo.offer.get_refresh_form_j_idt55()
            yield FormRequest(_link_post_period, callback=self.parse_period_offer_pages, headers=header, formdata=_form,
                              cookies=cookie_parser(cookie), dont_filter=True,
                              cb_kwargs={'cookie': cookie, 'loader': loader, 'header': header,
                                         '_form': _form, 'periods_': period_first_page, 'current': 1, 'total': total})
        else:
            loader.add_value('start_date_requests', combo.offer.get_start_date_request(period_first_page))
            loader.add_value('end_date_requests', combo.offer.get_end_date_request(period_first_page))
            loader.add_value('start_date_trading', combo.offer.get_start_date_request(period_first_page))
            loader.add_value('end_date_trading', combo.offer.get_end_date_request(period_first_page))
            loader.add_value('periods', period_first_page)
            loader.add_value('created_at', return_parse_date())
            yield loader.load_item()

    async def parse_period_offer_pages(self, response, cookie, loader, header, _form, current, total, periods_: list):
        from icecream import ic
        combo = Combo(_response=response)
        next_periods: list = combo.offer.return_next_periods()
        periods_.extend(next_periods)
        if current < total:
            current += 1
            _form['formMain:dataRSList_first'] = str(10 * current - 10)
            _form['formMain:inputServerTime'] = return_servertime()
            yield FormRequest(_link_post_period, callback=self.parse_period_offer_pages, headers=header, formdata=_form,
                              cookies=cookie_parser(cookie), dont_filter=True,
                              cb_kwargs={'cookie': cookie, 'loader': loader, 'header': header,
                                         '_form': _form, 'periods_': periods_, 'current': current, 'total': total})
        else:
            loader.add_value('periods', periods_)
            loader.add_value('start_date_requests', combo.offer.get_start_date_request(periods_))
            loader.add_value('end_date_requests', combo.offer.get_end_date_request(periods_))
            loader.add_value('start_date_trading', combo.offer.get_start_date_request(periods_))
            loader.add_value('end_date_trading', combo.offer.get_end_date_request(periods_))
            loader.add_value('created_at', return_parse_date())
            yield loader.load_item()

    async def parse_lot_auction(self, response, url_to_trade, cookie, transfer, lot_number, files):
        """ parse lot page of auction and competition """
        # with open('res_lot.txt', 'w') as f:
        #     f.write(response.text)
        combo = Combo(_response=response)
        loader = CrawlerAkostaItemLoader(CrawlerAkostaItem(), response=response)
        loader.add_value('data_origin', transfer['data_origin'])
        loader.add_value('trading_id', transfer['trading_id'])
        loader.add_value('trading_link', transfer['trading_link'])
        loader.add_value('trading_type', transfer['trading_type'])
        loader.add_value('trading_form', transfer['trading_form'])
        loader.add_value('trading_org', transfer['trading_org'])
        loader.add_value('trading_org_inn', transfer['trading_org_inn'])
        loader.add_value('trading_org_contacts', transfer['trading_org_contacts'])
        loader.add_value('trading_number', transfer['trading_number'])
        loader.add_value('msg_number', transfer['msg_number'])
        loader.add_value('case_number', transfer['case_number'])
        loader.add_value('debtor_inn', transfer['debtor_inn'])
        loader.add_value('arbit_manager', transfer['arbit_manager'])
        loader.add_value('arbit_manager_inn', transfer['arbit_manager_inn'])
        loader.add_value('arbit_manager_org', transfer['arbit_manager_org'])
        loader.add_value('start_date_requests', transfer['start_date_requests'])
        loader.add_value('end_date_requests', transfer['end_date_requests'])
        loader.add_value('start_date_trading', transfer['start_date_trading'])
        loader.add_value('end_date_trading', transfer['end_date_trading'])
        loader.add_value('status', combo.auc.get_lot_status())
        loader.add_value('lot_id', None)
        loader.add_value('lot_link', response.url)
        loader.add_value('lot_number', lot_number)
        loader.add_value('short_name', combo.auc.get_short_name(lot_number))
        loader.add_value('lot_info', combo.auc.get_lot_info())
        loader.add_value('property_information', combo.auc.get_property_info())
        loader.add_value('start_price', combo.auc.start_price_auction())
        loader.add_value('step_price', combo.auc.step_price_auction())
        lot_files = {'lot': list()}
        _files = files
        gen = {'general': _files}
        total_files = dict(chain(gen.items(), lot_files.items()))
        loader.add_value('files', total_files)
        loader.add_value('created_at', return_parse_date())
        yield loader.load_item()

    def parse_lot_competition(self, response, url_to_trade, cookie, transfer, lot_number):
        pass

    # ERROR CALLBACK FUNCTIONS

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

    @staticmethod
    def error_to_redirect(post_data):
        logger.error(f'{post_data}')

    # @staticmethod
    # def error_pagintaion(page_number):
    #     logger.error(f'{page_number} :: ERROR PAGINATION')
    @staticmethod
    def error_search_request(trade_data):
        logger.error(f'ERROR ::: INVALID SEARCH REQUEST for ::: {trade_data}')
