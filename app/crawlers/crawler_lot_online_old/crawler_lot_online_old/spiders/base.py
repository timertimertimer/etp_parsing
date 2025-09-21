import json
from datetime import datetime

from scrapy import FormRequest, Request

from app.db.models import AuctionPropertyType
from app.utils import dedent_func
from app.crawlers.base import BaseSpider
from app.utils.config import write_log_to_file
from app.crawlers.items import EtpItemLoader, EtpItem
from ..combo import Combo
from ..config import form_data, main_data_origin, data_origin


class LotOnlineOldBaseSpider(BaseSpider):
    name = "base"
    start_urls = ["https://{}.lot-online.ru/lot/categories-grid-json.html"]
    custom_settings = {
        "LOG_FILE": f"{name}.log" if write_log_to_file else None,
    }

    def __init__(self):
        self.name_without_prefix = self.name.removeprefix('lot_online_old_')
        super(LotOnlineOldBaseSpider, self).__init__(main_data_origin)

    def start_requests(self):
        form_data["saleTypeId"] = {
            "rad": "3001",
            "confiscate": "6001",
            "lease": "7001",
            "privatization": "4001",
            "arrested": "8001",
        }[self.name_without_prefix]
        form_data["nd"] = str(int(datetime.now().timestamp() * 1000))
        yield FormRequest(
            self.start_urls[0].format(self.name_without_prefix),
            self.parse_serp,
            formdata=form_data,
            method="POST",
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )

    def parse_serp(self, response, current_page=1):
        data = json.loads(response.text)
        for trade in data["rows"]:
            trading_id = trade["id"]
            if (
                f"https://{self.name_without_prefix}.lot-online.ru/tender/details.html?tenderId={trading_id}"
                not in self.previous_trades
            ):
                yield FormRequest(
                    f"https://{self.name_without_prefix}.lot-online.ru/tender/{trading_id}/lots.html",
                    self.parse_trade,
                    formdata={
                        "_search": "false",
                        "nd": str(int(datetime.now().timestamp() * 1000)),
                        "rows": "100",
                        "page": "1",
                        "sidx": "",
                        "sord": "asc",
                    },
                    method="POST",
                    headers={"Content-Type": "application/x-www-form-urlencoded"},
                    cb_kwargs={
                        "trading_id": trading_id,
                        "trading_number": trade["tender"]["tenderCode"],
                    },
                )
        if int(data["total"]) > int(form_data["rows"]) * current_page:
            current_page += 1
            form_data["nd"] = str(int(datetime.now().timestamp() * 1000))
            form_data["page"] = str(current_page)
            yield FormRequest(
                self.start_urls[0].format(self.name_without_prefix),
                self.parse_serp,
                formdata=form_data,
                method="POST",
                headers={"Content-Type": "application/x-www-form-urlencoded"},
            )

    def parse_trade(self, response, trading_id, trading_number, current_page=1):
        data = json.loads(response.text)
        for lot in data["rows"]:
            loader = EtpItemLoader(EtpItem(), response=response)
            loader.add_value("data_origin", data_origin[self.name_without_prefix])
            if self.property_type:
                loader.add_value("property_type", self.property_type.value)
            loader.add_value("trading_id", trading_id)
            loader.add_value(
                "trading_link",
                f"https://{self.name_without_prefix}.lot-online.ru/tender/details.html?tenderId={trading_id}",
            )
            loader.add_value("trading_number", trading_number)
            loader.add_value("lot_number", lot["lotInfo"]["lotCode"].split("-")[-1])
            loader.add_value("short_name", dedent_func(lot["lotInfo"]["name"]))
            yield Request(
                f"https://{self.name_without_prefix}.lot-online.ru/lot/details.html?lotId={lot['lotInfo']['id']}",
                self.parse_lot,
                cb_kwargs={"loader": loader},
            )
        if int(data["records"]) > int(form_data["rows"]) * current_page:
            current_page += 1
            form_data["nd"] = str(int(datetime.now().timestamp() * 1000))
            form_data["page"] = str(current_page)
            yield FormRequest.from_response(
                response,
                callback=self.parse_trade,
                formdata=form_data,
                method="POST",
                headers={"Content-Type": "application/x-www-form-urlencoded"},
            )

    def parse_lot(self, response, loader):
        combo = Combo(response)
        loader.add_value("trading_type", combo.trading_type)
        loader.add_value("trading_form", "open")
        loader.add_value("trading_org", combo.trading_org)
        loader.add_value("status", combo.status)
        loader.add_value("categories", combo.category)
        loader.add_value("start_price", combo.start_price)
        loader.add_value("step_price", combo.step_price)
        loader.add_value("periods", combo.periods)
        loader.add_value("lot_info", combo.lot_info)
        loader.add_value("address", combo.address)
        loader.add_value("start_date_requests", combo.start_date_requests)
        loader.add_value("end_date_requests", combo.end_date_requests)
        loader.add_value("start_date_trading", combo.start_date_trading)
        loader.add_value("end_date_trading", combo.end_date_trading)
        loader.add_value(
            "files",
            {
                "general": combo.download_general(),
                "lot": combo.download_lot(data_origin[self.name_without_prefix]),
            },
        )
        yield loader.load_item()


class LotOnlineArrestedSpider(LotOnlineOldBaseSpider):
    name = "lot_online_old_arrested"
    property_type = AuctionPropertyType.arrested
    custom_settings = {
        "LOG_FILE": f"{name}.log" if write_log_to_file else None,
    }

class LotOnlineConfiscateSpider(LotOnlineOldBaseSpider):
    name = "lot_online_old_confiscate"
    custom_settings = {
        "LOG_FILE": f"{name}.log" if write_log_to_file else None,
    }

class LotOnlineLeaseSpider(LotOnlineOldBaseSpider):
    name = "lot_online_old_lease"
    custom_settings = {
        "LOG_FILE": f"{name}.log" if write_log_to_file else None,
    }

class LotOnlinePrivatizationSpider(LotOnlineOldBaseSpider):
    name = "lot_online_old_privatization"
    custom_settings = {
        "LOG_FILE": f"{name}.log" if write_log_to_file else None,
    }

class LotOnlineRadSpider(LotOnlineOldBaseSpider):
    name = "lot_online_old_rad"
    custom_settings = {
        "LOG_FILE": f"{name}.log" if write_log_to_file else None,
    }
