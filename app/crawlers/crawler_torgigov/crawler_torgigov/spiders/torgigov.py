import json
from typing import Iterable

from scrapy import Request, FormRequest

from app.crawlers.base import BaseSpider
from app.crawlers.items import EtpItemLoader, EtpItem
from app.db.models import AuctionPropertyType
from app.utils.logger import logger
from ..combo import Combo
from ..config import formdata, data_origin, search_link, trade_link


class TorgiGovSpider(BaseSpider):
    name = "torgigov"
    property_type = AuctionPropertyType.gis

    def __init__(self):
        super().__init__(data_origin)

    def start_requests(self) -> Iterable[Request]:
        yield FormRequest(
            search_link,
            self.parse_serp,
            formdata=formdata,
            method="GET",
        )

    def parse_serp(self, response):
        data = json.loads(response.text)
        for trade in data["content"]:
            if (
                f"https://torgi.gov.ru/new/public/notices/view/{trade['id']}"
                not in self.previous_trades
            ):
                yield Request(f"{trade_link}/{trade['id']}", self.parse_trade)
        parsed_elements = (int(data["number"]) + 1) * int(data["size"])
        if parsed_elements < int(data["totalElements"]):
            logger.info(
                f"Parsed elements: {parsed_elements}/{data['totalElements']}"
            )
            formdata["page"] = str(int(formdata["page"]) + 1)
            yield FormRequest(
                search_link,
                self.parse_serp,
                formdata=formdata,
                method="GET",
            )

    def parse_trade(self, response):
        data = json.loads(response.text)
        combo = Combo(data)
        loader = EtpItemLoader(EtpItem(), response=response)
        loader.add_value("data_origin", data_origin)
        loader.add_value("property_type", self.property_type.value)
        loader.add_value("trading_id", combo.trading_id)
        loader.add_value("trading_link", combo.trading_link)
        loader.add_value("trading_number", combo.trading_number)
        loader.add_value("trading_type", combo.trading_type)
        loader.add_value("trading_form", combo.trading_form)
        loader.add_value("trading_org", combo.trading_org)
        loader.add_value("trading_org_contacts", combo.trading_org_contacts)
        loader.add_value("status", combo.status)
        loader.add_value("start_date_requests", combo.start_date_requests)
        loader.add_value("end_date_requests", combo.end_date_requests)
        loader.add_value("start_date_trading", combo.start_date_trading)
        loader.add_value("end_date_trading", combo.end_date_trading)
        general_files = combo.download_general()
        for lot in combo.get_lots():
            loader.add_value("address", combo.get_address(lot))
            loader.add_value('lot_id', combo.get_lot_id(lot))
            loader.add_value('lot_link', combo.get_lot_link(lot))
            loader.add_value("lot_number", combo.get_lot_number(lot))
            loader.add_value("categories", combo.get_category(lot))
            loader.add_value("short_name", combo.get_short_name(lot))
            loader.add_value("lot_info", combo.get_lot_info(lot))
            loader.add_value("start_price", combo.get_start_price(lot))
            loader.add_value("step_price", combo.get_step_price(lot))
            loader.add_value(
                "files", {"general": general_files, "lot": combo.download_lot(lot)}
            )
            yield loader.load_item()
