from itertools import chain

import scrapy
import scrapy_splash
from scrapy import Request, FormRequest
from scrapy.spidermiddlewares.httperror import HttpError
from scrapy_splash import SplashRequest
from twisted.internet.error import DNSLookupError, TCPTimedOutError

from ..settings import DEFAULT_REQUESTS_HEADERS
from ..items import CrawlerNistpruItemLoader, CrawlerNistpTransferItem, CrawlerNistpruItem
from ..trades.app import Combo
from ..utils.config import start_time, _data_origin, script_lua
from ..utils.download import agent_list, choice
from ..utils.get_data_from_table import DbConnectCheckLots
from ..utils.param_data import param_search as ps
from ..utils.working_with_time import return_parse_date
from ..utils.working_with_url import UrlConfig


class NistpSpider(scrapy.Spider):
    name = 'nistp'
    # allowed_domains = ['nistp.ru']
    start_url = ['https://nistp.ru/']
   
    def __init__(self):
        super(NistpSpider, self).__init__()
        self.url = UrlConfig()
        self.db_check = DbConnectCheckLots()
        self.previous_lots = self.db_check.get_latest_lot()


    def start_requests(self):
        header = DEFAULT_REQUESTS_HEADERS
        # yield SplashRequest(url=''.join(self.start_url),
        #                     endpoint='execute',
        #                     cache_args=['lua_source'],
        #                     args={'lua_source': script_lua},
        #                     slot_policy=scrapy_splash.SlotPolicy.PER_DOMAIN,
        #                     callback=self.parse_, splash_headers=DEFAULT_REQUESTS_HEADERS, cb_kwargs={'header': header},
        #               errback=self.errback_httpbin)
        yield Request(url=''.join(self.start_url), callback=self.parse_, headers=header, cb_kwargs={'header': header},
                      errback=self.errback_httpbin)
        
   
    def parse_(self, response, header):
        """ parse main page and make GET request with params """
        try:
            cookie = response.headers.getlist('Set-Cookie')
        except:
            cookie = ''
        ps['app_start_from'] = start_time
        yield FormRequest(url=''.join(self.start_url), callback=self.search_serp, formdata=ps, method='GET', headers=header,
                          cb_kwargs={'header': header, 'cookie': cookie}, errback=self.errback_httpbin)

    def search_serp(self, response, header, cookie):
        """ parse serp page after GET request with date param """
        combo = Combo(response_=response)
        current_page = combo.serp.get_current_page()
        next_page = combo.serp.get_next_page()
        for link in combo.serp.links_to_trade():
            # header['Referer'] = response.url
            # header['User-Agent'] = choice(agent_list)
            yield Request(url=link[0], callback=self.parse_trade, headers=header,
                          cb_kwargs={'header': header, 'cookie': cookie, 'trading_number': link[1]})

        if current_page < next_page:
            ps['pagenum'] = str(next_page)
            yield FormRequest(url=''.join(self.start_url), callback=self.search_serp, formdata=ps, method='GET',
                              headers=header,
                              cb_kwargs={'header': header, 'cookie': cookie}, errback=self.errback_httpbin)

    #def start_requests(self):
     #   header = DEFAULT_REQUESTS_HEADERS
      #      yield Request(url=i, callback=self.parse_trade, headers=header, cb_kwargs={'header': header, 'trading_number':trading_number},
       #                 errback=self.errback_httpbin)

    def parse_trade(self, response, header, trading_number, cookie):
        """ choose type of trade """
        #try:
        #    cookie = response.headers.getlist('Set-Cookie')
        #except:
         #   cookie = ''
        combo = Combo(response_=response)
        transfer = CrawlerNistpTransferItem()
        trade_type = combo.auc.get_trading_type()
        transfer['data_origin'] = _data_origin['nistp_ru']
        transfer['trading_id'] = combo.auc.get_trading_id()
        transfer['trading_link'] = response.url
        transfer['trading_number'] = trading_number
        transfer['trading_type'] = trade_type
        transfer['trading_form'] = combo.auc.get_trading_form()
        transfer['trading_org'] = combo.auc.get_org_name()
        transfer['trading_org_inn'] = combo.auc.get_inn_org()
        transfer['trading_org_contacts'] = combo.auc.get_org_contacts()
        transfer['msg_number'] = combo.auc.msg_number()
        transfer['case_number'] = combo.auc.case_number()
        transfer['debtor_inn'] = combo.auc.get_inn_debtor()
        transfer['arbit_manager'] = combo.auc.get_arbitr_full_name()
        transfer['arbit_manager_inn'] = combo.auc.get_arbitr_inn()
        transfer['arbit_manager_org'] = combo.auc.get_arbitr_company()
        if trade_type == 'auction' or trade_type == 'competition':
            transfer['start_date_requests'] = combo.auc.start_date_request_auc()
            transfer['end_date_requests'] = combo.auc.end_date_request_auc()
            transfer['start_date_trading'] = combo.auc.start_date_trading_auc()
            transfer['end_date_trading'] = None
        general_files = combo.doc_gen.download_general(_id=''.join(transfer['trading_id']))
        lots_table = combo.auc.count_lots()
        if 'auction' in trade_type:
            return self.parse_auction(response=response, transfer_=transfer, header=header,
                                      cookie=cookie, lots_table=lots_table,
                                      files=general_files)
        if 'offer' in trade_type:
            return self.parse_offer(response=response, transfer_=transfer, header=header,
                                    cookie=cookie, lots_table=lots_table,
                                    files=general_files)
        if 'competition' in trade_type:
            return self.parse_auction(response=response, transfer_=transfer, header=header,
                                      cookie=cookie, lots_table=lots_table,
                                      files=general_files)

    def parse_auction(self, response, transfer_, header, cookie, lots_table, files):
        """ parse all auction lots """
        combo = Combo(response_=response)
        transfer = transfer_
        for i in range(len(lots_table)):
            loader = CrawlerNistpruItemLoader(CrawlerNistpruItem(), response=response)
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
            loader.add_value('status', combo.offer.get_lot_status(lots_table[i]))
            loader.add_value('lot_number', combo.offer.get_lot_number(lots_table[i]))
            check_data = (''.join(transfer['trading_link']), ''.join(loader.get_collected_values('lot_number')))
            if check_data not in self.previous_lots:
                loader.add_value('short_name', combo.offer.get_short_name(lots_table[i]))
                loader.add_value('lot_info', combo.offer.get_lot_info(lots_table[i]))
                loader.add_value('property_information', combo.offer.get_property_info(lots_table[i]))
                loader.add_value('start_date_requests', transfer['start_date_requests'])
                loader.add_value('end_date_requests', transfer['end_date_requests'])
                loader.add_value('start_date_trading', transfer['start_date_trading'])
                loader.add_value('end_date_trading', None)
                loader.add_value('start_price', combo.offer.start_price_AUCTION(table=lots_table[i]))
                loader.add_value('step_price', combo.offer.step_price_AUCTION(table=lots_table[i]))
                general_files = files
                trade_id = ''.join(loader.get_collected_values('trading_id'))
                lot_number_ = loader.get_collected_values('lot_number')
                lot_files = combo.doc_loc.download_lot_files(table=lots_table[i],
                                                             _id=trade_id,
                                                             lot_number=lot_number_)
                files_ = dict(chain(general_files.items(),
                                    lot_files.items()))
                loader.add_value('files', files_)
                loader.add_value('created_at', return_parse_date())

                yield loader.load_item()

    def parse_offer(self, response, transfer_, header, cookie, lots_table, files):
        """ parse all offer lots """
        combo = Combo(response_=response)
        transfer = transfer_
        for i in range(len(lots_table)):
            loader = CrawlerNistpruItemLoader(CrawlerNistpruItem(), response=response)
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
            loader.add_value('status', combo.offer.get_lot_status(lots_table[i]))
            loader.add_value('lot_number', combo.offer.get_lot_number(lots_table[i]))
            check_data = (''.join(transfer['trading_link']), ''.join(loader.get_collected_values('lot_number')))
            if check_data not in self.previous_lots:
                loader.add_value('short_name', combo.offer.get_short_name(lots_table[i]))
                loader.add_value('lot_info', combo.offer.get_lot_info(lots_table[i]))
                loader.add_value('property_information', combo.offer.get_property_info(lots_table[i]))
                loader.add_value('start_date_requests', combo.offer.start_date_request_offer(lots_table[i]))
                loader.add_value('end_date_requests', combo.offer.end_date_request_offer(lots_table[i]))
                loader.add_value('start_date_trading', combo.offer.start_date_trading_offer(lots_table[i]))
                loader.add_value('end_date_trading', combo.offer.end_date_trading_offer(lots_table[i]))
                loader.add_value('start_price', combo.offer.start_price_offer(lots_table[i]))
                loader.add_value('step_price', None)
                loader.add_value('periods', combo.offer.return_periods(lots_table[i]))
                general_files = files
                trade_id = ''.join(loader.get_collected_values('trading_id'))
                lot_number_ = loader.get_collected_values('lot_number')
                lot_files = combo.doc_loc.download_lot_files(table=lots_table[i],
                                                             _id=trade_id,
                                                             lot_number=lot_number_)
                files_ = dict(chain(general_files.items(),
                                    lot_files.items()))
                loader.add_value('files', files_)
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
