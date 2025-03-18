import logging
from itertools import chain

from scrapy import Request, FormRequest

from general_utils import EtpItem, EtpItemLoader
from .base import RusonBaseSpider
from general_utils.config import write_log_to_file
from ..config import trade_link, data_origin, stop_page, formdata
from ..trades.app import Combo

logger = logging.getLogger(__name__)


class RusonSpider(RusonBaseSpider):
    name = 'ruson'
    custom_settings = {
        'LOG_FILE': f'{name}.log' if write_log_to_file else None,
    }

    def parse_main(self, response):
        yield Request(trade_link[self.name], callback=self.parse_serp, errback=self.errback_httpbin)

    def parse_serp(self, response, **kwargs):
        combo = Combo(response=response)
        for lot_data in combo.serp.get_lots_data():
            type_and_form = combo.serp.get_trading_type_and_form(lot_data[3])
            trading_number = combo.serp.get_trading_number(lot_data[3])
            trading_type = type_and_form[0]
            trading_form = type_and_form[1]
            status = combo.serp.get_status_of_trade(lot_data[4], lot_data[0])
            data_check_with_db = (lot_data[0], lot_data[1], status)
            if data_check_with_db not in self.previous_trades:
                if status == 'active' or status == 'pending':
                    if trading_type == 'auction':
                        yield Request(
                            url=lot_data[0], callback=self.parse_auction,
                            cb_kwargs={'trading_type': trading_type, 'organizer': lot_data[2],
                                       'status': status, 'trading_form': trading_form,
                                       'trading_number': trading_number, 'lot_link': lot_data[1]},
                            errback=self.errback_httpbin, dont_filter=True
                        )
                    elif trading_type == 'offer':
                        yield Request(url=lot_data[0], callback=self.parse_offer,
                                      cb_kwargs={'trading_type': trading_type, 'organizer': lot_data[2],
                                                 'status': status, 'trading_form': trading_form,
                                                 'trading_number': trading_number, 'lot_link': lot_data[1]},
                                      errback=self.errback_httpbin, dont_filter=True)
                    elif trading_type == 'competition':
                        yield Request(url=lot_data[0], callback=self.parse_auction,
                                      cb_kwargs={'trading_type': trading_type, 'organizer': lot_data[2],
                                                 'status': status, 'trading_form': trading_form,
                                                 'trading_number': trading_number, 'lot_link': lot_data[1]},
                                      errback=self.errback_httpbin, dont_filter=True)
                    else:
                        logger.critical(f'{response.url} :: ERROR TRADING TYPE!!!!!!!!!!!!!!!!!!!!!!!!!!')

        current_page = combo.serp.get_curent_page()
        next_page = current_page + 1
        if 0 < next_page < stop_page:
            formdata['pagenum'] = str(next_page)
            yield FormRequest(trade_link[self.name], callback=self.parse_serp,
                              formdata=formdata, method='GET',
                              errback=self.errback_httpbin)

    def parse_auction(self, response, trading_type, organizer, status, trading_form, trading_number, lot_link):
        combo = Combo(response=response)
        transfer = EtpItem()
        transfer['data_origin'] = data_origin[self.name]
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
        transfer['address'] = combo.serp.address
        transfer['arbit_manager'] = combo.serp.get_arbitrator_name()
        transfer['arbit_manager_inn'] = combo.serp.get_arbitr_inn()
        transfer['arbit_manager_org'] = combo.serp.get_arbitr_company()
        transfer['start_date_requests'] = combo.start_date_requests_auc
        transfer['end_date_requests'] = combo.end_date_requests_auc
        transfer['start_date_trading'] = combo.start_date_trading_auc
        general_files = combo.gen.download_general()
        yield Request(url=lot_link, callback=self.parse_auction_lot,
                      cb_kwargs={'general_files': general_files, 'transfer': transfer},
                      errback=self.errback_httpbin)

    def parse_auction_lot(self, response, general_files, transfer):
        """ page lot of auction and competition """
        combo = Combo(response=response)
        loader = EtpItemLoader(EtpItem(), response=response)
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
        loader.add_value('address', transfer['address'])
        loader.add_value('region', transfer['region'])
        loader.add_value('arbit_manager', transfer['arbit_manager'])
        loader.add_value('arbit_manager_inn', transfer['arbit_manager_inn'])
        loader.add_value('arbit_manager_org', transfer['arbit_manager_org'])
        loader.add_value('status', transfer['status'])
        loader.add_value('lot_id', combo.serp.get_trading_id())
        loader.add_value('lot_link', response.url)
        loader.add_value('lot_number', combo.get_lot_number())
        loader.add_value('short_name', combo.offer.get_short_name())
        loader.add_value('lot_info', combo.offer.get_lot_info())
        loader.add_value('property_information', combo.offer.property_info())
        loader.add_value('start_date_requests', transfer['start_date_requests'])
        loader.add_value('end_date_requests', transfer['end_date_requests'])
        loader.add_value('start_date_trading', transfer['start_date_trading'])
        loader.add_value('end_date_trading', None)
        loader.add_value('start_price', combo.offer.start_price())
        loader.add_value('step_price', combo.offer.get_step_price())
        lot_files = combo.lot.download_lot_files(_id=''.join(transfer['trading_id']),
                                                 lot_number=''.join(loader.get_collected_values('lot_number')))
        total_files = dict(chain(general_files.items(),
                                 lot_files.items()))
        loader.add_value('files', total_files)
        yield loader.load_item()

    def parse_offer(self, response, trading_type, organizer, status, trading_form, trading_number, lot_link):
        combo = Combo(response=response)
        transfer = EtpItem()
        transfer['data_origin'] = data_origin
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
        transfer['address'] = combo.serp.address
        transfer['arbit_manager'] = combo.serp.get_arbitrator_name()
        transfer['arbit_manager_inn'] = combo.serp.get_arbitr_inn()
        transfer['arbit_manager_org'] = combo.serp.get_arbitr_company()
        general_files = combo.gen.download_general()
        yield Request(url=lot_link, callback=self.parse_offer_lot,
                      cb_kwargs={'general_files': general_files, 'transfer': transfer},
                      errback=self.errback_httpbin)

    def parse_offer_lot(self, response, general_files, transfer):
        """ parse lot of offer """
        combo = Combo(response=response)
        loader = EtpItemLoader(EtpItem(), response=response)
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
        loader.add_value('address', transfer['address'])
        loader.add_value('region', transfer['region'])
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
        loader.add_value('start_date_requests', combo.offer.start_date_requests())
        loader.add_value('end_date_requests', combo.offer.end_date_requests())
        loader.add_value('start_date_trading', combo.offer.start_date_trading())
        loader.add_value('end_date_trading', combo.offer.end_date_trading())
        if len(''.join(loader.get_collected_values('start_date_requests'))) == 0:
            loader.add_value('start_date_requests', combo.auc.start_date_requests())
            loader.add_value('end_date_requests', combo.auc.end_date_requests())
            loader.add_value('start_date_trading', combo.auc.start_date_requests())
            loader.add_value('end_date_trading', combo.auc.end_date_requests())
        loader.add_value('start_price', combo.offer.start_price())
        loader.add_value('periods', combo.offer.get_periods())
        lot_files = combo.lot.download_files_lot(_id=''.join(transfer['trading_id']),
                                                 lot_number=''.join(loader.get_collected_values('lot_number')))
        total_files = dict(chain(general_files.items(),
                                 lot_files.items()))
        loader.add_value('files', total_files)
        yield loader.load_item()
