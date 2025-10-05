import json
from urllib.parse import quote_plus

from scrapy import Request

from app.crawlers.base import BaseSpider
from app.crawlers.crawler_ei.crawler_ei.combo import Combo
from app.crawlers.crawler_ei.crawler_ei.config import data_origin, params, types
from app.crawlers.items import EtpItem, EtpItemLoader
from app.db.models import AuctionPropertyType
from app.utils.config import write_log_to_file


def build_query(params_dict):
    parts = []
    for key, value in params_dict.items():
        if isinstance(value, list):
            for v in value:
                parts.append(f"{key}={quote_plus(str(v))}")
        else:
            parts.append(f"{key}={quote_plus(str(value))}")
    return "&".join(parts)


class EiBaseSpider(BaseSpider):
    name = "base"
    start_urls = ["https://api.ei.ru/v1/lot/index"]

    def __init__(self):
        super().__init__(data_origin)

    def start_requests(self):
        params["filter[type][]"] = types[self.property_type.value]
        for i in range(1, 51):
            params["page"] = i
            query_string = build_query(params)
            url = f"{self.start_urls[0]}?{query_string}"
            yield Request(
                url=url,
                method="GET",
                headers={"Accept": "application/json, text/plain, */*"},
                callback=self.parse_serp,
            )

    def parse_serp(self, response):
        data = json.loads(response.text)
        for lot in data:
            expand = [
                "bankrupt",
                "place",
                "manager",
                "owner",
                "casefile",
                "etp",
                "categories",
                "images",
                "prices",
                "torg",
                "messages",
                "documents",
                "rules",
                "torgDecsription",
                "cadastrs",
                "edit_url",
                "updated",
                "vins",
                "categories",
                "torgAdditionalText",
                "seo",
                "minPrice",
                "priceReduction",
                "ownerLotInfo",
            ]
            yield Request(
                url=f"https://api.ei.ru/v1/lot/view?id={lot['id']}&expand={','.join(expand)}",
                callback=self.parse_lot,
            )

    def parse_lot(self, response):
        loader = EtpItemLoader(EtpItem(), response=response)
        data = json.loads(response.text)
        combo = Combo(data)
        loader.add_value("data_origin", data_origin)
        loader.add_value("property_type", self.property_type.value)
        loader.add_value("trading_id", combo.trading_id)
        loader.add_value("trading_link", combo.trading_link)
        loader.add_value("trading_number", combo.trading_number)
        loader.add_value("trading_type", combo.trading_type)
        loader.add_value("trading_form", combo.trading_form)
        loader.add_value("trading_org", combo.trading_org)
        loader.add_value("trading_org_inn", combo.trading_org_inn)
        loader.add_value("trading_org_contacts", combo.trading_org_contacts)
        loader.add_value("msg_number", combo.msg_number)
        loader.add_value("case_number", combo.case_number)
        loader.add_value("debtor_inn", combo.debtor_inn)
        loader.add_value("address", combo.address)
        loader.add_value("arbit_manager", combo.arbit_manager)
        loader.add_value("arbit_manager_inn", combo.arbit_manager_inn)
        loader.add_value("arbit_manager_org", combo.arbit_manager_org)
        loader.add_value("status", combo.status)
        loader.add_value("lot_id", combo.lot_id)
        loader.add_value("lot_link", combo.lot_link)
        loader.add_value("lot_number", combo.lot_number)
        loader.add_value("short_name", combo.short_name)
        loader.add_value("lot_info", combo.lot_info)
        loader.add_value("categories", combo.categories)
        loader.add_value("property_information", combo.property_information)
        loader.add_value("start_date_requests", combo.start_date_requests)
        loader.add_value("end_date_requests", combo.end_date_requests)
        loader.add_value("start_date_trading", combo.start_date_trading)
        loader.add_value("end_date_trading", combo.end_date_trading)
        loader.add_value("start_price", combo.start_price)
        if combo.trading_type in ["auction", "competition"]:
            loader.add_value("step_price", combo.step_price)
        loader.add_value("periods", combo.periods)
        loader.add_value(
            "files",
            {"general": combo.download_general(), "lot": combo.download_lot()},
        )
        yield loader.load_item()


class EiBankruptcySpider(EiBaseSpider):
    name = "ei_bankruptcy"
    property_type = AuctionPropertyType.bankruptcy
    custom_settings = {
        "LOG_FILE": f"{name}.log" if write_log_to_file else None,
    }


class EiArrestedSpider(EiBaseSpider):
    name = "ei_arrested"
    property_type = AuctionPropertyType.arrested
    custom_settings = {
        "LOG_FILE": f"{name}.log" if write_log_to_file else None,
    }


class EiCommercialSpider(EiBaseSpider):
    name = "ei_commercial"
    property_type = AuctionPropertyType.commercial
    custom_settings = {
        "LOG_FILE": f"{name}.log" if write_log_to_file else None,
    }
