from typing import Iterable

import scrapy
from scrapy import Request, FormRequest

from crawler_moi_tender.crawler_moi_tender.items import CrawlerMoiTenderItemLoader, CrawlerMoiTenderItem
from crawler_moi_tender.crawler_moi_tender.trades.app import Combo
from crawler_moi_tender.crawler_moi_tender.utils.config import format_parse_date, start_time_from, data_origin_url
from crawler_moi_tender.crawler_moi_tender.utils.get_data_from_table import DbConnectCheckLots
from crawler_moi_tender.crawler_moi_tender.utils.working_with_time import return_parse_date


class MoiTenderSpider(scrapy.Spider):
    name = "moi_tender"
    start_urls = ["https://xn--d1abbnoievn.xn--p1ai/tenders.html"]

    def __init__(self):
        super(MoiTenderSpider, self).__init__()
        self.db_check = DbConnectCheckLots()
        self.previous_lots = self.db_check.get_latest_lot()
        self.trade_links = set()
        self.orgs = {}

    def start_requests(self) -> Iterable[Request]:
        params = {
            'filter': 'Y',
            'limit': '100',
            'sort': 'p.date_start',
            'order': 'DESC',
            'f_section': '0',
            'f_date_start_min': start_time_from,
        }
        for trading_type, f_type in enumerate(['offer', 'competition', 'auction'], start=1):
            params['f_type'] = str(f_type)
            yield FormRequest(self.start_urls, formdata=params, dont_filter=True,
                              cb_kwargs={'trading_type': trading_type})

    def parse(self, response, trading_type):
        combo = Combo(response)
        for lot in combo.get_lots():
            if lot[0] not in self.previous_lots:
                if lot[-2] not in self.orgs:
                    yield Request(lot[-1], self.parse_org, cb_kwargs={'lot_data': lot, 'trading_type': trading_type})
                yield Request(lot[0], self.parse_trade, cb_kwargs={'lot_data': lot, 'trading_type': trading_type})

    def parse_org(self, response, lot_data, trading_type):
        combo = Combo(response)
        self.orgs[lot_data[-2]] = combo.trading_org_contacts
        yield Request(lot_data[0], self.parse_trade, cb_kwargs={'lot_data': lot_data, 'trading_type': trading_type})

    def parse_trade(self, response, lot_data, trading_type):
        combo = Combo(response)
        loader = CrawlerMoiTenderItemLoader(CrawlerMoiTenderItem(), response=response)
        loader.add_value('data_origin', data_origin_url)
        loader.add_value('trading_id', lot_data[1])
        loader.add_value('trading_link', response.url)
        loader.add_value('trading_number', lot_data[2])
        loader.add_value('trading_type', trading_type)
        loader.add_value('trading_form', combo.trading_form)
        loader.add_value('trading_org', lot_data[4])
        loader.add_value('trading_org_contacts', combo.trading_org_contacts)
        loader.add_value('status', lot_data[3])
        loader.add_value('category', lot_data[5])
        loader.add_value('index', combo.index)
        loader.add_value('address', combo.address)
        loader.add_value('detailed_address', combo.detailed_address)
        loader.add_value('encumbrance', combo.encumbrance)
        loader.add_value('description_encumbrance', combo.description_encumbrance)
        loader.add_value('lot_number', combo.lot_number)
        loader.add_value('short_name', lot_data[6])
        loader.add_value('lot_info', combo.lot_info)
        loader.add_value('property_information', combo.property_information)
        loader.add_value('start_date_requests', combo.start_date_requests)
        loader.add_value('end_date_requests', combo.end_date_requests)
        loader.add_value('start_date_trading', combo.start_date_trading)
        loader.add_value('end_date_trading', combo.end_date_trading)
        loader.add_value('quantity', combo.quantity)
        loader.add_value('unit', combo.unit)
        loader.add_value('deposit', combo.deposit)
        loader.add_value('min_price', combo.min_price)
        loader.add_value('start_price', combo.start_price)
        loader.add_value('step_price', combo.step_price)
        loader.add_value('periods', combo.periods)
        loader.add_value('files', {'general': combo.download_general(), 'lot': combo.download_lot()})
        loader.add_value('created_at', return_parse_date())
        yield loader.load_item()
