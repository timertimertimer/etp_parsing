import json
import re
from bs4 import BeautifulSoup
from scrapy import FormRequest, Request

from app.db.models import AuctionPropertyType
from app.utils.config import write_log_to_file
from ..combo import Combo
from ..config import data_origin_url, bankrupt_form_data, sales_form_data, urls
from app.utils import URL
from app.crawlers.items import EtpItem, EtpItemLoader
from app.crawlers.base import BaseSpider


class TorgidvBaseSpider(BaseSpider):
    def __init__(self):
        super(TorgidvBaseSpider, self).__init__(data_origin_url)
        self.trades = set()
        self.pending_requests = 0

    def parse(self, response, **kwargs):
        match = re.search(r'"bitrix_sessid":"([a-f0-9]{32})"', response.text)
        sessid = match.group(1)
        url_params = {
            "mode": "class",
            "c": "wl.trade:lots.list",
            "action": "list",
            "sessid": sessid,
        }
        base_url = "https://torgidv.ru/bitrix/services/main/ajax.php?"
        url = base_url + "&".join(f"{key}={value}" for key, value in url_params.items())
        yield FormRequest(url, self.parse_serp, method="POST", formdata=self.form_data)

    def parse_serp(self, response):
        data = json.loads(response.text)
        for link in [el[0] for el in data["data"]]:
            link = BeautifulSoup(link, "lxml").a["href"]
            self.pending_requests += 1
            yield Request(
                URL.url_join(urls[self.property_type], link), self.get_trade_links
            )

        if self.pending_requests == 0:
            yield from self.process_trades()

    def get_trade_links(self, response):
        combo = Combo(response)
        self.trades.add(combo.get_trading_link(self.property_type))
        self.pending_requests -= 1

        if self.pending_requests == 0:
            yield from self.process_trades()

    def process_trades(self):
        for link in self.trades:
            if link not in self.previous_trades:
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
        address = combo.address
        msg_number = combo.msg_number
        case_number = combo.case_number
        start_date_requests = combo.start_date_requests
        end_date_requests = combo.end_date_requests
        start_date_trading = combo.start_date_trading
        end_date_trading = combo.end_date_trading
        files = combo.download()
        for lot in combo.get_lots():
            loader = EtpItemLoader(EtpItem(), response=response)
            loader.add_value("data_origin", data_origin_url)
            loader.add_value("property_type", self.property_type)
            loader.add_value("trading_id", trading_id)
            loader.add_value("trading_link", trading_link)
            loader.add_value("trading_number", trading_number)
            loader.add_value("trading_type", trading_type)
            loader.add_value("trading_form", trading_form)
            loader.add_value("trading_org", trading_org)
            loader.add_value("trading_org_inn", trading_org_inn)
            loader.add_value("trading_org_contacts", trading_org_contacts)
            loader.add_value("address", address)
            loader.add_value("msg_number", msg_number)
            loader.add_value("case_number", case_number)
            loader.add_value("start_date_requests", start_date_requests)
            loader.add_value("end_date_requests", end_date_requests)
            loader.add_value("start_date_trading", start_date_trading)
            loader.add_value("end_date_trading", end_date_trading)
            yield Request(
                URL.url_join(urls[self.property_type], lot),
                self.parse_lot,
                cb_kwargs={"loader": loader, "general_files": files},
            )

    def parse_lot(self, response, loader, general_files):
        combo = Combo(response)
        loader.add_value("debtor_inn", combo.debtor_inn)
        loader.add_value("arbit_manager", combo.arbit_manager)
        loader.add_value("arbit_manager_inn", combo.arbit_manager_inn)
        loader.add_value("arbit_manager_org", combo.arbit_manager_org)
        loader.add_value("status", combo.status)
        loader.add_value("lot_id", combo.id_)
        loader.add_value("lot_link", response.url)
        loader.add_value("lot_number", combo.lot_number)
        loader.add_value("short_name", combo.short_name)
        loader.add_value("lot_info", combo.lot_info)
        loader.add_value("property_information", combo.property_information)
        loader.add_value("start_price", combo.start_price)
        loader.add_value("step_price", combo.step_price)
        loader.add_value("periods", combo.periods)
        loader.add_value("categories", combo.categories)
        loader.add_value("files", {"general": general_files, "lot": combo.download()})
        yield loader.load_item()


class TorgidvBankruptSpider(TorgidvBaseSpider):
    name = "torgidv_bankruptcy"
    property_type = AuctionPropertyType.bankruptcy
    start_urls = [urls[property_type]]
    form_data = bankrupt_form_data
    custom_settings = {
        "LOG_FILE": f"{name}.log" if write_log_to_file else None,
    }


class TorgidvArrestedSpider(TorgidvBaseSpider):
    name = "torgidv_arrested"
    property_type = AuctionPropertyType.arrested
    start_urls = [urls[property_type]]
    form_data = sales_form_data
    custom_settings = {
        "LOG_FILE": f"{name}.log" if write_log_to_file else None,
    }
