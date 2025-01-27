from typing import Iterable

import scrapy
from scrapy import Request, FormRequest

from general_utils import DBHelper, headers, CrawlerBankruptItem, CrawlerBankruptItemLoader, UrlConfig, \
    return_parse_date
from ..trades.app import Combo
from ..config import data_origin, start_date, end_date


class UralbidinSpider(scrapy.Spider):
    name = "uralbidin"
    data_origin = data_origin['uralbidin']
    start_urls = ["https://uralbidin.ru/lots"]
    custom_settings = {
        'DEFAULT_REQUEST_HEADERS': headers | {'Host': 'uralbidin.ru'},
        # 'LOG_FILE': f'{name}.log',
    }

    def __init__(self):
        super(UralbidinSpider).__init__()
        self.db_check = DBHelper(self.custom_settings.get('TABLE_NAME', f'lots_{self.name}'))
        self.previous_lots = self.db_check.get_latest_lot()

    def start_requests(self) -> Iterable[Request]:
        params_data = {
            'applications_start_date': f'{start_date} ⇆ {end_date}',
            'applications_start_date_from': start_date,
            'applications_start_date_to': end_date
        }
        yield FormRequest(self.start_urls[0], self.parse, formdata=params_data, method='GET')

    def parse(self, response):
        links = response.xpath('//a[@class="blue-text bold"]/@href').getall()
        for link in links:
            if (link,) not in self.previous_lots:
                yield Request(UrlConfig.url_join(self.data_origin, link), self.parse_trade)

        pagination = response.xpath('//ul[@class="pagination"]').get()
        if pagination:
            next_page_link = response.xpath('//a[@rel="next"]/@href').get()
            if next_page_link:
                yield Request(next_page_link, self.parse)

    def parse_trade(self, response):
        combo = Combo(response)
        trading_id = trading_number = combo.id_
        trading_link = response.url
        trading_type, trading_form = combo.trading_type_and_form
        trading_org = combo.trading_org
        trading_org_inn = combo.trading_org_inn
        trading_org_contacts = combo.trading_org_contacts
        msg_number = combo.msg_number
        case_number = combo.case_number
        debtor_inn = combo.debtor_inn
        address, region = combo.address or (None, None)
        arbit_manager = combo.arbit_manager
        arbit_manager_inn = combo.arbit_manager_inn
        arbit_manager_org = combo.arbit_manager_org
        start_date_requests = combo.start_date_requests
        end_date_requests = combo.end_date_requests
        files = combo.download_general(self.data_origin)
        for lot_link, lot_number, status in combo.get_lots():
            loader = CrawlerBankruptItemLoader(CrawlerBankruptItem(), response=response)
            loader.add_value('data_origin', self.data_origin)
            loader.add_value('trading_id', trading_id)
            loader.add_value('trading_link', trading_link)
            loader.add_value('trading_number', trading_number)
            loader.add_value('trading_type', trading_type)
            loader.add_value('trading_form', trading_form)
            loader.add_value('trading_org', trading_org)
            loader.add_value('trading_org_inn', trading_org_inn)
            loader.add_value('trading_org_contacts', trading_org_contacts)
            loader.add_value('msg_number', msg_number)
            loader.add_value('case_number', case_number)
            loader.add_value('debtor_inn', debtor_inn)
            loader.add_value('address', address)
            loader.add_value('region', region)
            loader.add_value('arbit_manager', arbit_manager)
            loader.add_value('arbit_manager_inn', arbit_manager_inn)
            loader.add_value('arbit_manager_org', arbit_manager_org)
            loader.add_value('lot_link', lot_link)
            loader.add_value('lot_number', lot_number)
            loader.add_value('status', status)
            loader.add_value('start_date_requests', start_date_requests)
            loader.add_value('end_date_requests', end_date_requests)
            yield Request(lot_link, self.parse_lot, cb_kwargs={'loader': loader, 'general_files': files})

    def parse_lot(self, response, loader, general_files):
        combo = Combo(response)
        loader.add_value('lot_id', combo.id_)
        loader.add_value('short_name', combo.short_name)
        loader.add_value('lot_info', combo.lot_info)
        loader.add_value('property_information', combo.property_information)
        loader.add_value('start_price', combo.start_price)
        loader.add_value('step_price', combo.step_price)
        if loader.get_collected_values('trading_type')[0] in ['auction', 'competition']:
            loader.add_value('start_date_trading', combo.auc.start_date_trading)
            loader.add_value('end_date_trading', combo.auc.end_date_trading)
            loader.add_value('periods', None)
        else:
            loader.add_value('periods', combo.offer.periods)
            loader.add_value('start_date_trading', combo.offer.start_date_trading)
            loader.add_value('end_date_trading', combo.offer.end_date_trading)
        lot_files = combo.download_lot(loader.get_collected_values('lot_number')[0], self.data_origin)
        loader.add_value('files', {'general': general_files, 'lot': lot_files})
        loader.add_value('created_at', return_parse_date())
        yield loader.load_item()
