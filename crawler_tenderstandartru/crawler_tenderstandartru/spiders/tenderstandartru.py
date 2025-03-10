from general_utils import EtpItem, EtpItemLoader
from ..libraries.libraries import *
from ..utils.config import trades, tables
from ..utils.working_with_url import UrlConfig

logger = logging.getLogger(__name__)
TABLE = tables['tenderstandart']


class TenderstandartruSpider(Spider):
    name = 'tenderstandartru'
    data_origin = data_origin['tenderstandart']
    custom_settings = {
        # 'LOG_FILE': f'{name}.log',
    }

    def __init__(self):
        super(TenderstandartruSpider, self).__init__()
        self.db_check = DbConnectCheckLots()
        self.previous_lots = self.db_check.get_latest_lot(TABLE)
        self.url = UrlConfig()

    def start_requests(self):
        for trade in trades:
            yield Request(url=self.url.url_join(self.data_origin, trade), callback=self.parse_auction_main, 
                          cb_kwargs={'page': 1})

    def parse_auction_main(self, response, page):
        """ parse response(serp) of current type of trade and make requests with param to search active lots"""
        combo = Combo(response, self.data_origin)
        trading_type = combo.serp.get_trading_type()
        length = combo.serp.get_length_param()
        types_ = combo.serp.get_types_param()
        timestamp_ = combo.serp.get_time_stamp()
        sp['Length'] = length
        sp['types'] = types_
        sp['_'] = timestamp_
        yield FormRequest(url=self.url.url_join(self.data_origin, 'Trade/AllSearch'), callback=self.parse_serp,
                          formdata=sp, method='GET',
                           cb_kwargs={'page': page, 'trading_type': trading_type}, dont_filter=True,
                          errback=self.errback_httpbin)

    def parse_serp(self, response, page, trading_type):
        """ parse output of lots in period mention in param data """
        combo = Combo(response, self.data_origin)
        for lot_data in combo.serp.get_lots_data_from_div_table():
            # [0] - trading page; [1] - lot_link; [2] - lot_number; [3] - organizer; [4] - status; [5] - start price [6] - start date trading
            status = combo.serp.get_status(lot_data[4]) if any(lot_data) else None
            if status == 'active' or status == 'pending':
                transfer = EtpItem()
                transfer['trading_type'] = trading_type
                transfer['data_origin'] = self.data_origin
                transfer['trading_id'] = combo.serp.get_trading_id(lot_data[0])
                transfer['trading_number'] = transfer['trading_id']
                transfer['trading_link'] = lot_data[0]
                transfer['trading_org'] = lot_data[3]
                transfer['status'] = status
                transfer['lot_number'] = lot_data[2]
                transfer['lot_link'] = lot_data[1]
                transfer['start_price'] = lot_data[5]
                transfer['start_date_trading'] = lot_data[6]
                data_check_with_db = (lot_data[0], lot_data[1], status)
                if data_check_with_db not in self.previous_lots:
                    yield Request(url=lot_data[0], callback=self.parse_trading_page,
                                   cb_kwargs={'transfer': transfer, 'trading_type': trading_type},
                                  dont_filter=True,
                                  errback=self.errback_httpbin)
        page += 1
        if next_page := combo.serp.get_next_page_link(page, self.data_origin):
            yield Request(url=next_page, callback=self.parse_serp, 
                          cb_kwargs={'page': page, 'trading_type': trading_type}, errback=self.errback_httpbin)

    def parse_trading_page(self, response, transfer, trading_type):
        """ parse trading page - according traing type """
        combo = Combo(response, self.data_origin)
        transfer['trading_org_inn'] = combo.auc.get_organizer_inn()
        transfer['trading_org_contacts'] = combo.auc.get_full_org_contacts()
        transfer['case_number'] = combo.auc.get_case_number()
        transfer['debtor_inn'] = combo.auc.get_debtor_inn()
        transfer['address'] = combo.auc.address
        transfer['arbit_manager'] = combo.auc.get_arbitr_name()
        transfer['arbit_manager_org'] = combo.auc.get_arbitr_company()
        transfer['property_information'] = combo.auc.get_property_information()
        general_files = combo.gen.download_files_general(_id=''.join(transfer['trading_id']), data_origin=self.data_origin)
        if trading_type == 'offer':
            yield Request(url=''.join(transfer['lot_link']), callback=self.parse_periods_offer, 
                          cb_kwargs={'transfer': transfer, 'general_files': general_files,
                                     'page_offer': 1, 'periods': list()})
        else:
            yield Request(url=''.join(transfer['lot_link']), callback=self.parse_auction_lot, 
                          cb_kwargs={'transfer': transfer, 'general_files': general_files})

    def parse_periods_offer(self, response, transfer, page_offer, general_files, periods):
        """ parse periods on offer(lot page) """
        combo = Combo(response, self.data_origin)
        page_offer += 1
        next_page = combo.serp.get_next_page_link(page_offer, self.data_origin)
        period = combo.offer.get_periods()
        periods.extend(period)
        if next_page:
            yield Request(url=next_page, callback=self.parse_periods_offer, 
                          cb_kwargs={'transfer': transfer, 'general_files': general_files, 'page_offer': page_offer,
                                     'periods': periods},
                          errback=self.errback_httpbin)
        else:
            yield Request(url=''.join(transfer['lot_link']), callback=self.parse_offer_lot, 
                          cb_kwargs={'transfer': transfer, 'general_files': general_files, 'periods': periods},
                          dont_filter=True)

    def parse_auction_lot(self, response, transfer, general_files):
        """ parse lot page """
        combo = Combo(response, self.data_origin)
        loader = EtpItemLoader(EtpItem(), response=response)
        loader.add_value('data_origin', transfer['data_origin'])
        loader.add_value('trading_id', transfer['trading_id'])
        loader.add_value('trading_link', transfer['trading_link'])
        loader.add_value('trading_number', transfer['trading_number'])
        loader.add_value('trading_type', transfer['trading_type'])
        loader.add_value('trading_form', combo.auc.trading_form_div())
        loader.add_value('trading_org', transfer['trading_org'])
        loader.add_value('trading_org_inn', transfer['trading_org_inn'])
        loader.add_value('trading_org_contacts', transfer['trading_org_contacts'])
        loader.add_value('msg_number', combo.auc.get_msg_number())
        loader.add_value('case_number', transfer['case_number'])
        loader.add_value('debtor_inn', transfer['debtor_inn'])
        loader.add_value('address', transfer['address'])
        loader.add_value('arbit_manager', transfer['arbit_manager'])
        loader.add_value('arbit_manager_org', transfer['arbit_manager_org'])
        loader.add_value('status', transfer['status'])
        loader.add_value('msg_number', combo.auc.get_msg_number())
        loader.add_value('lot_id', combo.serp.get_trading_id(response.url))
        loader.add_value('lot_link', transfer['lot_link'])
        loader.add_value('lot_number', transfer['lot_number'])
        loader.add_value('short_name', combo.auc.get_short_name())
        loader.add_value('lot_info', combo.auc.get_lot_info())
        loader.add_value('property_information', transfer['property_information'])
        loader.add_value('start_date_requests', combo.auc.start_date_requests_auction())
        loader.add_value('end_date_requests', combo.auc.end_date_requests_auction())
        loader.add_value('start_date_trading', transfer['start_date_trading'])
        loader.add_value('start_price', transfer['start_price'])
        loader.add_value('step_price', combo.auc.get_step_price(loader.get_collected_values('start_price')))
        lot_files = combo.lot.download_files_lot(_id=''.join(loader.get_collected_values('lot_id')),
                                                 lot_number=''.join(loader.get_collected_values('lot_number')),
                                                 data_origin=self.data_origin)
        total_files = dict(chain(general_files.items(),
                                 lot_files.items()))
        loader.add_value('files', total_files)
        loader.add_value('created_at', return_parse_date())
        yield loader.load_item()

    def parse_offer_lot(self, response, transfer, general_files, periods):
        """ parse lot page """
        combo = Combo(response, self.data_origin)
        loader = EtpItemLoader(EtpItem(), response=response)
        loader.add_value('data_origin', transfer['data_origin'])
        loader.add_value('trading_id', transfer['trading_id'])
        loader.add_value('trading_link', transfer['trading_link'])
        loader.add_value('trading_number', transfer['trading_number'])
        loader.add_value('trading_type', transfer['trading_type'])
        loader.add_value('trading_form', combo.auc.trading_form_div())
        loader.add_value('trading_org', transfer['trading_org'])
        loader.add_value('trading_org_inn', transfer['trading_org_inn'])
        loader.add_value('trading_org_contacts', transfer['trading_org_contacts'])
        loader.add_value('msg_number', combo.auc.get_msg_number())
        loader.add_value('case_number', transfer['case_number'])
        loader.add_value('debtor_inn', transfer['debtor_inn'])
        loader.add_value('address', transfer['address'])
        loader.add_value('arbit_manager', transfer['arbit_manager'])
        loader.add_value('arbit_manager_org', transfer['arbit_manager_org'])
        loader.add_value('status', transfer['status'])
        loader.add_value('msg_number', combo.auc.get_msg_number())
        loader.add_value('lot_id', combo.serp.get_trading_id(response.url))
        loader.add_value('lot_link', transfer['lot_link'])
        loader.add_value('lot_number', transfer['lot_number'])
        loader.add_value('short_name', combo.auc.get_short_name())
        loader.add_value('lot_info', combo.auc.get_lot_info())
        loader.add_value('property_information', transfer['property_information'])
        loader.add_value('start_date_requests', combo.offer.get_start_date_request(periods))
        loader.add_value('end_date_requests', combo.offer.get_end_date_request(periods))
        loader.add_value('start_date_trading', combo.offer.get_start_date_request(periods))
        loader.add_value('end_date_trading', combo.offer.get_end_date_request(periods))
        loader.add_value('start_price', transfer['start_price'])
        lot_files = combo.lot.download_files_lot(_id=''.join(loader.get_collected_values('lot_id')),
                                                 lot_number=''.join(loader.get_collected_values('lot_number')),
                                                 data_origin=self.data_origin)
        total_files = dict(chain(general_files.items(),
                                 lot_files.items()))
        loader.add_value('files', total_files)
        loader.add_value('periods', periods)
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
