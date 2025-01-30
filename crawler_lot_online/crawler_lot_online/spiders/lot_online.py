from datetime import datetime
import scrapy
import json

from scrapy import FormRequest, Request

from general_utils.items import CrawlerNonBankruptItem, CrawlerNonBankruptItemLoader
from general_utils.location import Region
from ..app import Combo
from ..utils.config import data_origin
from ..utils.get_data_from_table import DbConnectCheckLots
from ..utils.post_data import form_data
from ..utils.work_with_text_and_number import dedent_func
from ..utils.working_with_time import return_parse_date


class LotOnlineSpider(scrapy.Spider):
    name = "lot_online"
    start_urls = ["https://{}.lot-online.ru/lot/categories-grid-json.html"]

    def __init__(self, domain):
        super(LotOnlineSpider, self).__init__()
        self.domain = domain
        self.db_check = DbConnectCheckLots(domain)
        self.previous_lots = self.db_check.get_latest_lot()
        form_data['saleTypeId'] = {
            'rad': '3001',
            'confiscate': '6001',
            'lease': '7001',
            'privatization': '4001',
            'arrested': '8001'
        }[domain]

    def start_requests(self):
        form_data['nd'] = str(int(datetime.now().timestamp() * 1000))
        yield FormRequest(
            self.start_urls[0].format(self.domain), self.parse_serp, formdata=form_data, method='POST',
            headers={'Content-Type': 'application/x-www-form-urlencoded'}
        )

    def parse_serp(self, response, current_page=1):
        data = json.loads(response.text)
        for trade in data['rows']:
            trading_id = trade["id"]
            if str(trading_id) not in self.previous_lots:
                yield FormRequest(
                    f'https://{self.domain}.lot-online.ru/tender/{trading_id}/lots.html', self.parse_trade, formdata={
                        '_search': 'false',
                        'nd': str(int(datetime.now().timestamp() * 1000)),
                        'rows': '100',
                        'page': '1',
                        'sidx': '',
                        'sord': 'asc'
                    },
                    method='POST',
                    headers={'Content-Type': 'application/x-www-form-urlencoded'},
                    cb_kwargs={'trading_id': trading_id, 'trading_number': trade['tender']['tenderCode']}
                )
        if int(data['total']) > int(form_data['rows']) * current_page:
            current_page += 1
            form_data['nd'] = str(int(datetime.now().timestamp() * 1000))
            form_data['page'] = str(current_page)
            yield FormRequest(
                self.start_urls[0].format(self.domain), self.parse_serp, formdata=form_data, method='POST',
                headers={'Content-Type': 'application/x-www-form-urlencoded'}
            )

    def parse_trade(self, response, trading_id, trading_number, current_page=1):
        data = json.loads(response.text)
        for lot in data['rows']:
            loader = CrawlerNonBankruptItemLoader(CrawlerNonBankruptItem(), response=response)
            loader.add_value('data_origin', data_origin[self.domain])
            loader.add_value('trading_id', trading_id)
            loader.add_value('trading_link',
                             f'https://{self.domain}.lot-online.ru/tender/details.html?tenderId={trading_id}')
            loader.add_value('trading_number', trading_number)
            loader.add_value('lot_number', lot['lotInfo']['lotCode'].split('-')[-1])
            loader.add_value('short_name', dedent_func(lot['lotInfo']['name']))
            yield Request(
                f'https://{self.domain}.lot-online.ru/lot/details.html?lotId={lot["lotInfo"]["id"]}', self.parse_lot,
                cb_kwargs={'loader': loader}
            )
        if int(data['records']) > int(form_data['rows']) * current_page:
            current_page += 1
            form_data['nd'] = str(int(datetime.now().timestamp() * 1000))
            form_data['page'] = str(current_page)
            yield FormRequest.from_response(
                response, callback=self.parse_trade, formdata=form_data, method='POST',
                headers={'Content-Type': 'application/x-www-form-urlencoded'}
            )

    def parse_lot(self, response, loader):
        combo = Combo(response, self.domain)
        loader.add_value('trading_type', combo.trading_type)
        loader.add_value('trading_org', combo.trading_org)
        loader.add_value('status', combo.status)
        loader.add_value('category', combo.category)
        loader.add_value('start_price', combo.start_price)
        loader.add_value('step_price', combo.step_price)
        loader.add_value('min_price', combo.min_price)
        loader.add_value('deposit', combo.deposit)
        loader.add_value('periods', combo.periods)
        loader.add_value('lot_info', combo.lot_info)
        address = combo.address
        region = None
        if address:
            region = Region.get_region(address)
        loader.add_value('address', address)
        loader.add_value('region', region)
        loader.add_value('start_date_requests', combo.start_date_requests)
        loader.add_value('end_date_requests', combo.end_date_requests)
        loader.add_value('start_date_trading', combo.start_date_trading)
        loader.add_value('end_date_trading', combo.end_date_trading)
        loader.add_value('files', {"general": combo.download_general(), "lot": combo.download_lot(
            str(loader.get_collected_values('trading_id')[0]), str(loader.get_collected_values('lot_number')[0]),
            data_origin[self.domain], self.domain
        )})
        loader.add_value('created_at', return_parse_date())
        yield loader.load_item()
