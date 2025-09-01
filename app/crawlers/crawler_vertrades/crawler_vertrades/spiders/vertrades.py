from typing import Iterable

from scrapy import Request, FormRequest

from app.crawlers.items import EtpItem, EtpItemLoader
from app.crawlers.base import BaseSpider
from app.utils import URL
from app.utils.config import start_date
from ..config import data_origin, params_data
from ..trades.combo import Combo


class VertradesSpider(BaseSpider):
    name = "vertrades"
    start_urls = ["https://bankrot.vertrades.ru/bidding"]

    def __init__(self):
        super().__init__(data_origin)

    def start_requests(self) -> Iterable[Request]:
        params_data["from"] = start_date
        yield FormRequest(
            self.start_urls[0], callback=self.parse, formdata=params_data, method="GET"
        )

    def parse(self, response):
        combo = Combo(response)
        for link in combo.serp.get_trading_links():
            if (
                URL.url_join(data_origin, link.removesuffix("#lot"))
                not in self.previous_trades
            ):
                yield response.follow(link, callback=self.parse_trading)

    def parse_trading(self, response):
        combo = Combo(response)
        trading_type = combo.trading_type
        trading_id = combo.trading_id
        trading_number = combo.trading_number
        trading_form = combo.trading_form
        status = combo.status
        trading_org = combo.trading_org
        trading_org_contacts = combo.trading_org_contacts
        msg_number = combo.msg_number
        case_number = combo.case_number
        debtor_inn = combo.debitor_inn
        address = combo.address
        arbit_manager = combo.arbitr_manager
        arbit_manager_inn = combo.arbitr_inn
        arbit_manager_org = combo.arbitr_manager_org
        start_date_requests = combo.start_date_requests
        end_date_requests = combo.end_date_requests
        general_files = combo.download_general()
        for lot in combo.get_lots():
            loader = EtpItemLoader(EtpItem(), response=response)
            loader.add_value("data_origin", data_origin)
            loader.add_value("trading_id", trading_id)
            loader.add_value("trading_link", response.url)
            loader.add_value("trading_number", trading_number)
            loader.add_value("trading_type", trading_type)
            loader.add_value("trading_form", trading_form)
            loader.add_value("status", status)
            loader.add_value("trading_org", trading_org)
            loader.add_value("trading_org_inn", None)
            loader.add_value("trading_org_contacts", trading_org_contacts)
            loader.add_value("msg_number", msg_number)
            loader.add_value("case_number", case_number)
            loader.add_value("debtor_inn", debtor_inn)
            loader.add_value("address", address)
            loader.add_value("arbit_manager", arbit_manager)
            loader.add_value("arbit_manager_inn", arbit_manager_inn)
            loader.add_value("arbit_manager_org", arbit_manager_org)
            loader.add_value("lot_number", combo.lot_number(lot))
            loader.add_value("short_name", combo.short_name(lot))
            loader.add_value("lot_info", combo.lot_info(lot))
            loader.add_value("property_information", combo.property_information(lot))
            loader.add_value("start_price", combo.start_price(lot))
            loader.add_value("categories", combo.categories(lot))
            loader.add_value("start_date_requests", start_date_requests)
            loader.add_value("end_date_requests", end_date_requests)
            lot_files = combo.download_lot(lot)
            loader.add_value("files", {"general": general_files, "lot": lot_files})
            if trading_type in ["auction", "competition"]:
                loader.add_value("start_date_trading", combo.auc.start_date_trading)
                loader.add_value("end_date_trading", combo.auc.end_date_trading)
                loader.add_value("step_price", combo.auc.step_price(lot))
            elif trading_type == "offer":
                loader.add_value(
                    "start_date_trading", combo.offer.start_date_trading(lot)
                )
                loader.add_value("end_date_trading", combo.offer.end_date_trading(lot))
                loader.add_value("periods", combo.offer.get_periods(lot))
            else:
                ...
            yield loader.load_item()
