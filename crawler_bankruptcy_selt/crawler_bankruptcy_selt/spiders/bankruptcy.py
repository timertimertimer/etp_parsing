# -*- coding: utf-8 -*-
from scrapy.spiders import CrawlSpider

from ..get_data_from_table import DbConnectCheckLots
from ..items import BankruptcyItem, TradingBankruptcyItem, BankruptcyItemLoader, DownlodItem, check_trading_type
from scrapy.spidermiddlewares.httperror import HttpError
from twisted.internet.error import DNSLookupError
from twisted.internet.error import TimeoutError, TCPTimedOutError
from ..manage import *
from ..config import *
from scrapy import Request
import logging
from ..download import DownloadFiles
import pathlib
from bs4 import BeautifulSoup as BS
from itertools import chain
from pprint import pprint

logger = logging.getLogger(__name__)


class BankruptcySpider(CrawlSpider, DownloadFiles):
    name = 'bankruptcy'
    # allowed_domains = ['bankruptcy.selt-online.ru']

    start_url = [url_main_pagination.format(start_page)]

    def __init__(self):
        super(BankruptcySpider, self).__init__()
        self.db_check = DbConnectCheckLots()
        self.previous_lots = self.db_check.get_latest_lot()

    def start_requests(self):
        yield Request(self.start_url[0], self.parse_main)

    #    def start_requests(self):
    #        yield Request('http://bankruptcy.selt-online.ru/Trade/AnounsmentDetails/213364', self.check_pagination_trading_page)
    # # #     # yield Request('http://bankruptcy.selt-online.ru/Trade/AnounsmentDetails/214701', self.parse_trade)
    # # #     # yield Request('http://bankruptcy.selt-online.ru/Trade/AnounsmentDetails/214700', self.parse_trade)

    ###_PAGINATION_###
    def parse_main(self, response):
        links = response.xpath(get_links_to_trading()).re(pattern_trade_links)
        all_links_set = set(map(lambda x: x, links))
        for l in all_links_set:
            status = dedent_func(response.xpath(get_status(l)).get())
            link = host_url + l
            if link not in self.previous_lots:
                yield Request(url=host_url + l, callback=self.check_pagination_trading_page,
                              meta={'status': status})
        next_page = response.xpath(get_next_page()).get()
        if next_page:
            next_page_link = clean_next_page(next_page, url_main_pagination)
            if next_page_link != f'http://bankruptcy.selt-online.ru/?page={stop_page}&ascending=False':
                yield response.follow(next_page_link, callback=self.parse_main)

    def check_pagination_trading_page(self, response):
        status = response.meta['status']
        paginator = response.xpath('//div[@id="paginator"]//a[last()]').get()

        if paginator:
            get_paginator = ''.join(re.findall(r'page=\d+', paginator))
            clean_pagination = ''.join(re.findall(r'\d+', get_paginator))
            for i in range(int(clean_pagination)):
                i = i + 1
                yield Request(url=str(response.url) + f'?page={i}', callback=self.parse_trade,
                              meta={'status': status}, errback=self.errback_httpbin, dont_filter=True)

        else:
            yield Request(url=response.url, callback=self.parse_trade,
                          meta={'status': status}, errback=self.errback_httpbin, dont_filter=True)

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

    def parse_trade(self, response):
        if response.status != 200:
            logger.error(f'CONNECTION ERROR--{response.url}--CONNECTION ERROR')
        else:
            # _check_if_start_date_request_exists_and_meet the criteria_#
            check_date_request = dedent_func(
                response.xpath(get_start_request()).get(default=None))
            try:
                check_date_request = format_time(check_date_request)
            except:
                check_date_request = '0000-00-00 00:00:00'
                logger.error(
                    f'{response.url}:::START DATE REQUEST IS NOT FOUND')
            if check_date_request < '2017-01-01 00:00:00':
                logger.info(
                    f'Start date request on--{response.url}--less 2017.01.01')
            else:
                trade = TradingBankruptcyItem()
                trade['data_origin'] = main_url
                trade['trading_id'] = trade_id(response.url)
                trade['trading_link'] = response.url
                trade['trading_number'] = trade_id(response.url)
                type_trade = dedent_func(
                    response.xpath(trading_type_loc).get())
                if type_trade:
                    type_trade = check_trading_type(type_trade)
                else:
                    logger.error(f'{response.url}--WITHOUT Type Trade ')
                trade['trading_type'] = dedent_func(
                    response.xpath(trading_type_loc).get())
                trade['trading_form'] = dedent_func(
                    response.xpath(trading_type_loc).get())
                trade['trading_status'] = response.meta['status']
                # _variables_#_ORGANIZATOR_INFO_###
                inn_org = dedent_func(response.xpath(
                    get_inn_org()).extract_first())
                if inn_org:
                    inn_org = check_inn(inn_org)
                last_name = dedent_func(response.xpath(
                    get_last_name()).extract_first())
                first_name = dedent_func(response.xpath(
                    get_first_name()).extract_first())
                middle_name = dedent_func(
                    response.xpath(get_mid_name()).extract_first())
                email_org = dedent_func(response.xpath(
                    get_email_org()).extract_first())
                if email_org:
                    email_org = check_email(email_org)
                phone_org = dedent_func(response.xpath(
                    get_phone_org()).extract_first())
                if phone_org:
                    phone_org = check_phone(phone_org)
                organizator_if_company = dedent_func(
                    response.xpath(get_if_company()).extract_first())
                organizator_if_company_short = dedent_func(
                    response.xpath(get_if_company_short()).extract_first())
                if organizator_if_company is None:
                    organizator_if_company = organizator_if_company_short
                # _end_variables_#_ORGANIZATOR_INFO_###
                trade['inn_org'] = inn_org
                full_name = get_full_name_info(last_name, first_name, middle_name, response.url,
                                               organizator_if_company)
                contacts_org = {'email': email_org, 'phone': phone_org}
                trade['full_name'] = full_name
                trade['trading_contacts'] = contacts_org
                trade['debtor_inn'] = check_inn(dedent_func(
                    response.xpath(get_debitor_inn()).get()))
                trade['msg_number'] = check_msg_number(dedent_func(response.xpath(get_msg_number()).get()),
                                                       response.url)
                trade['case_number'] = check_case_number(dedent_func(response.xpath(get_case_number()).get()),
                                                         response.url)
                arbitr_last_name = dedent_func(response.xpath(
                    arbitr_last_name_loc).get(default=None))
                arbitr_first_name = dedent_func(response.xpath(
                    arbitr_first_name_loc).get(default=None))
                arbitr_middle_name = dedent_func(response.xpath(
                    arbitr_middl_name_loc).get(default=None))
                full_name_arbitr = get_full_name_info(arbitr_last_name, arbitr_first_name, arbitr_middle_name,
                                                      response.url)
                arbitr_inn = check_inn(dedent_func(
                    response.xpath(arb_man_inn).get()))
                arbitr_organiz = dedent_func(
                    response.xpath(arbit_manager_org_loc).get())
                trade['arbit_manager'] = full_name_arbitr
                trade['arbit_manager_inn'] = arbitr_inn
                trade['arbit_manager_org'] = arbitr_organiz

                ###_WORKING_WITH_DATES_INFLUENCE_AUCTION_###
                # _start_date_request_#
                start_date_request = dedent_func(
                    response.xpath(start_date_request_loc).get())
                if start_date_request:
                    try:
                        start_date_request = format_time(start_date_request)
                    except:
                        start_date_request = None
                        logger.error(
                            f'{response.url} START DATE REQUEST INCLUDE INVALID DATA')
                else:
                    logger.error(
                        f'TRADE on page {response.url} --WITHOUT START DATE REQUEST')
                trade['start_date_requests'] = start_date_request
                # _end_date_request_#
                end_date_requests = dedent_func(
                    response.xpath(end_date_requests_loc).get())
                if end_date_requests:
                    try:
                        end_date_requests = format_time(end_date_requests)
                    except:
                        end_date_requests = None
                        logger.error(
                            f'{response.url} END DATE REQUEST INCLUDE INVALID DATA')
                else:
                    logger.error(
                        f'TRADE on page {response.url} --WITHOUT END DATE REQUEST')
                trade['end_date_requests'] = end_date_requests
                # _start_date_trading_#
                start_date_trading = dedent_func(
                    response.xpath(start_date_trading_loc).get())
                if start_date_trading:
                    try:
                        start_date_trading = format_time(start_date_trading)
                    except:
                        start_date_trading = None
                        logger.error(
                            f'{response.url} START DATE TRADING INCLUDE INVALID DATA')
                trade['start_date_trading'] = start_date_trading
                if start_date_trading is None and str(type_trade) == 'auction':
                    logger.warning(
                        f'{response.url} AUCTION WITHOUT START DATE TRADING ')
                # end_date_trading_#
                end_date_trading = dedent_func(
                    response.xpath(end_date_trading_loc).get())
                if end_date_trading:
                    try:
                        end_date_trading = format_time(end_date_trading)
                    except:
                        end_date_trading = None
                        logger.warning(
                            f'{response.url} END DATE TRADING INCLUDE INVALID DATA')
                trade['end_date_trading'] = end_date_trading
                if end_date_trading is None and str(type_trade) == 'auction':
                    logger.warning(
                        f'{response.url} AUCTION WITHOUT END DATE TRADING')

                # _count_lots_#
                lot_titles = response.xpath(all_lot_title).getall()
                amount_lots = len(lot_titles)
                if amount_lots == 0:
                    amount_lots = 1
                for num in range(amount_lots):
                    try:
                        lot_number = get_lot_number(
                            dedent_func(lot_titles[num]))
                    except:
                        lot_number = None
                        logger.error(
                            f'{response.url} - WITHOUT LOT NUMBER or INVALID DATA')
                    loader = BankruptcyItemLoader(
                        BankruptcyItem(), response=response)
                    loader.add_value('data_origin', trade['data_origin'])
                    loader.add_value('trading_id', trade['trading_id'])
                    loader.add_value('trading_link', trade['trading_link'])
                    loader.add_value('trading_number', trade['trading_number'])
                    loader.add_value('trading_type', trade['trading_type'])
                    loader.add_value('trading_form', trade['trading_form'])
                    loader.add_value('status', trade['trading_status'])
                    loader.add_value('msg_number', trade['msg_number'])
                    loader.add_value('case_number', trade['case_number'])
                    loader.add_value('debtor_inn', trade['debtor_inn'])
                    loader.add_value('trading_org', trade['full_name'])
                    loader.add_value('trading_org_inn', trade['inn_org'])
                    loader.add_value('trading_org_contacts',
                                     trade['trading_contacts'])
                    loader.add_value('arbit_manager', trade['arbit_manager'])
                    loader.add_value('arbit_manager_inn',
                                     trade['arbit_manager_inn'])
                    loader.add_value('arbit_manager_org',
                                     trade['arbit_manager_org'])
                    loader.add_value('lot_id', None)  # None
                    loader.add_value('lot_link', None)  # None
                    loader.add_value('lot_number', lot_number)
                    loader.add_value('short_name', dedent_func(
                        response.xpath(get_short_name(lot_number)).get()))
                    loader.add_value('lot_info', None)  # None
                    loader.add_value('property_information', None)  # None

                    ###_WORKING_WITH_PERIODS_AND_DATES_OFFER_###
                    period_data = response.xpath(
                        get_period_data(lot_number)).getall()
                    full_period = list()
                    if period_data:
                        period_data = clean_periods(period_data)
                    if period_data and len(period_data) > 1 and str(type_trade) == 'offer':
                        try:
                            start_date_requests_offer = period_data[0][0] + \
                                                        " " + period_data[0][1]
                            end_date_requests_offer = period_data[-1][2] + \
                                                      " " + period_data[-1][3]
                            start_date_requests_offer = format_time_period(
                                start_date_requests_offer)
                            end_date_requests_offer = format_time_period(
                                end_date_requests_offer)
                            loader.add_value(
                                'start_date_requests', start_date_requests_offer)
                            loader.add_value(
                                'end_date_requests', end_date_requests_offer)
                            loader.add_value(
                                'start_date_trading', start_date_requests_offer)
                            loader.add_value(
                                'end_date_trading', end_date_requests_offer)
                        except Exception as e:
                            logger.error(
                                f'{response.url} -- ERROR DURING WORK WITH DATES OFFER {traceback.format_exc(e)}')

                        for iter in range(len(period_data)):
                            start = period_data[iter][0] + \
                                    " " + period_data[iter][1]
                            end = period_data[iter][2] + \
                                  " " + period_data[iter][3]
                            price = period_data[iter][4]
                            period = {
                                'start_date_requests': format_time_period(start),
                                'end_date_requests': format_time_period(end),
                                'end_date_trading': format_time_period(end),
                                'current_price': make_float(price)

                            }

                            full_period.append(period)
                    elif str(type_trade) == 'offer':
                        loader.add_value('start_date_requests',
                                         trade['start_date_requests'])
                        loader.add_value('end_date_requests',
                                         trade['end_date_requests'])
                        loader.add_value('start_date_trading',
                                         trade['start_date_requests'])
                        loader.add_value('end_date_trading',
                                         trade['end_date_requests'])
                        logger.warning(
                            f'{response.url}--{type_trade} WITHOUT  PERIOD ', exc_info=True)
                    loader.add_value('periods', full_period)

                    if str(type_trade) == 'auction':
                        loader.add_value('start_date_requests',
                                         trade['start_date_requests'])
                        loader.add_value('end_date_requests',
                                         trade['end_date_requests'])
                        loader.add_value('start_date_trading',
                                         trade['start_date_trading'])
                        loader.add_value('end_date_trading',
                                         trade['end_date_trading'])

                    ###_WORKING_WITH_PRICE_###
                    start_price = dedent_func(response.xpath(
                        get_start_price(lot_number)).get())
                    if start_price:
                        try:
                            start_price = make_float(start_price)
                        except:
                            start_price = None
                            logger.error(
                                f'{response.url}::INVALID DATA START PRICE')
                    step_price = dedent_func(response.xpath(
                        get_step_price(lot_number)).get())
                    if step_price:
                        try:
                            step_price = make_float(step_price)
                        except:
                            step_price = None
                            logger.error(
                                f'{response.url}::INVALID DATA STEP PRICE')
                    if str(type_trade) == 'auction' and step_price is None:
                        logger.warning(
                            f'{response.url}:: AUCTION WITHOUT STEP PRICE')

                    if str(type_trade) == 'offer':
                        step_price = None

                    loader.add_value('start_price', start_price)
                    loader.add_value('step_price', step_price)

                    files = self.download_trading_files(response)
                    extra_files = {'lot': list()}
                    total_files = dict(
                        chain(
                            files.items(),
                            extra_files.items()))
                    loader.add_value('files', total_files)
                    loader.add_value('created_at', return_parse_date())
                    ###_END_WORKING_WITH_PERIODS_AND_DATES_OFFER_###
                    yield loader.load_item()

    def download_trading_files(self, response):
        item = DownlodItem()
        load = DownloadFiles()
        general = list()
        lst_files = response.xpath(tr_files).getall()
        for l in lst_files:
            picture = BS(str(l), features='lxml')
            icon = picture.img['src']
            file_ext = pathlib.Path(icon).stem
            href_ = picture.a['href']
            link_etp = host_url + str(href_)
            original_name = dedent_func(picture.a.get_text())
            relative_path_server = ''
            if '/Trade/' in href_ and (file_ext in lst_ext):
                create_dir()
                original_name = original_name + "." + file_ext
                name_on_server = name_file_on_server(
                    response.url, original_name)
                relative_path_server = name_in_column_files(
                    response.url, original_name)
                load.request_for_download(link_etp, name_on_server)
            if 'Протокол' not in original_name and '/Trade/' in href_:
                general.append({'original_name': original_name,
                                'link': relative_path_server,
                                'link_etp': link_etp})
        item['general'] = general

        return item
