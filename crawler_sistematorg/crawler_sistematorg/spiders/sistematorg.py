# -*- coding: utf-8 -*-
from scrapy.spiders import CrawlSpider

from general_utils import EtpItem, EtpItemLoader
import pathlib

from general_utils.config import lst_exet
from ..get_data_from_table import DbConnectCheckLots
from scrapy import Request
from ..manage import *
from ..config import *
from ..download import DownloadFiles
from twisted.internet.error import DNSLookupError
from twisted.internet.error import TimeoutError, TCPTimedOutError
from scrapy.spidermiddlewares.httperror import HttpError
from bs4 import BeautifulSoup as BS
import traceback
import logging

logger = logging.getLogger(__name__)


def check_trading_type(string: str = None):
    """
    Check what type of trade
    :return:
    """
    offer = ['Публичное предложение',
             'Закрытое публичное предложение']
    auction = ['Аукцион с открытой формой представления цены',
               'Аукцион с закрытой формой представления цены',
               'Закрытый аукцион с открытой формой представления цены',
               'Закрытый аукцион с закрытой формой представления цены']
    competition = ['Конкурс с открытой формой представления цены',
                   'Конкурс с закрытой формой представления цены',
                   'Закрытый конкурс с открытой формой представления цены',
                   'Закрытый конкурс с закрытой формой представления цены']

    if str(string).strip() in auction:
        return 'auction'
    elif str(string).strip() in offer:
        return 'offer'
    elif (str(string).strip() in competition):
        return 'competition'
    else:
        return None


def check_trading_form(string: str = None):
    """
    Check what form
    :param form:str
    :return: trading form: open/closed
    """
    open_form = ['Аукцион с открытой формой представления цены',
                 'Аукцион с закрытой формой представления цены',
                 'Конкурс с открытой формой представления цены',
                 'Конкурс с закрытой формой представления цены',
                 'Публичное предложение']
    close_form = ['Закрытый аукцион с открытой формой представления цены',
                  'Закрытый аукцион с закрытой формой представления цены',
                  'Закрытый конкурс с открытой формой представления цены',
                  'Закрытый конкурс с закрытой формой представления цены',
                  'Закрытое публичное предложение']

    if str(string).strip() in open_form:
        return 'open'
    elif str(string).strip() in close_form:
        return 'close'
    else:
        return None


def check_status(status_lot: str = None):
    """
    Check status
    :param status: str
    :return: staus of trade
    """
    active = ('Прием заявок',)
    pending = ('Торги объявлены',)
    ended = ('Прием заявок завершен', 'Идут торги', 'Подведение итогов',
             'Торги завершены', 'Торги не состоялись', 'Торги отменены')
    try:
        if str(status_lot).strip() in active:
            return 'active'
        elif str(status_lot).strip() in pending:
            return 'pending'
        elif str(status_lot).strip() in ended:
            return 'ended'
    except:
        return None


