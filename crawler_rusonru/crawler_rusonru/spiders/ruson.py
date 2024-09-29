from itertools import chain

from icecream import ic
from scrapy import Spider, Request, FormRequest
from scrapy.spidermiddlewares.httperror import HttpError
from twisted.internet.error import DNSLookupError, TCPTimedOutError

from ..items import CrawlerRusonTransferItem, CrawlerRusonruItem, CrawlerRusonruItemLoader
from ..trades.app import Combo
from ..utils.config import _data_origin, _trade_link, stop_page
from ..utils.get_data_from_table import DbConnectCheckLots
from ..utils.headers import header as hd
import logging

from ..utils.pagination_param_data import param_data
from ..utils.working_with_time import return_parse_date

logger = logging.getLogger(__name__)


class RusonSpider(Spider):
    name = 'ruson'
    allowed_domains = ['rus-on.ru']
    start_url = _data_origin['rus-on']

    def __init__(self):
        super(RusonSpider, self).__init__()
        self.db_check = DbConnectCheckLots()
        self.previous_lots = self.db_check.get_latest_lot()

    def start_requests(self):
        yield Request(self.start_url, self.parse_main)

    def parse_main(self, response):
        """ parse main page and make request to serp with  """
        hd['Referer'] = response.url
        yield Request(_trade_link['rus-on'], callback=self.parse_serp, headers=hd, errback=self.errback_httpbin)

    def parse_serp(self, response):
        """ parse pagination pages with short lot data (serp) """
        combo = Combo(response_=response)
        hd['Referer'] = response.url
        for lot_data in combo.serp.get_lots_data():
            # [0] - trading page; [1] - lot_link; [2] - organizer; [3] - trading type and form; [4] - status
            type_and_form = combo.serp.get_trading_type_and_form(lot_data[3])
            trading_number = combo.serp.get_trading_number(lot_data[3])
            trading_type = type_and_form[0]
            trading_form = type_and_form[1]
            status = combo.serp.get_status_of_trade(lot_data[4], lot_data[0])
            data_check_with_db = (lot_data[0], lot_data[1], status)
            if data_check_with_db not in self.previous_lots:
                if status == 'active' or status == 'pending':
                    if trading_type == 'auction':
                        yield Request(url=lot_data[0], callback=self.parse_auction, headers=hd,
                                      cb_kwargs={'trading_type': trading_type, 'organizer': lot_data[2],
                                                 'status': status, 'trading_form': trading_form,
                                                 'trading_number': trading_number, 'lot_link': lot_data[1]},
                                      errback=self.errback_httpbin, dont_filter=True)
                    elif trading_type == 'offer':
                        yield Request(url=lot_data[0], callback=self.parse_offer, headers=hd,
                                      cb_kwargs={'trading_type': trading_type, 'organizer': lot_data[2],
                                                 'status': status, 'trading_form': trading_form,
                                                 'trading_number': trading_number, 'lot_link': lot_data[1]},
                                      errback=self.errback_httpbin, dont_filter=True)
                    elif trading_type == 'competition':
                        yield Request(url=lot_data[0], callback=self.parse_auction, headers=hd,
                                      cb_kwargs={'trading_type': trading_type, 'organizer': lot_data[2],
                                                 'status': status, 'trading_form': trading_form,
                                                 'trading_number': trading_number, 'lot_link': lot_data[1]},
                                      errback=self.errback_httpbin, dont_filter=True)
                    else:
                        logger.critical(f'{response.url} :: ERROR TRADING TYPE!!!!!!!!!!!!!!!!!!!!!!!!!!')

        current_page = combo.serp.get_curent_page()
        next_page = current_page + 1
        if 0 < next_page < stop_page:
            param_data['pagenum'] = str(next_page)
            yield FormRequest('https://rus-on.ru/trades', callback=self.parse_serp, headers=hd,
                              formdata=param_data, method='GET',
                              errback=self.errback_httpbin)

    def parse_auction(self, response, trading_type, organizer, status, trading_form, trading_number, lot_link):
        """ page auction and competition page """
        combo = Combo(response_=response)
        transfer = CrawlerRusonTransferItem()
        transfer['data_origin'] = _data_origin['rus-on']
        transfer['trading_id'] = combo.serp.get_trading_id()
        transfer['trading_link'] = response.url,
        transfer['trading_number'] = trading_number
        transfer['trading_type'] = trading_type
        transfer['trading_form'] = trading_form
        transfer['trading_org'] = organizer
        transfer['trading_org_inn'] = combo.serp.get_organizer_inn()
        transfer['trading_org_contacts'] = combo.serp.get_organizer_contacts()
        transfer['status'] = status
        transfer['msg_number'] = combo.serp.get_msg_number()
        transfer['case_number'] = combo.serp.get_case_number()
        transfer['debtor_inn'] = combo.serp.get_debtor_inn()
        transfer['arbit_manager'] = combo.serp.get_arbitrator_name()
        transfer['arbit_manager_inn'] = combo.serp.get_arbitr_inn()
        transfer['arbit_manager_org'] = combo.serp.get_arbitr_company()
        transfer['start_date_requests'] = combo.auc.start_date_requests()
        transfer['end_date_requests'] = combo.auc.end_date_requests()
        transfer['start_date_trading'] = combo.auc.start_date_trading()
        general_files = combo.gen.download_files_general(_id=''.join(transfer['trading_id']))
        yield Request(url=lot_link, callback=self.parse_auction_lot, headers=hd,
                      cb_kwargs={'general_files': general_files, 'transfer': transfer},
                      errback=self.errback_httpbin)

    def parse_auction_lot(self, response, general_files, transfer):
        """ page lot of auction and competition """
        combo = Combo(response_=response)
        loader = CrawlerRusonruItemLoader(CrawlerRusonruItem(), response=response)
        loader.add_value('data_origin', transfer['data_origin'])
        loader.add_value('trading_id', transfer['trading_id'])
        loader.add_value('trading_link', transfer['trading_link'])
        loader.add_value('trading_number', transfer['trading_number'])
        loader.add_value('trading_type', transfer['trading_type'])
        loader.add_value('trading_form', transfer['trading_form'])
        loader.add_value('trading_org', transfer['trading_org'])
        loader.add_value('trading_org_inn', transfer['trading_org_inn'])
        loader.add_value('trading_org_contacts', transfer['trading_org_contacts'])
        loader.add_value('msg_number', transfer['msg_number'])
        loader.add_value('case_number', transfer['case_number'])
        loader.add_value('debtor_inn', transfer['debtor_inn'])
        loader.add_value('arbit_manager', transfer['arbit_manager'])
        loader.add_value('arbit_manager_inn', transfer['arbit_manager_inn'])
        loader.add_value('arbit_manager_org', transfer['arbit_manager_org'])
        loader.add_value('status', transfer['status'])
        loader.add_value('lot_id', combo.serp.get_trading_id())
        loader.add_value('lot_link', response.url)
        loader.add_value('lot_number', combo.offer.get_lot_number())
        loader.add_value('short_name', combo.offer.get_short_name())
        loader.add_value('lot_info', combo.offer.get_lot_info())
        loader.add_value('property_information', combo.offer.property_info())
        loader.add_value('start_date_requests', transfer['start_date_requests'])
        loader.add_value('end_date_requests', transfer['end_date_requests'])
        loader.add_value('start_date_trading', transfer['start_date_trading'])
        loader.add_value('end_date_trading', None)
        loader.add_value('start_price', combo.offer.start_price())
        loader.add_value('step_price', combo.offer.step_price())
        lot_files = combo.lot.download_files_lot(_id=''.join(transfer['trading_id']),
                                                 lot_number=''.join(loader.get_collected_values('lot_number')))
        total_files = dict(chain(general_files.items(),
                                 lot_files.items()))
        loader.add_value('files', total_files)
        loader.add_value('created_at', return_parse_date())
        yield loader.load_item()

    def parse_offer(self, response, trading_type, organizer, status, trading_form, trading_number, lot_link):
        """ parse offer page """

        combo = Combo(response_=response)
        transfer = CrawlerRusonTransferItem()
        transfer['data_origin'] = _data_origin['rus-on']
        transfer['trading_id'] = combo.serp.get_trading_id()
        transfer['trading_link'] = response.url
        transfer['trading_number'] = trading_number
        transfer['trading_type'] = trading_type
        transfer['trading_form'] = trading_form
        transfer['trading_org'] = organizer
        transfer['trading_org_inn'] = combo.serp.get_organizer_inn()
        transfer['trading_org_contacts'] = combo.serp.get_organizer_contacts()
        transfer['status'] = status
        transfer['msg_number'] = combo.serp.get_msg_number()
        transfer['case_number'] = combo.serp.get_case_number()
        transfer['debtor_inn'] = combo.serp.get_debtor_inn()
        transfer['arbit_manager'] = combo.serp.get_arbitrator_name()
        transfer['arbit_manager_inn'] = combo.serp.get_arbitr_inn()
        transfer['arbit_manager_org'] = combo.serp.get_arbitr_company()
        general_files = combo.gen.download_files_general(_id=''.join(transfer['trading_id']))
        yield Request(url=lot_link, callback=self.parse_offer_lot, headers=hd,
                      cb_kwargs={'general_files': general_files, 'transfer': transfer},
                      errback=self.errback_httpbin)

    def parse_offer_lot(self, response, general_files, transfer):
        """ parse lot of offer """
        combo = Combo(response_=response)
        loader = CrawlerRusonruItemLoader(CrawlerRusonruItem(), response=response)
        loader.add_value('data_origin', transfer['data_origin'])
        loader.add_value('trading_id', transfer['trading_id'])
        loader.add_value('trading_link', transfer['trading_link'])
        loader.add_value('trading_number', transfer['trading_number'])
        loader.add_value('trading_type', transfer['trading_type'])
        loader.add_value('trading_form', transfer['trading_form'])
        loader.add_value('trading_org', transfer['trading_org'])
        loader.add_value('trading_org_inn', transfer['trading_org_inn'])
        loader.add_value('trading_org_contacts', transfer['trading_org_contacts'])
        loader.add_value('msg_number', transfer['msg_number'])
        loader.add_value('case_number', transfer['case_number'])
        loader.add_value('debtor_inn', transfer['debtor_inn'])
        loader.add_value('arbit_manager', transfer['arbit_manager'])
        loader.add_value('arbit_manager_inn', transfer['arbit_manager_inn'])
        loader.add_value('arbit_manager_org', transfer['arbit_manager_org'])
        loader.add_value('status', transfer['status'])
        loader.add_value('lot_id', combo.serp.get_trading_id())
        loader.add_value('lot_link', response.url)
        loader.add_value('lot_number', combo.offer.get_lot_number())
        loader.add_value('short_name', combo.offer.get_short_name())
        loader.add_value('lot_info', combo.offer.get_lot_info())
        loader.add_value('property_information', combo.offer.property_info())

        # START: if period table doesn't exist, take value of dates from trading info section
        loader.add_value('start_date_requests', combo.offer.start_date_requests())
        loader.add_value('end_date_requests', combo.offer.end_date_requests())
        loader.add_value('start_date_trading', combo.offer.start_date_trading())
        loader.add_value('end_date_trading', combo.offer.end_date_trading())
        if len(''.join(loader.get_collected_values('start_date_requests'))) == 0:
            loader.add_value('start_date_requests', combo.auc.start_date_requests())
            loader.add_value('end_date_requests', combo.auc.end_date_requests())
            loader.add_value('start_date_trading', combo.auc.start_date_requests())
            loader.add_value('end_date_trading', combo.auc.end_date_requests())
        # END

        loader.add_value('start_price', combo.offer.start_price())
        loader.add_value('periods', combo.offer.return_periods())
        lot_files = combo.lot.download_files_lot(_id=''.join(transfer['trading_id']),
                                                 lot_number=''.join(loader.get_collected_values('lot_number')))
        total_files = dict(chain(general_files.items(),
                                 lot_files.items()))
        loader.add_value('files', total_files)
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
