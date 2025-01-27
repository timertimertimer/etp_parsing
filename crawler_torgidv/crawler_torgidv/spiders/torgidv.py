import json
import re
import scrapy
from bs4 import BeautifulSoup
from scrapy import FormRequest, Request

from general_utils import UrlConfig, CrawlerBankruptItem, CrawlerBankruptItemLoader, return_parse_date
from ..trades.app import Combo
from ..utils.config import main_url, data_origin_url
from ..utils.data_for_requests import form_data
from ..utils.get_data_from_table import DbConnectCheckLots


class TorgidvSpider(scrapy.Spider):
    name = "torgidv"
    start_urls = ["https://torgidv.ru/bankrupt/"]

    def __init__(self):
        super(TorgidvSpider).__init__()
        self.db_check = DbConnectCheckLots()
        self.previous_lots = self.db_check.get_latest_lot()
        self.trades = set()
        self.pending_requests = 0

    def parse(self, response):
        match = re.search(r'"bitrix_sessid":"([a-f0-9]{32})"', response.text)
        sessid = match.group(1)
        url_params = {
            "mode": "class",
            "c": "wl.trade:lots.list",
            "action": "list",
            "sessid": sessid
        }
        base_url = 'https://torgidv.ru/bitrix/services/main/ajax.php?'
        url = base_url + "&".join(f"{key}={value}" for key, value in url_params.items())
        yield FormRequest(url, self.parse_serp, method='POST', formdata=form_data)

    def parse_serp(self, response):
        data = json.loads(response.text)
        # if len(data['recordsTotal']) > len(data['data']):
        #     form_data['length']
        for link in [el[0] for el in data['data']]:
            link = BeautifulSoup(link, 'lxml').a['href']
            self.pending_requests += 1
            yield Request(UrlConfig.url_join(main_url, link), self.get_trade_links)

        if self.pending_requests == 0:
            yield from self.process_trades()

    def get_trade_links(self, response):
        combo = Combo(response)
        self.trades.add(combo.get_trading_link())
        self.pending_requests -= 1

        if self.pending_requests == 0:
            yield from self.process_trades()

    def process_trades(self):
        for link in self.trades:
            if link not in self.previous_lots:
                yield Request(link, self.parse_trade)

    def parse_trade(self, response):
        combo = Combo(response)
        trading_id = trading_number = combo.id_
        trading_link = response.url
        trading_type = combo.trading_type
        trading_form = combo.trading_form
        trading_org = combo.trading_org
        trading_org_inn = combo.trading_org_inn
        trading_org_contacts = combo.trading_org_contacts
        address, region = combo.get_address() or (None, None)
        msg_number = combo.msg_number
        case_number = combo.case_number
        start_date_requests = combo.start_date_requests
        end_date_requests = combo.end_date_requests
        start_date_trading = combo.start_date_trading
        end_date_trading = combo.end_date_trading
        files = combo.download_general()
        for lot in combo.get_lots():
            loader = CrawlerBankruptItemLoader(CrawlerBankruptItem(), response=response)
            loader.add_value('data_origin', data_origin_url)
            loader.add_value('trading_id', trading_id)
            loader.add_value('trading_link', trading_link)
            loader.add_value('trading_number', trading_number)
            loader.add_value('trading_type', trading_type)
            loader.add_value('trading_form', trading_form)
            loader.add_value('trading_org', trading_org)
            loader.add_value('trading_org_inn', trading_org_inn)
            loader.add_value('trading_org_contacts', trading_org_contacts)
            loader.add_value('address', address)
            loader.add_value('region', region)
            loader.add_value('msg_number', msg_number)
            loader.add_value('case_number', case_number)
            loader.add_value('start_date_requests', start_date_requests)
            loader.add_value('end_date_requests', end_date_requests)
            loader.add_value('start_date_trading', start_date_trading)
            loader.add_value('end_date_trading', end_date_trading)
            yield Request(UrlConfig.url_join(main_url, lot), self.parse_lot,
                          cb_kwargs={'loader': loader, 'general_files': files})

    def parse_lot(self, response, loader, general_files):
        combo = Combo(response)
        loader.add_value('debtor_inn', combo.debtor_inn)
        loader.add_value('arbit_manager', combo.arbit_manager)
        loader.add_value('arbit_manager_inn', combo.arbit_manager_inn)
        loader.add_value('arbit_manager_org', combo.arbit_manager_org)
        loader.add_value('status', combo.status)
        loader.add_value('lot_id', combo.id_)
        loader.add_value('lot_link', response.url)
        loader.add_value('lot_number', combo.lot_number)
        loader.add_value('short_name', combo.short_name)
        loader.add_value('lot_info', combo.lot_info)
        loader.add_value('property_information', combo.property_information)
        loader.add_value('start_price', combo.start_price)
        loader.add_value('step_price', combo.step_price)
        loader.add_value('periods', combo.periods)
        loader.add_value('files', {'general': general_files, 'lot': combo.download_lot()})
        loader.add_value('created_at', return_parse_date())
        yield loader.load_item()
