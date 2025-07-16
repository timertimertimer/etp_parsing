# -*- coding: utf-8 -*-
import scrapy
import logging
from typing import Iterable
from scrapy import Request, FormRequest
from app.crawlers.items import EtpItemLoader, EtpItem
from app.crawlers.base import BaseSpider
from app.utils.config import write_log_to_file
from ..app import Combo
from ..config import page_limits, formdata, data_origin

logger = logging.getLogger(__name__)


class Rutrade24Spider(BaseSpider):
    name = "rutrade24"
    start_urls = ["https://ru-trade24.ru/query/Filter"]
    custom_settings = {
        "LOG_FILE": f"{name}.log" if write_log_to_file else None,
    }

    def __init__(self):
        super(Rutrade24Spider, self).__init__(data_origin)

    def start_requests(self) -> Iterable[Request]:
        yield FormRequest(
            self.start_urls[0], self.parse, method="POST", formdata=formdata
        )

    def parse(self, response, **kwargs):
        current_page = self.get_currentPage(response)
        nextPage_url = self.get_next_page(response)
        trade_containers = response.css(".row.row--v-offset.trade-card")

        if len(trade_containers) != 25 and nextPage_url is not None:
            logger.warning(
                "Площадка: ru-trade24.ru. "
                + "Cсылка: %s. " % response.url
                + "Полученое количество ссылок торгов не равно 25. "
                + "Полученое количество: '%s'." % len(trade_containers)
            )

        if page_limits["page_start"] <= current_page <= page_limits["page_stop"]:
            for trade_container in trade_containers:
                trade_link = (
                    "https://ru-trade24.ru" + trade_container.css("a::attr(href)").get()
                )
                status = trade_container.css(".trade-card__status::text").get()
                if trade_link not in self.previous_trades:
                    yield scrapy.Request(
                        url=trade_link,
                        callback=self.parse_trade,
                        cb_kwargs=dict(status=status),
                    )

        if nextPage_url is not None and current_page <= page_limits["page_stop"]:
            formdata["page"] = str(current_page + 1)
            yield FormRequest(
                self.start_urls[0],
                method="POST",
                formdata=formdata,
                callback=self.parse,
            )

    def get_currentPage(self, response):
        for page in response.css("div.paging a"):
            if page.css("::attr(href)").get() == "#":
                return int(page.css("::text").get())

    def get_next_page(self, response):
        next_href = response.css(".paging__arrow--next::attr(href)").get()
        if next_href:
            return "http://ru-trade24.ru/" + next_href

    def parse_trade(self, response, status):
        combo = Combo(response)
        general_files = combo.download_general()
        address = combo.get_debtor_address()
        common_data = {
            "data_origin": data_origin,
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
                "files": {"general": general_files, "lot": combo.download_lot(lot)},
            }
            item_data = {**common_data, **lot_data}
            loader = EtpItemLoader(item=EtpItem(), response=response)
            for key, value in item_data.items():
                loader.add_value(key, value)
            yield loader.load_item()
