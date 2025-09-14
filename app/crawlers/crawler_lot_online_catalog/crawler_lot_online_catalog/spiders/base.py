import json
from typing import Iterable
from datetime import datetime
from scrapy import Request, FormRequest

from app.crawlers.base import BaseSpider
from app.db.models import AuctionPropertyType
from app.utils.config import write_log_to_file
from app.crawlers.items import EtpItem, EtpItemLoader
from ..combo import Combo
from ..config import form_data, hashes, data_origin, start_datetime


class LotOnlineCatalogBaseSpider(BaseSpider):
    name = "base"
    start_urls = ["https://catalog.lot-online.ru/index.php"]
    custom_settings = {
        "LOG_FILE": f"{name}.log" if write_log_to_file else None,
    }

    def __init__(self):
        super(LotOnlineCatalogBaseSpider, self).__init__(data_origin)

    def start_requests(self) -> Iterable[Request]:
        start_timestamp = int(start_datetime.timestamp())
        end_timestamp = int(datetime.now().timestamp()) - 1
        form_data["features_hash"] = (
            f"112-{start_timestamp}-{end_timestamp}_{hashes[self.name]}"
        )
        yield FormRequest(
            self.start_urls[0], self.parse_serp, formdata=form_data, method="POST"
        )

    def parse_serp(self, response):
        html = json.loads(response.text)["html"]["pagination_contents"]
        combo = Combo(response)
        for lot in combo.get_lots(html):
            if lot[0] not in self.previous_trades:
                yield Request(lot[0], self.parse_lot, cb_kwargs={"lot": lot})

        if combo.next_page(html):
            form_data["page"] = str(int(form_data["page"]) + 1)
            yield FormRequest(
                self.start_urls[0], self.parse_serp, formdata=form_data, method="POST"
            )

    def parse_lot(self, response, lot):
        combo = Combo(response)
        loader = EtpItemLoader(EtpItem(), response=response)
        loader.add_value("data_origin", data_origin)
        loader.add_value("property_type", self.property_type.value)
        loader.add_value("trading_id", combo.trading_id)
        loader.add_value("trading_link", combo.trading_link)
        loader.add_value("trading_number", lot[1])
        loader.add_value("trading_type", combo.trading_type)
        loader.add_value("trading_form", combo.trading_form)
        loader.add_value("trading_org", combo.trading_org)
        loader.add_value("trading_org_contacts", combo.trading_org_contacts)
        loader.add_value("msg_number", combo.msg_number)
        loader.add_value("case_number", combo.case_number)
        loader.add_value("debtor_inn", combo.debtor_inn)
        loader.add_value("address", combo.address or combo.sud)
        loader.add_value("arbit_manager", combo.arbit_manager)
        loader.add_value("arbit_manager_inn", combo.arbit_manager_inn)
        loader.add_value("arbit_manager_org", combo.arbit_manager_org)
        loader.add_value("status", lot[3])
        loader.add_value("lot_id", combo.lot_id)
        loader.add_value("lot_link", combo.lot_link)
        loader.add_value("lot_number", combo.get_lot_number(lot[2]))
        loader.add_value("short_name", lot[2])
        loader.add_value("lot_info", combo.lot_info)
        loader.add_value("property_information", combo.property_information)
        loader.add_value(
            "files", {"general": combo.download_general(), "lot": combo.download_lot()}
        )
        loader.add_value("start_price", combo.start_price)
        if combo.trading_type == "offer" and combo.periods:
            loader.add_value("periods", combo.periods)
            loader.add_value(
                "start_date_requests", combo.periods[0]["start_date_requests"]
            )
            loader.add_value(
                "end_date_requests", combo.periods[-1]["end_date_requests"]
            )
            loader.add_value(
                "start_date_trading", combo.periods[0]["start_date_requests"]
            )
            loader.add_value("end_date_trading", combo.periods[-1]["end_date_trading"])
            yield loader.load_item()
        else:
            yield Request(
                combo.get_auc_dates_link(),
                self.get_auction_info,
                cb_kwargs={"loader": loader},
            )

    def get_auction_info(self, response, loader):
        combo = Combo(response)
        loader.add_value("start_price", combo.start_price)
        loader.add_value("start_date_requests", combo.start_date_requests_auc)
        loader.add_value("end_date_requests", combo.end_date_requests_auc)
        loader.add_value("step_price", combo.step_price)
        yield loader.load_item()


class LotOnlineBankruptcySpider(LotOnlineCatalogBaseSpider):
    name = "lot_online_bankruptcy"
    property_type = AuctionPropertyType.bankruptcy
    custom_settings = {
        "LOG_FILE": f"{name}.log" if write_log_to_file else None,
    }


class LotOnlinePrivatePropertySpider(LotOnlineCatalogBaseSpider):
    name = "lot_online_private_property"
    property_type = AuctionPropertyType.commercial
    custom_settings = {
        "LOG_FILE": f"{name}.log" if write_log_to_file else None,
    }


class LotOnlineRentSpider(LotOnlineCatalogBaseSpider):
    name = "lot_online_rent"
    property_type = AuctionPropertyType.rent
    custom_settings = {
        "LOG_FILE": f"{name}.log" if write_log_to_file else None,
    }
