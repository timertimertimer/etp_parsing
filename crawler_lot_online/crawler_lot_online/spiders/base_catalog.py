import json
from typing import Iterable
from datetime import datetime
from scrapy import Spider, Request, FormRequest

from general_utils.config import format_parse_date
from general_utils.items import CrawlerNonBankruptItem, CrawlerNonBankruptItemLoader
from general_utils.location import RegionIdentifier, get_index
from ..catalog_app import Combo
from ..utils.config import formdata, hashes, start_date
from general_utils import DBHelper, return_parse_date


class LotOnlineBaseSpider(Spider):
    name = 'lot_online_base'
    start_urls = ['https://catalog.lot-online.ru/index.php']
    data_origin = 'https://lot-online.ru/'
    custom_settings = {
        # 'LOG_FILE': f'{name}.log'
    }

    def __init__(self, domain):
        super(LotOnlineBaseSpider, self).__init__()
        self.db_check = DBHelper(f'lots_{self.name}')
        self.previous_lots = self.db_check.get_latest_lot()
        self.domain = domain

    def start_requests(self) -> Iterable[Request]:
        start_timestamp = int(datetime.strptime(start_date, '%d.%m.%Y').timestamp())
        end_timestamp = int(datetime.strptime(format_parse_date(-1), '%d.%m.%Y').timestamp()) - 1
        formdata['features_hash'] = f'112-{start_timestamp}-{end_timestamp}_{hashes[self.domain]}'
        yield FormRequest(self.start_urls[0], self.parse_serp, formdata=formdata, method='POST')

    def parse_serp(self, response):
        html = json.loads(response.text)['html']['pagination_contents']
        combo = Combo(response)
        for lot in combo.get_lots(html):
            if (lot[0],) not in self.previous_lots:
                yield Request(lot[0], self.parse_lot, cb_kwargs={'lot': lot})

        if combo.next_page(html):
            formdata['page'] = str(int(formdata['page']) + 1)
            yield FormRequest(self.start_urls[0], self.parse_serp, formdata=formdata, method='POST')

    def parse_lot(self, response, lot):
        combo = Combo(response)
        loader = CrawlerNonBankruptItemLoader(CrawlerNonBankruptItem(), response=response)
        loader.add_value('data_origin', self.data_origin)
        loader.add_value('trading_id', combo.trading_id)
        loader.add_value('trading_link', combo.trading_link)
        loader.add_value('trading_number', lot[1])
        loader.add_value('trading_type', combo.trading_type)
        loader.add_value('trading_form', combo.trading_form)
        loader.add_value('trading_org', combo.trading_org)
        loader.add_value('trading_org_contacts', combo.trading_org_contacts)
        loader.add_value('status', lot[3])
        address = combo.address
        region = None
        if address:
            region = RegionIdentifier.get_region(address)
        loader.add_value('index', get_index(address))
        loader.add_value('address', address)
        loader.add_value('region', region)
        loader.add_value('encumbrance', 'Нет')
        loader.add_value('lot_number', combo.get_lot_number(lot[2]))
        loader.add_value('short_name', lot[2])
        loader.add_value('lot_info', combo.lot_info)
        loader.add_value('property_information', combo.property_information)
        loader.add_value(
            'files',
            {'general': combo.download_general(self.domain), 'lot': combo.download_lot(self.domain)}
        )
        loader.add_value('start_price', combo.start_price)
        loader.add_value('created_at', return_parse_date())
        if combo.trading_type == 'offer' and combo.periods:
            loader.add_value('periods', combo.periods)
            loader.add_value('start_date_requests', combo.periods[0]['start_date_requests'])
            loader.add_value('end_date_requests', combo.periods[-1]['end_date_requests'])
            loader.add_value('start_date_trading', combo.periods[0]['start_date_requests'])
            loader.add_value('end_date_trading', combo.periods[-1]['end_date_trading'])
            yield loader.load_item()
        else:
            yield Request(combo.get_auc_dates_link(), self.get_auction_info, cb_kwargs={'loader': loader})

    def get_auction_info(self, response, loader):
        combo = Combo(response)
        loader.add_value('start_price', combo.start_price)
        loader.add_value('start_date_requests', combo.start_date_requests_auc)
        loader.add_value('end_date_requests', combo.end_date_requests_auc)
        loader.add_value('step_price', combo.step_price)
        yield loader.load_item()
