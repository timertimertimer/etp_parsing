from scrapy import Request

from general_utils import EtpItemLoader, EtpItem, return_parse_date
from general_utils.location import RegionIdentifier
from .base_catalog import LotOnlineBaseSpider
from ..catalog_app import Combo


class LotOnlineBankruptcySpider(LotOnlineBaseSpider):
    name = "lot_online_bankruptcy"
    custom_settings = {
        'ITEM_PIPELINES': {
            'general_utils.pipelines.ETPBankruptPipeline': 300,
        }
    }

    def parse_lot(self, response, lot):
        combo = Combo(response)
        loader = EtpItemLoader(EtpItem(), response=response)
        loader.add_value('data_origin', self.data_origin)
        loader.add_value('trading_id', combo.trading_id)
        loader.add_value('trading_link', combo.trading_link)
        loader.add_value('trading_number', lot[1])
        loader.add_value('trading_type', combo.trading_type)
        loader.add_value('trading_form', combo.trading_form)
        loader.add_value('trading_org', combo.trading_org)
        loader.add_value('trading_org_contacts', combo.trading_org_contacts)
        loader.add_value('msg_number', combo.msg_number)
        loader.add_value('case_number', combo.case_number)
        loader.add_value('debtor_inn', combo.debtor_inn)
        loader.add_value('address', combo.address or combo.sud)
        loader.add_value('arbit_manager', combo.arbit_manager)
        loader.add_value('arbit_manager_inn', combo.arbit_manager_inn)
        loader.add_value('arbit_manager_org', combo.arbit_manager_org)
        loader.add_value('status', lot[3])
        loader.add_value('lot_id', combo.lot_id)
        loader.add_value('lot_link', combo.lot_link)
        loader.add_value('lot_number', combo.get_lot_number(lot[2]))
        loader.add_value('short_name', lot[2])
        loader.add_value('lot_info', combo.lot_info)
        loader.add_value('property_information', combo.property_information)
        loader.add_value(
            'files',
            {'general': combo.download_general(self.domain), 'lot': combo.download_lot(self.domain)}
        )
        loader.add_value('created_at', return_parse_date())
        loader.add_value('start_price', combo.start_price)
        if combo.trading_type == 'offer':
            loader.add_value('periods', combo.periods)
            loader.add_value('start_date_requests', combo.periods[0]['start_date_requests'])
            loader.add_value('end_date_requests', combo.periods[-1]['end_date_requests'])
            loader.add_value('start_date_trading', combo.periods[0]['start_date_requests'])
            loader.add_value('end_date_trading', combo.periods[-1]['end_date_trading'])
            loader.add_value('periods', combo.periods)
            yield loader.load_item()
        else:
            yield Request(combo.get_auc_dates_link(), self.get_auction_info, cb_kwargs={'loader': loader})
