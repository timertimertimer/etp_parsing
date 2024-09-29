import copy
import re
from itertools import chain
from icecream import ic
from scrapy import Request, FormRequest, Spider
from scrapy.spidermiddlewares.httperror import HttpError
from twisted.internet.error import DNSLookupError, TCPTimedOutError
from ..items import CrawlerKartotekaRuTransferItem, CrawlerKartotekaRuItemLoader, CrawlerKartotekaRuItem
from ..utils.get_data_from_table import DbConnectCheckLots
from ..utils.param_data import param_data
from ..utils.headers import headers as hd
from ..trades.app import Combo
from ..utils.config import _data_origin
from ..utils.working_with_time import return_parse_date


class KartotekaSpider(Spider):
    name = 'kartoteka'
    start_url = ['https://etp.kartoteka.ru/etp/trade/list.html']

    def __init__(self):
        super(KartotekaSpider, self).__init__()
        self.db_check = DbConnectCheckLots()
        self.previous_lots = self.db_check.get_latest_lot()

    def start_requests(self):
        yield Request(self.start_url[0], self.parse_serp)

    def parse_serp(self, response):
        """ parse page with param form """
        header = copy.deepcopy(hd)
        header['Referer'] = response.url
        yield FormRequest.from_response(response, formdata=param_data, headers=header, callback=self.result_of_serch,
                                        cb_kwargs={'header': header})

    def result_of_serch(self, response, header):
        """ get result of amount of all lots in period """
        combo = Combo(response_=response)
        links = combo.serp.get_links_to_trade_page()
        pagination = combo.serp.get_pagination_next_page()
        header['Referer'] = response.url
        for link in links:
            yield Request(link, callback=self.parse_trading_page, headers=header, dont_filter=True,
                          errback=self.errback_httpbin, cb_kwargs={'header': header})
        if pagination:
            yield Request(pagination, self.result_of_serch, headers=header,
                          cb_kwargs={'header': header})

    def parse_trading_page(self, response, header):
        """ parse the same information """
        combo = Combo(response_=response)
        transfer = CrawlerKartotekaRuTransferItem()
        trading_type = combo.serp.trading_type()
        transfer['data_origin'] = _data_origin['kartoteka']
        transfer['trading_id'] = combo.serp.get_trading_id()
        transfer['trading_link'] = response.url
        transfer['trading_number'] = combo.serp.get_trading_number()
        transfer['trading_type'] = trading_type
        transfer['trading_form'] = combo.serp.get_trading_form()
        transfer['trading_org'] = combo.serp.get_org_name()
        transfer['trading_org_contacts'] = combo.serp.full_org_contacts()
        transfer['msg_number'] = combo.serp.get_msg_number()
        transfer['case_number'] = combo.serp.get_case_number()
        transfer['debtor_inn'] = combo.serp.get_debtor_inn()
        transfer['arbit_manager'] = combo.serp.get_arbitr_name()
        transfer['arbit_manager_org'] = combo.serp.get_arbitr_org()
        transfer['start_date_requests'] = combo.auc.get_start_date_requests_auc()
        transfer['end_date_requests'] = combo.auc.get_end_date_requests_auc()
        transfer['start_date_trading'] = combo.auc.get_start_date_trading_auc()
        transfer['end_date_trading'] = combo.auc.get_end_date_trading_auc()
        # page_number - number by default for first page
        page_number = '1'
        general_files_link = combo.general.get_full_doc_link(combo.serp.get_trading_id())
        link_to_lots_page = combo.serp.get_lots_link(combo.serp.get_trading_id(), page_number)
        yield Request(general_files_link, callback=self.parse_document_page, headers=header,
                      cb_kwargs={'header': header, 'transfer': transfer, 'link_to_lots_page': link_to_lots_page,
                                 'trading_type': trading_type}, dont_filter=True)

    def parse_document_page(self, response, header, transfer, link_to_lots_page, trading_type):
        """ parse and download documents on documen page """
        combo = Combo(response_=response)
        trading_type = trading_type
        general_files_complete = combo.general.download_files_general(_id=''.join(transfer['trading_id']))
        if trading_type == 'offer':
            yield Request(link_to_lots_page, callback=self.parse_offer, headers=header,
                          cb_kwargs={'header': header, 'transfer': transfer, 'general_files': general_files_complete},
                          dont_filter=True)
        if trading_type == 'auction':
            yield Request(link_to_lots_page, callback=self.parse_auction, headers=header,
                          cb_kwargs={'header': header, 'transfer': transfer, 'general_files': general_files_complete},
                          dont_filter=True)
        if trading_type == 'competition':
            yield Request(link_to_lots_page, callback=self.parse_auction, headers=header,
                          cb_kwargs={'header': header, 'transfer': transfer, 'general_files': general_files_complete},
                          dont_filter=True)

    def parse_auction(self, response, header, general_files, transfer):
        """ parse auction type and competition type """
        combo = Combo(response_=response)
        lot_tables = combo.serp.fetch_lots_tables_on_page()
        next_page = combo.serp.find_next_page_lot()
        for table in lot_tables:
            title_th = combo.offer.get_title_lot(table)
            lot_number = combo.offer.get_lot_number(title_th)
            check_data = (lot_number, response.url)
            if check_data not in self.previous_lots:
                loader = CrawlerKartotekaRuItemLoader(CrawlerKartotekaRuItem(), response=response)
                loader.add_value('data_origin', transfer['data_origin'])
                loader.add_value('trading_id', transfer['trading_id'])
                loader.add_value('trading_link', transfer['trading_link'])
                loader.add_value('trading_number', transfer['trading_number'])
                loader.add_value('trading_type', transfer['trading_type'])
                loader.add_value('trading_form', transfer['trading_form'])
                loader.add_value('trading_org', transfer['trading_org'])
                loader.add_value('trading_org_contacts', transfer['trading_org_contacts'])
                loader.add_value('msg_number', transfer['msg_number'])
                loader.add_value('case_number', transfer['case_number'])
                loader.add_value('debtor_inn', transfer['debtor_inn'])
                loader.add_value('arbit_manager', transfer['arbit_manager'])
                loader.add_value('arbit_manager_org', transfer['arbit_manager_org'])
                loader.add_value('status', combo.offer.get_status(table))
                loader.add_value('lot_link', response.url)
                loader.add_value('lot_number', lot_number)
                loader.add_value('short_name', combo.offer.get_short_name(title_th))
                loader.add_value('lot_info', combo.offer.get_lot_info(table))
                loader.add_value('property_information', combo.offer.get_property_info(table))
                loader.add_value('start_date_requests', transfer['start_date_requests'])
                loader.add_value('end_date_requests', transfer['end_date_requests'])
                loader.add_value('start_date_trading', transfer['start_date_trading'])
                loader.add_value('end_date_trading', transfer['end_date_trading'])
                loader.add_value('start_price', combo.offer.start_price(table))
                loader.add_value('step_price', combo.auc.step_price(table, combo.offer.start_price(table)))
                lot_files = combo.lot.download_files_lot(_id=''.join(transfer['trading_id']), table=table,
                                                         lot_number=lot_number)
                total_files = dict(chain(general_files.items(),
                                         lot_files.items()))
                loader.add_value('files', total_files)
                loader.add_value('created_at', return_parse_date())
                yield loader.load_item()

        if next_page:
            current_page = int(combo.serp.get_current_page_lot())
            link_to_lots_page = re.sub(f'page={current_page}', f'page={int(next_page)}', str(response.url))
            yield Request(link_to_lots_page, callback=self.parse_auction, headers=header,
                          cb_kwargs={'header': header, 'transfer': transfer, 'general_files': general_files},
                          dont_filter=True)

    def parse_offer(self, response, header, general_files, transfer):
        """ parse offer type """
        combo = Combo(response_=response)
        lot_tables = combo.serp.fetch_lots_tables_on_page()
        next_page = combo.serp.find_next_page_lot()
        for table in lot_tables:
            title_th = combo.offer.get_title_lot(table)
            lot_number = combo.offer.get_lot_number(title_th)
            check_data = (lot_number, re.sub(r'&_=\d+$', '', str(response.url)))
            if check_data not in self.previous_lots:
                loader = CrawlerKartotekaRuItemLoader(CrawlerKartotekaRuItem(), response=response)
                loader.add_value('data_origin', transfer['data_origin'])
                loader.add_value('trading_id', transfer['trading_id'])
                loader.add_value('trading_link', transfer['trading_link'])
                loader.add_value('trading_number', transfer['trading_number'])
                loader.add_value('trading_type', transfer['trading_type'])
                loader.add_value('trading_form', transfer['trading_form'])
                loader.add_value('trading_org', transfer['trading_org'])
                loader.add_value('trading_org_contacts', transfer['trading_org_contacts'])
                loader.add_value('msg_number', transfer['msg_number'])
                loader.add_value('case_number', transfer['case_number'])
                loader.add_value('debtor_inn', transfer['debtor_inn'])
                loader.add_value('arbit_manager', transfer['arbit_manager'])
                loader.add_value('arbit_manager_org', transfer['arbit_manager_org'])
                loader.add_value('status', combo.offer.get_status(table))
                loader.add_value('lot_link', response.url)
                loader.add_value('lot_number', lot_number)
                loader.add_value('short_name', combo.offer.get_short_name(title_th))
                loader.add_value('lot_info', combo.offer.get_lot_info(table))
                loader.add_value('property_information', combo.offer.get_property_info(table))
                loader.add_value('start_date_requests', combo.offer.start_date_requests_offer(table))
                loader.add_value('end_date_requests', combo.offer.end_date_requests_offer(table))
                loader.add_value('start_date_trading', combo.offer.start_date_trading_ofer(table))
                loader.add_value('end_date_trading', combo.offer.end_date_trading_offer(table))
                loader.add_value('start_price', combo.offer.start_price(table))
                loader.add_value('periods', combo.offer.get_periods_offer(table))
                lot_files = combo.lot.download_files_lot(_id=''.join(transfer['trading_id']), table=table,
                                                         lot_number=lot_number)
                total_files = dict(chain(general_files.items(),
                                         lot_files.items()))
                loader.add_value('files', total_files)
                loader.add_value('created_at', return_parse_date())
                yield loader.load_item()

        if next_page:
            current_page = int(combo.serp.get_current_page_lot())
            link_to_lots_page = re.sub(f'page={current_page}', f'page={int(next_page)}', str(response.url))
            yield Request(link_to_lots_page, callback=self.parse_offer, headers=header,
                          cb_kwargs={'header': header, 'transfer': transfer, 'general_files': general_files},
                          dont_filter=True)

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
