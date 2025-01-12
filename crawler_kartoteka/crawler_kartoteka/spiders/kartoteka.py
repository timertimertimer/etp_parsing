import json
from typing import Iterable

from bs4 import BeautifulSoup
import scrapy
from scrapy import Request, FormRequest

from ..items import CrawlerKartotekaItem, CrawlerKartotekaItemLoader
from ..utils.work_with_text_and_number import dedent_func
from ..utils.working_with_time import return_parse_date

from ..locators.serp_locator import SerpLocator
from ..trades.app import Combo
from ..utils.config import format_parse_date, time_delta, trash_resources, data_origin_url
from ..utils.get_data_from_table import DbConnectCheckLots
from ..utils.post_data import form_data
from ..utils.working_with_url import UrlConfig


class KartotekaSpider(scrapy.Spider):
    name = "kartoteka"
    start_urls = ["https://www.kartoteka.ru/bankruptcy2/"]
    custom_settings = {"PLAYWRIGHT_ABORT_REQUEST": lambda request: request.resource_type in trash_resources}

    def __init__(self):
        super(KartotekaSpider, self).__init__()
        self.db_check = DbConnectCheckLots()
        self.previous_lots = self.db_check.get_latest_lot()
        self.url = UrlConfig()
        self.loc = SerpLocator

    def start_requests(self):
        for url in self.start_urls:
            yield Request(
                url,
                callback=self.get_validate_data,
                meta=dict(
                    playwright=True,
                ),
            )

    def get_validate_data(self, response) -> Iterable[Request]:
        validate_data = response.xpath('//input[@name="validate"]/@value').get()
        data_trade_begin = format_parse_date(time_delta)
        form_data["data-trade-begin"] = data_trade_begin
        form_data["validate"] = validate_data
        yield FormRequest(
            f"{self.start_urls[0]}/?action=Hash",
            self.get_hash,
            method="POST",
            formdata=form_data,
            headers={"Content-Type": "application/x-www-form-urlencoded; charset=UTF-8"},
        )

    def get_hash(self, response):
        hash = json.loads(response.text)["hash"]
        yield Request(f"{self.start_urls[0]}{hash}", self.parse_serp)

    def parse_serp(self, response):
        trade_cards = response.xpath(self.loc.trade_card_loc)
        for trade in trade_cards:
            link = self.url.url_join(data_origin_url, trade.xpath(self.loc.link_to_trade_loc).get())
            if link not in self.previous_lots:
                status = trade.xpath(self.loc.status_loc).get()
                short_name = dedent_func(trade.xpath(self.loc.short_name_loc).get())
                yield Request(link, self.parse_trade, cb_kwargs={"status": status, "short_name": short_name})
        pagination = response.xpath(self.loc.pagination_loc).get()
        if pagination:
            next_page = response.xpath(self.loc.next_page_loc).get()
            if next_page:
                form_data["page"] = next_page
                yield FormRequest(
                    f"{self.start_urls[0]}/?action=Hash",
                    self.get_hash,
                    method="POST",
                    formdata=form_data,
                    headers={"Content-Type": "application/x-www-form-urlencoded; charset=UTF-8"},
                )

    def parse_trade(self, response, status, short_name):
        combo = Combo(response)
        trading_type, trading_form = combo.trading_type_and_form
        trading_id = trading_number = combo.trading_id
        status = combo.parse_status(status)
        loader = CrawlerKartotekaItemLoader(CrawlerKartotekaItem(), response=response)
        loader.add_value("data_origin", data_origin_url)
        loader.add_value("trading_id", trading_id)
        loader.add_value("trading_link", response.url)
        loader.add_value("trading_number", trading_number)
        loader.add_value("trading_type", trading_type)
        loader.add_value("trading_form", trading_form)
        loader.add_value("trading_org", combo.trading_org)
        loader.add_value("trading_org_inn", combo.trading_org_inn)
        loader.add_value("trading_org_contacts", combo.trading_org_contacts)
        loader.add_value("msg_number", combo.msg_number)
        loader.add_value("case_number", combo.case_number)
        loader.add_value("debtor_inn", combo.debitor_inn)
        loader.add_value('address', combo.address)
        loader.add_value("arbit_manager", combo.arbit_manager)
        loader.add_value("arbit_manager_inn", combo.arbit_manager_inn)
        loader.add_value("arbit_manager_org", combo.arbit_manager_org)
        loader.add_value("status", status)
        loader.add_value("lot_id", combo.lot_id)
        loader.add_value("lot_link", combo.lot_link)
        loader.add_value("lot_number", combo.lot_number)
        loader.add_value("short_name", short_name)
        loader.add_value("lot_info", combo.lot_info)
        loader.add_value("property_information", combo.property_information)
        loader.add_value("start_date_requests", combo.start_date_requests)
        loader.add_value("end_date_requests", combo.end_date_requests)
        loader.add_value("start_date_trading", combo.start_date_trading)
        loader.add_value("end_date_trading", combo.end_date_trading)
        loader.add_value("start_price", combo.start_price)
        loader.add_value("step_price", combo.step_price)
        loader.add_value("periods", combo.periods)
        loader.add_value("files", {"general": combo.download_general(), "lot": combo.download_lot()})
        loader.add_value("created_at", return_parse_date())
        yield loader.load_item()
