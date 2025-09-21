import json
import re

from scrapy import Request, FormRequest
from scrapy_splash import SplashRequest, SlotPolicy

from app.crawlers.base import BaseSpider
from app.utils.config import write_log_to_file
from app.crawlers.items import EtpItem, EtpItemLoader
from ..config import (
    start_url,
    data_pagination,
    pagination_url,
    organization_ids,
    script_lua,
    main_data_origin,
)
from ..combo import Combo


class LotOnlineZalogBaseSpider(BaseSpider):
    name = "base"
    custom_settings = {
        "LOG_FILE": f"{name}.log" if write_log_to_file else None,
    }

    def __init__(self):
        super().__init__(main_data_origin)

    def start_requests(self):
        yield SplashRequest(
            start_url,
            callback=self.go_to,
            endpoint="execute",
            cache_args=["lua_source"],
            args={"lua_source": script_lua},
            slot_policy=SlotPolicy.PER_DOMAIN,
            errback=self.errback_httpbin,
        )

    def go_to(self, response, next_page: int = 1):
        data_pagination["organizationId"] = organization_ids[self.name.removeprefix('lot_online_zalog_')]
        data_pagination["page"] = str(next_page)
        if next_page > 1:
            json_res = json.loads(response.text)
            for lot in list(map(lambda x: x["id"], json_res["rows"])):
                link = f"https://zalog.lot-online.ru/user/collateral/catalog_page.html?id={lot}"
                if link not in self.previous_trades:
                    yield Request(link, self.parse_lot_page)
            if next_page - 1 < int(json_res["total"]):
                next_page += 1
                yield FormRequest(
                    pagination_url,
                    callback=self.go_to,
                    formdata=data_pagination,
                    cb_kwargs={"next_page": next_page},
                )
        else:
            next_page += 1
            yield FormRequest(
                pagination_url,
                callback=self.go_to,
                formdata=data_pagination,
                cb_kwargs={"next_page": next_page},
            )

    async def parse_lot_page(self, response):
        combo = Combo(response=response)
        short_name = combo.get_short_name()
        match = re.match(r".+?аренд.+", short_name, re.IGNORECASE)
        match1 = re.match(r"^arend.+", short_name, re.IGNORECASE)
        if not match and not match1:
            loader = EtpItemLoader(EtpItem(), response=response)
            loader.add_value("data_origin", start_url)
            # zalog не входит ни в одну категорию торгов
            # loader.add_value("property_type", self.property_type.value)
            loader.add_value("trading_id", combo.get_trading_id())
            loader.add_value("trading_link", response.url)
            loader.add_value("trading_number", combo.get_trading_id())
            loader.add_value("trading_type", "competition")
            loader.add_value("trading_form", "open")
            loader.add_value("trading_org", "Россельхозбанк")
            loader.add_value(
                "trading_org_contacts", combo.get_trading_org_contact()
            )
            loader.add_value("status", "active")
            loader.add_value("address", combo.address)
            loader.add_value("lot_number", "1")
            loader.add_value("short_name", short_name)
            loader.add_value("lot_info", combo.return_complete_lot_info())
            loader.add_value("property_information", combo.property_info())
            loader.add_value("start_date_requests", combo.start_date_requests())
            loader.add_value("end_date_requests", None)
            loader.add_value("start_date_trading", combo.start_date_requests())
            loader.add_value("end_date_trading", None)
            loader.add_value("start_price", combo.start_price())
            loader.add_value("categories", combo.get_categories())
            pictures = combo.get_all_pictures_link()
            lot_pictures = combo.download_img(pictures)
            loader.add_value("files", {"general": [], "lot": lot_pictures})
            yield loader.load_item()


class LotOnlineZalogRadSpider(LotOnlineZalogBaseSpider):
    name = "lot_online_zalog_rad"
    custom_settings = {
        "LOG_FILE": f"{name}.log" if write_log_to_file else None,
    }


class LotOnlineZalogRshbSpider(LotOnlineZalogBaseSpider):
    name = "lot_online_zalog_rshb"
    custom_settings = {
        "LOG_FILE": f"{name}.log" if write_log_to_file else None,
    }


class LotOnlineZalogSbrfSpider(LotOnlineZalogBaseSpider):
    name = "lot_online_zalog_sbrf"
    custom_settings = {
        "LOG_FILE": f"{name}.log" if write_log_to_file else None,
    }