class SistematorgSpider(CrawlSpider, DownloadFiles):
    name = bot_name
    allowed_domains = [allowed_domain]
    start_urls = [main_url_list.format(n + int(start_page)) for n in range(int(finish_page) - int(start_page))]
    addresses = dict()

    def __init__(self):
        super(SistematorgSpider, self).__init__()
        self.db_check = DbConnectCheckLots()
        self.previous_lots = self.db_check.get_latest_lot()

    def start_requests(self):
        for url in self.start_urls:
            yield Request(url, self.parse)

    def parse(self, response):
        all_links = response.xpath(LINKS_to_TRADING_pages_loc).re(pattern_trade_links)
        all_links_set = set(map(lambda x: x, all_links))
        for url in all_links_set:
            url = ''.join(main_url) + url
            yield Request(url=str(url), callback=self.parse_lots, errback=self.errback_httpbin,
                          dont_filter=True
                          )

    def parse_lots(self, response):
        trade = EtpItem()
        trade['data_origin'] = ''.join(main_url)
        trade['trading_link'] = response.url
        trade['trading_id'] = trade_id(response.url)
        trade['trading_number'] = response.xpath(trading_number_loc).get()
        trade['trading_type'] = check_trading_type(response.xpath(trading_form_loc).get())
        trade['trading_form'] = check_trading_form(response.xpath(trading_form_loc).get())
        trade['trading_org'] = check_name(response.xpath(fms_name_org).get())
        trade['trading_org_contacts'] = {'email': check_email(
            response.xpath(email_org_loc).get()),
            'phone': check_phone(response.xpath(
                phone_org_loc).get())
        }
        trade['msg_number'] = check_msg_number(response.url,
                                               response.xpath(msg_num_loc).get())
        trade['case_number'] = check_case_number(url=response.url,
                                                 case_number=response.xpath(case_number_loc).get())
        trade['debtor_inn'] = check_inn(response.xpath(debitor_inn_loc).get())
        trade['address'] = response.xpath(address_loc).get()
        arbit_name = response.xpath(arbitr_first_name_loc).get()
        arbit_surname = response.xpath(arbit_last_name_loc).get()
        arbit_middle = response.xpath(arbitr_middle_name_loc).get()
        trade['arbit_manager'] = get_org_info(arbit_surname,
                                              arbit_name,
                                              arbit_middle,
                                              response.url)
        trade['arbit_manager_inn'] = check_inn(response.xpath(arbitr_inn).get())
        trade['arbit_manager_org'] = check_name(response.xpath(arbitr_org).get())
        type_trade = trade['trading_type']
        start_request = response.xpath(start_date_requests_loc).get()
        end_request = response.xpath(end_date_requests_loc).get()
        start_trading = response.xpath(start_date_trading_loc).get()
        if start_request:
            try:
                trade['start_date_requests'] = format_time(start_request)
            except:
                logger.error(f'{response.url}::WITHOUT START DATE REQUEST OR INVALID DATA!!!')
        else:
            logger.error(f'{response.url}::WITHOUT START DATE REQUEST!!!')
        try:
            trade['end_date_requests'] = format_time(end_request)
        except:
            trade['end_date_requests'] = None
            logger.error(f'{response.url}::WITHOUT END DATE REQUEST OR INVALID DATA!!!')
        if str(type_trade) == 'auction' or str(type_trade) == 'competition':
            try:
                trade['start_date_trading'] = format_time(start_trading)
            except:
                logger.error(f'{response.url}::AUCTION WITHOUT START TRADING OR INVALID DATA!!!')
        # _working_with_file_trade_table_#
        files_trade_general = response.xpath(get_general_files())
        all_files = response.xpath(all_files_loc).getall()
        files_general = self.download_files(response)
        ###_check_how_many_lots_on_page_###
        lots_on_page = response.xpath(get_amount_lots()).getall()
        amount_lots = int(len(lots_on_page))
        th_lot_title = response.xpath(th_lot_number).getall()
        if amount_lots < 1:
            amount_lots = 1
        for num in range(amount_lots):
            lot_number = th_lot_title[num]
            lot_number = clean_lot_number(str(lot_number))
            if (str(response.url), lot_number) not in self.previous_lots:
                loader = EtpItemLoader(EtpItem(), response=response)
                loader.add_value('data_origin', trade['data_origin'])
                loader.add_value('trading_id', trade['trading_id'])
                loader.add_value('trading_link', trade['trading_link'])
                loader.add_value('trading_number', trade['trading_number'])
                loader.add_value('trading_type', trade['trading_type'])
                loader.add_value('trading_form', trade['trading_form'])
                loader.add_value('trading_org', trade['trading_org'])
                loader.add_value('trading_org_inn', None)
                loader.add_value('trading_org_contacts', trade['trading_org_contacts'])
                loader.add_value('msg_number', trade['msg_number'])
                loader.add_value('case_number', trade['case_number'])
                loader.add_value('debtor_inn', trade['debtor_inn'])
                loader.add_value('address', trade['address'])
                loader.add_value('arbit_manager', trade['arbit_manager'])
                loader.add_value('arbit_manager_inn', trade['arbit_manager_inn'])
                loader.add_value('arbit_manager_org', trade['arbit_manager_org'])
                loader.add_value('lot_id', None)
                loader.add_value('lot_link', None)
                loader.add_value('lot_number', lot_number)

                loader.add_value('status',
                                 check_status(''.join(response.xpath(get_status(lot_number)).extract_first())))
                ######################_END_VARIABLES_######status_get#######################
                loader.add_value('short_name', response.xpath(get_short_name(lot_number)).get())
                loader.add_value('lot_info', response.xpath(get_lot_info(lot_number)).get())
                loader.add_value('property_information', response.xpath(get_property_info(lot_number)).get())
                start_request_offer = response.xpath(get_start_request_offer(lot_number)).get()
                end_request_offer = response.xpath(get_end_request_offer(lot_number)).get()
                if start_request_offer and str(type_trade) == 'offer':
                    try:
                        loader.add_value('start_date_requests', format_time(start_request_offer))
                        loader.add_value('end_date_requests', format_time(end_request_offer))
                        loader.add_value('start_date_trading', format_time(start_request_offer))
                        loader.add_value('end_date_trading', format_time(end_request_offer))
                    except:
                        loader.add_value('start_date_requests', trade['start_date_requests'])
                        loader.add_value('end_date_requests', trade['end_date_requests'])
                        loader.add_value('start_date_trading', trade['start_date_requests'])
                        loader.add_value('end_date_trading', trade['end_date_requests'])
                        logger.error(f'{response.url}::INVALID DATA _ OFFER_PERIODS_TABLE{traceback.format_exc()}')
                elif str(type_trade) == 'offer':
                    loader.add_value('start_date_requests', trade['start_date_requests'])
                    loader.add_value('end_date_requests', trade['end_date_requests'])
                    loader.add_value('start_date_trading', trade['start_date_requests'])
                    loader.add_value('end_date_trading', trade['end_date_requests'])
                    logger.error(f'{response.url}::CHECK LOTS IF CORRECT INFO!!!!!!!!')
                elif str(type_trade) == 'auction' or str(type_trade) == 'competition':
                    loader.add_value('start_date_requests', trade['start_date_requests'])
                    loader.add_value('end_date_requests', trade['end_date_requests'])
                    loader.add_value('start_date_trading', trade['start_date_trading'])
                    loader.add_value('end_date_trading', None)

                start_price = response.xpath(get_start_price(lot_number)).get()
                step_price = response.xpath(get_step_price(lot_number)).get()
                if start_price:
                    try:
                        loader.add_value('start_price', make_float(start_price))
                    except:
                        logger.error(f'{response.url}::INVALID START PRICE')
                if str(type_trade) == 'auction':
                    if step_price is not None:
                        try:
                            loader.add_value('step_price', make_float(step_price))
                        except:
                            logger.error(f'{response.url}:;AUCTION WITHOUT STEP_PRICE OR INVALID DATA')
                    else:
                        logger.error(f'{response.url}:;AUCTION WITHOUT STEP_PRICE OR INVALID DATA')
                ###_WORKING_WITH_TABLE_PERIODS_IF_OFFER_###
                table_periods = response.xpath(get_table_periods(lot_number))
                full_period = []
                for tr in table_periods:
                    try:
                        start = tr.xpath('td[1]//text()').get()
                        end = tr.xpath('td[2]//text()').get()
                        price = tr.xpath('td[3]//text()').get()
                        start_date_requests = replaceMultiple(start, pattern_replace, ' ')
                        end_date_requests = replaceMultiple(end, pattern_replace, ' ')
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
                status = loader.get_collected_values('status')[0]
                # _work_with_lot_files_(if_exists)_#
                if status == 'active' or status == 'pending':
                    lot_files = list()
                    if len(all_files) > len(files_trade_general):
                        lot_files = self.download_lot_files(response, lot_number)
                    total_files = {'general': files_general, 'lot': lot_files}
                    loader.add_value('files', total_files)
                    loader.add_value('created_at', return_parse_date())
                    yield loader.load_item()

    def download_files(self, response):
        load = DownloadFiles()
        # soup = BS(response.text, 'lxml')
        general = list()
        selector_links = response.xpath(files_generel_loc).getall()
        for l in selector_links:
            link_soup = BS(str(l), features="lxml")
            l = link_soup.a['href']
            link_etp = str(l)
            original_name = str(link_soup.get_text()).strip()
            original_name = dedent_func(original_name)
            relative_path_server = ''
            if pathlib.Path(original_name).suffix in lst_exet:
                create_dir()
                name_on_server = name_file_on_server(response.url, original_name)
                relative_path_server = name_in_column_files(response.url, original_name)
                load.request_for_download(link_etp, name_on_server)

            general.append({'original_name': original_name,
                            'link': relative_path_server,
                            'link_etp': link_etp})
        return general

    def download_lot_files(self, response, lot_number):
        load = DownloadFiles()
        lot = list()
        selector_links = response.xpath(get_lot_files(lot_number)).getall()
        for l in selector_links:
            link_soup = BS(str(l), features="lxml")
            l = link_soup.a['href']
            link_etp = str(l)
            original_name = str(link_soup.get_text()).strip()
            original_name = dedent_func(original_name)
            relative_path_server = ''
            if pathlib.Path(original_name).suffix in lst_exet:
                create_dir()
                name_on_server = name_file_on_server_lot(response.url, original_name, lot_number)
                relative_path_server = name_in_column_files_lot(response.url, original_name, lot_number)
                load.request_for_download(link_etp, name_on_server)

            lot.append({'original_name': original_name,
                        'link': relative_path_server,
                        'link_etp': link_etp})
        return lot

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
