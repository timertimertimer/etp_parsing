import json
from typing import Iterable

from scrapy import Spider, Request, FormRequest

from general_utils.items import CrawlerNonBankruptItem, CrawlerNonBankruptItemLoader
from general_utils.location import RegionIdentifier, get_index
from ..app import Combo
from ..utils.config import formdata, data_origin, search_link, trade_link
from general_utils import DBHelper, return_parse_date


class TorgiGovSpider(Spider):
    name = 'torgigov'

    def __init__(self):
        super(TorgiGovSpider).__init__()
        self.db_check = DBHelper(f'lots_{self.name}')
        self.previous_lots = self.db_check.get_latest_lot(['lot_id'])

    def start_requests(self) -> Iterable[Request]:
        yield FormRequest(search_link, self.parse_serp, formdata=formdata, method='GET')

    def parse_serp(self, response):
        data = json.loads(response.text)
        for trade in data['content']:
            if trade['id'] not in self.previous_lots:
                yield Request(f'{trade_link}/{trade["id"]}', self.parse_trade)
        if (int(data['number']) + 1) * int(data['size']) < int(data['totalElements']):
            formdata['page'] = str(int(formdata['page']) + 1)
            yield FormRequest(search_link, self.parse_serp, formdata=formdata, method='GET')

    def parse_trade(self, response):
        data = json.loads(response.text)
        combo = Combo(data)
        loader = CrawlerNonBankruptItemLoader(CrawlerNonBankruptItem(), response=response)
        loader.add_value('data_origin', data_origin)
        loader.add_value('trading_id', combo.trading_id)
        loader.add_value('trading_link', combo.trading_link)
        loader.add_value('trading_number', combo.trading_number)
        loader.add_value('trading_type', combo.trading_type)
        loader.add_value('trading_form', combo.trading_form)
        loader.add_value('trading_org', combo.trading_org)
        loader.add_value('trading_org_contacts', combo.trading_org_contacts)
        loader.add_value('status', combo.status)
        loader.add_value('start_date_requests', combo.start_date_requests)
        loader.add_value('end_date_requests', combo.end_date_requests)
        loader.add_value('start_date_trading', combo.start_date_trading)
        loader.add_value('end_date_trading', combo.end_date_trading)
        general_files = combo.download_general()
        for lot in combo.get_lots():
            loader.add_value('address', combo.get_address(lot))
            loader.add_value('lot_number', combo.get_lot_number(lot))
            loader.add_value('category', combo.get_category(lot))
            loader.add_value('short_name', combo.get_short_name(lot))
            loader.add_value('lot_info', combo.get_lot_info(lot))
            loader.add_value('deposit', combo.get_deposit(lot))
            loader.add_value('start_price', combo.get_start_price(lot))
            loader.add_value('step_price', combo.get_step_price(lot))
            loader.add_value('min_price', combo.get_start_price(lot))
            loader.add_value('files', {'general': general_files, 'lot': combo.download_lot(lot)})
            # yield loader.load_item()
