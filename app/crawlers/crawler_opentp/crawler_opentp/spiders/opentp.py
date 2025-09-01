from scrapy import Request

from app.utils import URL
from app.crawlers.items import EtpItem, EtpItemLoader
from app.crawlers.base import BaseSpider
from ..config import data_origin_url
from ..combo import Combo


class OpentpSpider(BaseSpider):
    name = "opentp"
    start_urls = ["http://opentp.ru/tenders/kind/s/"]

    def __init__(self):
        super(OpentpSpider, self).__init__(data_origin_url)

    def parse(self, response, unique_links: set = None):
        combo = Combo(response=response)
        unique_links = unique_links or set()
        unique_links.update(combo.get_trading_links())
        next_page = combo.get_next_page()
        if next_page:
            yield Request(
                URL.url_join(data_origin_url, next_page),
                self.parse,
                cb_kwargs={"unique_links": unique_links},
            )
        else:
            for link in list(unique_links):
                if link not in self.previous_trades:
                    yield Request(link, callback=self.parse_trade)

    def parse_trade(self, response):
        combo = Combo(response)
        trading_number, trading_type = combo.get_main_info()
        trading_form = combo.trading_form
        trading_id = combo.trading_id
        trading_org = combo.trading_org
        trading_org_inn = combo.trading_org_inn
        trading_org_contacts = combo.trading_org_contacts
        msg_number = combo.msg_number
        case_number = combo.case_number
        debtor_inn = combo.debitor_inn
        arbit_manager = combo.arbitr_manager
        arbit_manager_inn = combo.arbitr_manager_inn
        arbit_manager_org = combo.arbitr_manager_org
        start_date_requests = combo.start_date_requests
        end_date_requests = combo.end_date_requests
        general_files = combo.download_general()
        for (
            lot_link,
            lot_number,
            short_name,
            status,
            address,
            start_price,
        ) in combo.get_lots():
            loader = EtpItemLoader(EtpItem(), response=response)
            loader.add_value("data_origin", data_origin_url)
            loader.add_value("trading_id", trading_id)
            loader.add_value("trading_link", response.url)
            loader.add_value("trading_number", trading_number)
            loader.add_value("trading_type", trading_type)
            loader.add_value("trading_form", trading_form)
            loader.add_value("trading_org", trading_org)
            loader.add_value("trading_org_inn", trading_org_inn)
            loader.add_value("trading_org_contacts", trading_org_contacts)
            loader.add_value("msg_number", msg_number)
            loader.add_value("case_number", case_number)
            loader.add_value("debtor_inn", debtor_inn)
            loader.add_value("address", address)
            loader.add_value("arbit_manager", arbit_manager)
            loader.add_value("arbit_manager_inn", arbit_manager_inn)
            loader.add_value("arbit_manager_org", arbit_manager_org)
            loader.add_value("status", status)
            loader.add_value("lot_link", lot_link)
            loader.add_value("lot_number", lot_number)
            loader.add_value("short_name", short_name)
            loader.add_value("property_information", combo.property_information)
            loader.add_value("start_date_requests", start_date_requests)
            loader.add_value("end_date_requests", end_date_requests)
            loader.add_value("start_date_trading", combo.start_date_trading)
            loader.add_value("end_date_trading", combo.end_date_trading)
            loader.add_value("start_price", start_price)
            yield Request(
                lot_link,
                self.parse_lot,
                cb_kwargs={"loader": loader, "general_files": general_files},
            )

    def parse_lot(self, response, loader, general_files):
        combo = Combo(response)
        loader.add_value("lot_id", combo.lot_id)
        loader.add_value("lot_info", combo.lot_info)
        if loader.get_collected_values("trading_type")[0] == "auction":
            loader.add_value("step_price", combo.step_price)
        loader.add_value(
            "files", {"general": general_files, "lot": combo.download_lot()}
        )
        loader.add_value("categories", None)
        yield loader.load_item()
