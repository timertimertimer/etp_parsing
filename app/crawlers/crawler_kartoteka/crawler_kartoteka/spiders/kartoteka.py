import json
from typing import Iterable

from scrapy import Request, FormRequest

from app.db.models import AuctionPropertyType
from app.utils import dedent_func, URL
from app.crawlers.items import EtpItem, EtpItemLoader
from app.crawlers.base import BaseSpider
from app.utils.config import trash_resources, start_date, write_log_to_file
from ..locators.serp_locator import SerpLocator
from ..combo import Combo
from ..config import data_origin_url, form_data


class KartotekaSpider(BaseSpider):
    name = "kartoteka"
    start_urls = ["https://www.kartoteka.ru/bankruptcy2/"]
    custom_settings = {
        "LOG_FILE": f"{name}.log" if write_log_to_file else None,
        "PLAYWRIGHT_ABORT_REQUEST": lambda request: request.resource_type
        in trash_resources,
        "PLAYWRIGHT_LAUNCH_OPTIONS": {"timeout": 60 * 1000},
    }
    property_type = AuctionPropertyType.bankruptcy

    def __init__(self):
        super().__init__(data_origin_url)

    def start_requests(self):
        for url in self.start_urls:
            yield Request(
                url, callback=self.get_validate_data, meta=dict(playwright=True)
            )

    def get_validate_data(self, response) -> Iterable[Request]:
        validate_data = response.xpath('//input[@name="validate"]/@value').get()
        form_data["data-trade-begin"] = start_date
        form_data["validate"] = validate_data
        yield FormRequest(
            f"{self.start_urls[0]}/?action=Hash",
            self.get_hash,
            method="POST",
            formdata=form_data,
            headers={
                "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8"
            },
        )

    def get_hash(self, response):
        hash = json.loads(response.text)["hash"]
        yield Request(f"{self.start_urls[0]}{hash}", self.parse_serp)

    def parse_serp(self, response):
        trade_cards = response.xpath(SerpLocator.trade_card_loc)
        for trade in trade_cards:
            link = URL.url_join(
                data_origin_url, trade.xpath(SerpLocator.link_to_trade_loc).get()
            )
            if link not in self.previous_trades:
                status = trade.xpath(SerpLocator.status_loc).get()
                short_name = dedent_func(trade.xpath(SerpLocator.short_name_loc).get())
                yield Request(
                    link,
                    self.parse_trade,
                    cb_kwargs={"status": status, "short_name": short_name},
                )
        pagination = response.xpath(SerpLocator.pagination_loc).get()
        if pagination:
            next_page = response.xpath(SerpLocator.next_page_loc).get()
            if next_page:
                form_data["page"] = next_page
                yield FormRequest(
                    f"{self.start_urls[0]}/?action=Hash",
                    self.get_hash,
                    method="POST",
                    formdata=form_data,
                    headers={
                        "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8"
                    },
                )

    def parse_trade(self, response, status, short_name):
        combo = Combo(response)
        trading_type, trading_form = combo.trading_type_and_form
        trading_id = trading_number = combo.trading_id
        status = combo.parse_status(status)
        loader = EtpItemLoader(EtpItem(), response=response)
        loader.add_value("data_origin", data_origin_url)
        loader.add_value("property_type", self.property_type.value)
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
        loader.add_value("address", combo.address)
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
        loader.add_value("categories", None)
        loader.add_value(
            "files", {"general": combo.download_general(), "lot": combo.download_lot()}
        )
        yield loader.load_item()
