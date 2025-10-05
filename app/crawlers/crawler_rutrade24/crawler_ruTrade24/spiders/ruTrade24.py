# -*- coding: utf-8 -*-
from typing import Iterable
from scrapy import Request, FormRequest

from app.crawlers.items import EtpItemLoader, EtpItem
from app.crawlers.base import BaseSpider
from app.db.models import AuctionPropertyType
from app.utils import URL
from app.utils.config import write_log_to_file
from ..combo import Combo
from ..config import (
    page_limits,
    formdata,
    main_data_origin,
    start_urls,
    data_origins,
    pagination_urls,
)

BOUNDARY = "wL36Yn8afVp8Ag7AmP8qZ0SA4n1v9T"


def build_multipart(fields: dict, boundary=BOUNDARY, encoding="utf-8"):
    lines = []
    for name, value in fields.items():
        lines.append(f"--{boundary}")
        lines.append(f'Content-Disposition: form-data; name="{name}"')
        lines.append("")  # пустая строка между заголовками части и телом
        lines.append(value if value is not None else "")
    lines.append(f"--{boundary}--")
    lines.append("")  # финальный CRLF
    body = "\r\n".join(lines).encode(encoding)
    return body, f"multipart/form-data; boundary={boundary}"


class Rutrade24BaseSpider(BaseSpider):
    name = "base"
    custom_settings = {
        "LOG_FILE": f"{name}.log" if write_log_to_file else None,
    }

    def __init__(self):
        super(Rutrade24BaseSpider, self).__init__(main_data_origin)

    def start_requests(self) -> Iterable[Request]:
        body, content_type = build_multipart(formdata)
        yield Request(
            start_urls[self.property_type.value],
            self.parse,
            method="POST",
            headers={"Content-Type": content_type},
            body=body,
        )

    def parse(self, response, **kwargs):
        current_page = self.get_current_page(response)
        nextPage_url = self.get_next_page(response, self.property_type.value)
        trade_containers = response.css(".row.row--v-offset.trade-card")

        if page_limits["page_start"] <= current_page <= page_limits["page_stop"]:
            for trade_container in trade_containers:
                trade_link = URL.url_join(
                    data_origins[self.property_type.value],
                    trade_container.css("a::attr(href)").get(),
                )
                status = trade_container.css(".trade-card__status::text").get()
                if trade_link not in self.previous_trades:
                    yield Request(
                        url=trade_link,
                        callback=self.parse_trade,
                        cb_kwargs=dict(status=status),
                    )

        if nextPage_url is not None and current_page <= page_limits["page_stop"]:
            formdata["page"] = str(current_page + 1)
            yield FormRequest(
                pagination_urls[self.property_type.value],
                method="POST",
                formdata=formdata,
                callback=self.parse,
            )

    def get_current_page(self, response):
        for page in response.css("div.paging a"):
            if page.css("::attr(href)").get() == "#":
                return int(page.css("::text").get())
        return None

    def get_next_page(self, response, property_type: str):
        next_href = response.css(".paging__arrow--next::attr(href)").get()
        if next_href:
            return URL.url_join(data_origins[property_type], next_href)
        return None

    def parse_trade(self, response, status):
        combo = Combo(response)
        general_files = combo.download_general(self.property_type.value)
        address = combo.get_debtor_address()
        common_data = {
            "data_origin": main_data_origin,
            "property_type": self.property_type,
            "trading_id": combo.trading_id,
            "trading_link": combo.trading_link,
            "trading_number": combo.trading_number,
            "trading_type": combo.trading_type,
            "trading_form": combo.trading_form,
            "trading_org": combo.trading_org,
            "trading_org_inn": combo.trading_org_inn,
            "trading_org_contacts": combo.trading_org_contacts,
            "msg_number": combo.msg_number,
            "case_number": combo.case_number,
            "debtor_inn": combo.debtor_inn,
            "address": address,
            "arbit_manager": combo.arbit_manager,
            "arbit_manager_inn": combo.arbit_manager_inn,
            "arbit_manager_org": combo.arbit_manager_org,
            "status": combo.parse_status(status),
            "start_date_requests": combo.start_date_requests,
            "end_date_requests": combo.end_date_requests,
            "start_date_trading": combo.start_date_trading,
            "end_date_trading": combo.end_date_trading,
        }
        for lot in combo.get_lots():
            lot_data = {
                "lot_id": combo.lot_id,
                "lot_link": combo.lot_link,
                "lot_number": combo.lot_number(lot),
                "short_name": combo.short_name,
                "lot_info": combo.lot_info(lot),
                "property_information": combo.property_information,
                "periods": combo.periods(lot),
                "start_price": combo.start_price(lot),
                "step_price": combo.step_price(lot),
                "categories": combo.categories(lot),
                "files": {"general": general_files, "lot": combo.download_lot(lot, self.property_type.value)},
            }
            item_data = {**common_data, **lot_data}
            loader = EtpItemLoader(item=EtpItem(), response=response)
            for key, value in item_data.items():
                loader.add_value(key, value)
            yield loader.load_item()


class Rutrade24BankruptcySpider(Rutrade24BaseSpider):
    name = "rutrade24_bankruptcy"
    property_type = AuctionPropertyType.bankruptcy
    custom_settings = {
        "LOG_FILE": f"{name}.log" if write_log_to_file else None,
    }


class Rutrade24CommercialSpider(Rutrade24BaseSpider):
    name = "rutrade24_commercial"
    property_type = AuctionPropertyType.commercial
    custom_settings = {
        "LOG_FILE": f"{name}.log" if write_log_to_file else None,
    }
