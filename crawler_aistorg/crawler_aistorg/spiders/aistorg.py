# -*- coding: utf-8 -*-

from scrapy.spiders import CrawlSpider
from ..items import AistorgItem, TradingAistorgItem, AistorgItemLoader, DownlodItem, check_trading_type
from ..manage import *
from ..config import *
from scrapy import Request
from scrapy_splash import SplashRequest
from scrapy.spidermiddlewares.httperror import HttpError
from twisted.internet.error import DNSLookupError
from twisted.internet.error import TimeoutError, TCPTimedOutError
import scrapy_splash
import logging
from ..download import DownloadFiles
from crawler_aistorg.settings import DEFAULT_REQUESTS_HEADERS
from ..get_data_from_table import DbConnectCheckLots
import pathlib
from bs4 import BeautifulSoup as BS
from itertools import chain

logger = logging.getLogger(__name__)


class AistorgSpider(CrawlSpider, DownloadFiles):
    name = 'aistorg'
    allowed_domains = ['aistorg.ru']
    total_iterations = int(finish_page) - int(start_page)
    # start_urls = ['http://www.aistorg.ru/']

    # def start_requests(self):
    #     yield Request('http://www.aistorg.ru/reestr/auctions/bankrot/599216/', self.parse_trading)
    # #     yield Request('http://www.aistorg.ru/reestr/auctions/bankrot/589860/', self.parse_trading)

    start_urls = [url_reestr.format(n + int(start_page))
                  for n in range(total_iterations)]

    def __init__(self):
        super(AistorgSpider, self).__init__()
        self.db_check = DbConnectCheckLots()
        self.previous_lots = self.db_check.get_latest_lot()

    def start_requests(self):
        for url in self.start_urls:
            yield SplashRequest(url, self.parse,
                                endpoint='execute',
                                cache_args=['lua_source'],
                                args={'lua_source': script_lua},
                                slot_policy=scrapy_splash.SlotPolicy.PER_DOMAIN,
                                splash_headers=DEFAULT_REQUESTS_HEADERS, session_id=1, errback=self.errback_httpbin)

    def parse(self, response):
        # try:
        #     # _if_cookies_in_list_format.__GET_DICT_FROM_LIST_###
        #     cookies = response.data['cookies']
        #     for c in cookies:
        #         cookies = c
        # except:
        #     cookie = response.headers['Set-Cookie'].decode('utf-8')
        #     cookies = cookie_parser(cookie)
        trading_links = response.css(
            get_links_to_trading()).re(pattern_trade_links)
        for l in trading_links:
            trading_url = main_url + l
            yield Request(url=trading_url, callback=self.parse_trading,
                          #cookies=cookies,
                          errback=self.errback_httpbin)

    def parse_trading(self, response):
        if response.status != 200:
            logger.error(f'CONNECTION ERROR--{response.url}--CONNECTION ERROR')
        else:
            # _check_if_start_date_request_exists_and_meet the criteria_#
            check_date_request = dedent_func(
                response.xpath(start_request_loc).get(default=None))
            try:
                check_date_request = format_time_period(check_date_request)
            except:
                check_date_request = '0000-00-00 00:00:00'
                logger.error(
                    f'{response.url}:::START DATE REQUEST IS NOT FOUND')
            if check_date_request < '2017-01-01 00:00:00':
                logger.info(
                    f'Start date request on--{response.url}--less 2017.01.01')
            else:
                # # set_cookies_request_to_trading_page_###
                # try:
                #     # _if_cookies_in_list_format.__GET_DICT_FROM_LIST_###
                #     cookies = response.data['cookies']
                #     for c in cookies:
                #         cookies = c
                # except:
                #     cookie = (response.headers['Set-Cookie']).decode('utf-8')
                #     cookies = cookie_parser(cookie)
                trade = TradingAistorgItem()
                trade['data_origin'] = main_url
                trade['trading_id'] = trade_id(response.url)
                trade['trading_link'] = response.url
                trade['trading_number'] = dedent_func(
                    response.xpath(trading_num_loc).get())
                type_trade = check_trading_type(dedent_func(
                    response.xpath(trading_form_loc).get()))
                trade['trading_type'] = type_trade
                trade['trading_form'] = dedent_func(
                    response.xpath(trading_form_loc).get())
                trade['trading_status'] = None
                case_number = check_case_number(dedent_func(response.xpath(case_number_loc).get()),
                                                response.url)
                if case_number is None:
                    extra_case_number = check_extra_case_number(dedent_func(response.xpath(extra_case_num_loc).get()),
                                                                response.url)
                    case_number = extra_case_number
                trade['case_number'] = case_number
                msg_number = check_msg_number(dedent_func(
                    response.xpath(msg_number_loc).get()), response.url)
                trade['msg_number'] = msg_number
                # trading_org = dedent_func(response.xpath(organizator_name_loc).get())
                organizator = dedent_func(
                    response.xpath(organizator_loc).get())
                trade['full_name_org'] = organizator
                inn_org = dedent_func(
                    check_inn(response.xpath(organiz_inn_loc).get(), response.url))
                email_org = check_email(response.xpath(
                    organiz_email_loc).get(), response.url)
                phone_org = check_phone(response.xpath(
                    organiz_phone_loc).extract_first(), response.url)
                trade['inn_org'] = inn_org
                contacts = {'email': email_org, 'phone': phone_org}
                trade['trading_contacts'] = contacts
                debit_inn = check_inn(response.xpath(
                    debit_inn_loc).get(), response.url)
                trade['debtor_inn'] = debit_inn
                arbitr_manager = dedent_func(
                    response.xpath(arbitr_manager_loc).get())
                arbitr_org = dedent_func(response.xpath(arbitr_org_loc).get())
                arbitr_manager_inn = dedent_func(
                    response.xpath(arbitr_inn_loc).get())
                if arbitr_manager_inn:
                    arbitr_manager_inn = check_inn(
                        arbitr_manager_inn, response.url)
                    trade['arbit_manager_inn'] = arbitr_manager_inn
                else:
                    trade['arbit_manager_inn'] = None
                trade['arbit_manager'] = clean_names_members(
                    arbitr_manager, response.url)
                trade['arbit_manager_org'] = arbitr_org
                trade['property_information'] = dedent_func(
                    response.xpath(property_info_loc).get())
                start_date_request_auc = dedent_func(
                    response.xpath(start_request_loc).get())
                if start_date_request_auc:
                    try:
                        start_date_request_auc = format_time_period(
                            start_date_request_auc)
                    except:
                        start_date_request_auc = None
                        logger.error(
                            f'{response.url}::INVALID DATA START DATE REQUEST')
                trade['start_date_requests'] = start_date_request_auc
                end_date_request_auc = dedent_func(
                    response.xpath(end_request_loc).get())
                if end_date_request_auc:
                    try:
                        end_date_request_auc = format_time_period(
                            end_date_request_auc)
                    except:
                        end_date_request_auc = None
                        logger.error(
                            f'{response.url}::INVALID DATA END DATE REQUEST')
                trade['end_date_requests'] = end_date_request_auc
                start_date_trade_auc = dedent_func(
                    response.xpath(start_trade_loc).get())
                if start_date_trade_auc:
                    try:
                        start_date_trade_auc = format_time_period(
                            start_date_trade_auc)
                    except:
                        start_date_trade_auc = None
                        logger.warning(
                            f'{response.url}::INVALID DATA START DATE TRADING')
                if start_date_trade_auc is None:
                    try:
                        start_date_trade_auc = dedent_func(
                            response.xpath(extra_start_tading_auc_loc).get())
                        start_date_trade_auc = format_time_period(
                            start_date_trade_auc)
                    except:
                        logger.error(
                            f'{response.url}::START DATE TRADING AUCTION')
                trade['start_date_trading'] = start_date_trade_auc
                lot_liks = response.css(
                    'a[href *= "/reestr/"]').re(pattern_lot_links.format(trade_id(response.url)))
                ###_WORKING_WITH_GENERAL_DOCUMENTS_###
                trade_doc = response.css(
                    'a[href *= "/upload/iblock/"]').getall()
                if len(trade_doc) > 0:
                    doc_trading_page = self.download_trading_files(response)
                else:
                    doc_trading_page = {'general': list()}
                ###_END_WORKING_WITH_GENERAL_DOCUMENTS_###

                for lot in lot_liks:
                    try:
                        lot_link = main_url + replace_html(lot)
                    except:
                        lot_link = None
                        logger.error(
                            f'{response.url}::INVALID DATA LOT URL {replace_html(lot)}')
                    if lot_link not in self.previous_lots:
                        yield Request(url=lot_link,
                                      callback=self.parse_lot,
                                     # cookies=cookies,
                                      errback=self.errback_httpbin,
                                      cb_kwargs=dict(trade=trade,
                                                     doc_trade=doc_trading_page),
                                      )


    def parse_lot(self, response, trade, doc_trade):
        trade = trade
        doc_trading_page = doc_trade
        loader = AistorgItemLoader(AistorgItem(), response=response)
        loader.add_value('data_origin', trade['data_origin'])
        loader.add_value('trading_id', trade['trading_id'])
        loader.add_value('trading_link', trade['trading_link'])
        loader.add_value('trading_number', trade['trading_number'])
        loader.add_value('trading_type', trade['trading_type'])
        loader.add_value('trading_form', trade['trading_form'])
        loader.add_value('status', dedent_func(
            response.xpath(status_loc).get()))
        loader.add_value('msg_number', trade['msg_number'])
        loader.add_value('case_number', trade['case_number'])
        loader.add_value('debtor_inn', trade['debtor_inn'])
        loader.add_value('trading_org', trade['full_name_org'])
        loader.add_value('trading_org_inn', trade['inn_org'])
        loader.add_value('trading_org_contacts', trade['trading_contacts'])
        loader.add_value('arbit_manager', trade['arbit_manager'])
        loader.add_value('arbit_manager_inn', trade['arbit_manager_inn'])
        loader.add_value('arbit_manager_org', trade['arbit_manager_org'])
        lot_number = check_lot_number(
            response.xpath(lot_number_loc).get(), response.url)
        loader.add_value('lot_id', get_lot_id(response.url))
        loader.add_value('lot_link', response.url)
        loader.add_value('lot_number', lot_number)
        loader.add_value('short_name', dedent_func(
            response.xpath(short_name_loc).get()))
        loader.add_value('lot_info', dedent_func(
            response.xpath(lot_info_loc).get()))
        loader.add_value('property_information', trade['property_information'])
        ###_WORKING_WITH_PRICES_###
        start_price = dedent_func(response.xpath(start_price_loc).get())
        if start_price:
            try:
                start_price = make_float(start_price)
            except:
                start_price = None
                logger.error(f'{response.url}:: INVALID DATA START PRICE')
        else:
            start_price = None
            logger.warning(f'{response.url}:; WITHOUT START PRICE')
        step_price = dedent_func(response.xpath(step_price_loc).get())
        if step_price:
            try:
                step_price = make_float(step_price)
            except:
                step_price = None
                logger.warning(f'{response.url}:: INVALID DATA STEP PRICE')
        elif trade['trading_type'] == 'auction' or trade['trading_type'] == 'competition':
            step_price = None
            logger.warning(f'{response.url}:: AUCTION WITHOUT STEP PRICE')
        loader.add_value('start_price', start_price)
        loader.add_value('step_price', step_price)

        ###_WORKING_WITH_DATES_AND_PERIODS_###
        table_periods = response.xpath(period_table_loc)
        if table_periods:
            full_period = []
            for tr in table_periods:
                try:
                    start = tr.xpath('td[4]//text()').get()
                    end = tr.xpath('td[5]//text()').get()
                    price = tr.xpath('td[8]//text()').get()
                    start_date_requests = replaceMultiple(
                        start.strip(), pattern_replace1, ' ')
                    end_date_requests = replaceMultiple(
                        end.strip(), pattern_replace1, ' ')
                    period = {
                        'start_date_requests': format_time_period(start_date_requests),
                        'end_date_requests': format_time_period(end_date_requests),
                        'end_date_trading': format_time_period(end_date_requests),
                        'current_price': make_float(price)

                    }
                except:
                    continue
                full_period.append(period)
            loader.add_value('periods', full_period)
            if trade['trading_type'] == 'offer':
                start_date_requests_offer = dedent_func(
                    response.xpath(start_date_requesr_offer_loc).get())
                start_date_requests_offer = replaceMultiple(
                    start_date_requests_offer.strip(), pattern_replace1, ' ')
                try:
                    start_date_requests_offer = format_time_period(
                        start_date_requests_offer)
                except:
                    start_date_requests_offer = None
                    logger.error(
                        f'{response.url}:; INVALID DATA START DATE REQUEST OFFER')
                end_date_requests_offer = dedent_func(
                    response.xpath(end_date_requesr_offer_loc).get())
                end_date_requests_offer = replaceMultiple(
                    end_date_requests_offer.strip(), pattern_replace1, ' ')
                try:
                    end_date_requests_offer = format_time_period(
                        end_date_requests_offer)
                except:
                    end_date_requests_offer = None
                    logger.error(
                        f'{response.url}:; INVALID DATA END DATE REQUEST OFFER')
                loader.add_value('start_date_requests',
                                 start_date_requests_offer)
                loader.add_value('end_date_requests', end_date_requests_offer)
                loader.add_value('start_date_trading',
                                 start_date_requests_offer)
                loader.add_value('end_date_trading', end_date_requests_offer)
        if trade['trading_type'] == 'auction' or trade['trading_type'] == 'competition':
            loader.add_value('start_date_requests',
                             trade['start_date_requests'])
            loader.add_value('end_date_requests', trade['end_date_requests'])
            loader.add_value('start_date_trading', trade['start_date_trading'])
            loader.add_value('end_date_trading', None)

        lot_doc = response.css('a[href *= "/upload/iblock/"]').getall()
        if len(lot_doc) > 0:
            document_lot = self.download_lot_files(response, lot_number)
        else:
            document_lot = {'lot': list()}
        total_files = dict(
            chain(
                doc_trading_page.items(),
                document_lot.items()))
        loader.add_value('files', total_files)
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

    def download_trading_files(self, response):
        item = DownlodItem()
        load = DownloadFiles()
        general = list()
        table_files = response.xpath(table_trading_files).getall()
        for l in table_files:
            html_elem = BS(str(l), features='lxml')
            if html_elem.a is not None:
                href_ = html_elem.a['href']
                try:
                    original_name = html_elem.select_one(
                        'tr > td:nth-child(3)').get_text()
                    original_name = dedent_func(original_name)
                except:
                    logger.error(f'{response.url}::INVALID FILE NAME')
                    original_name = 'Document'
                link_etp = main_url + str(href_)
                relative_path_server = ''
                if pathlib.Path(link_etp).suffix in lst_ext:
                    create_dir()
                    sufix = pathlib.Path(link_etp).suffix
                    original_name = original_name + sufix
                    name_on_server = name_file_on_server(
                        response.url, original_name)
                    relative_path_server = name_in_column_files(
                        response.url, original_name)
                    load.request_for_download(link_etp, name_on_server)
                if 'Протокол' not in original_name:
                    general.append({'original_name': original_name,
                                    'link': relative_path_server,
                                    'link_etp': link_etp})
        item['general'] = general

        return item

    def download_lot_files(self, response, lot_number):
        item = DownlodItem()
        load = DownloadFiles()
        lot = list()
        table_files = response.xpath(table_lot_files).getall()
        for l in table_files:
            html_elem = BS(str(l), features='lxml')
            if html_elem.a is not None:
                href_ = html_elem.a['href']
                try:
                    original_name = html_elem.select_one('a').get_text()
                    original_name = dedent_func(original_name)
                except:
                    original_name = 'Document'
                link_etp = main_url + str(href_)
                relative_path_server = ''
                if pathlib.Path(link_etp).suffix in lst_ext:
                    create_dir()
                    sufix = pathlib.Path(link_etp).suffix
                    original_name = original_name + sufix
                    name_on_server = name_file_on_server_lot(
                        response.url, original_name, lot_number)
                    relative_path_server = name_in_column_files_lot(
                        response.url, original_name, lot_number)
                    load.request_for_download(link_etp, name_on_server)
                if 'Протокол' not in original_name:
                    lot.append({'original_name': original_name,
                                'link': relative_path_server,
                                'link_etp': link_etp})
        item['lot'] = lot

        return item
