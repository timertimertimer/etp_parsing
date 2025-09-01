from typing import Iterable

from scrapy import Request, FormRequest

from app.crawlers.base import BaseSpider
from ..config import start_date, end_date, data_origin_urls, urls
from ..trades.combo import Combo
from app.utils import URL
from app.utils.config import write_log_to_file
from app.crawlers.items import EtpItemLoader, EtpItem


class ElectroTorgiBaseSpider(BaseSpider):
    name = "base"
    property_type = None
    custom_settings = {
        "LOG_FILE": f"{name}.log" if write_log_to_file else None,
    }

    @classmethod
    def set_links(cls):
        cls.data_origin_url = data_origin_urls.get(cls.name)
        cls.url = urls.get(cls.name)

    def __init__(self):
        self.set_links()
        super().__init__(self.data_origin_url)

    def start_requests(self) -> Iterable[Request]:
        params_data = {
            "search": "true",
            "applications_start_date": f"{start_date} ⇆ {end_date}",
            "applications_start_date_from": start_date,
            "applications_start_date_to": end_date,
        }
        yield FormRequest(
            self.url + "lots",
            self.parse,
            formdata=params_data,
            method="GET",
        )

    def parse(self, response, **kwargs):
        links = response.xpath('//a[@class="block-lot"]/@href').getall()
        for link in links:
            link = URL.url_join(self.url, link)
            if link not in self.previous_trades:
                yield Request(link, self.parse_trade)

        pagination = response.xpath('//ul[@class="pagination"]').get()
        if pagination:
            next_page_link = response.xpath('//a[@rel="next"]/@href').get()
            if next_page_link:
                yield Request(next_page_link.replace("http://", "https://"), self.parse)

    def parse_trade(self, response):
        combo = Combo(response)
        trading_id = trading_number = combo.id_
        trading_link = response.url
        trading_type, trading_form = combo.trading_type_and_form
        trading_org = combo.trading_org
        trading_org_inn = combo.trading_org_inn
        trading_org_contacts = combo.trading_org_contacts
        msg_number = combo.msg_number
        case_number = combo.case_number
        debtor_inn = combo.debtor_inn
        address = combo.address
        arbit_manager = combo.arbit_manager
        arbit_manager_inn = combo.arbit_manager_inn
        arbit_manager_org = combo.arbit_manager_org
        start_date_requests = combo.start_date_requests
        end_date_requests = combo.end_date_requests
        files = combo.download()
        for lot_link, lot_number, status in combo.get_lots():
            loader = EtpItemLoader(EtpItem(), response=response)
            loader.add_value("data_origin", self.url)
            loader.add_value("property_type", self.property_type)
            loader.add_value("trading_id", trading_id)
            loader.add_value("trading_link", trading_link)
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
            loader.add_value("lot_link", lot_link)
            loader.add_value("lot_number", lot_number)
            loader.add_value("status", status)
            loader.add_value("start_date_requests", start_date_requests)
            loader.add_value("end_date_requests", end_date_requests)
            yield Request(
                lot_link,
                self.parse_lot,
                cb_kwargs={"loader": loader, "general_files": files},
            )

    def parse_lot(self, response, loader, general_files):
        combo = Combo(response)
        loader.add_value("lot_id", combo.id_)
        loader.add_value("short_name", combo.short_name)
        loader.add_value("lot_info", combo.lot_info)
        loader.add_value("property_information", combo.property_information)
        loader.add_value("start_price", combo.start_price)
        loader.add_value("step_price", combo.step_price)
        loader.add_value("categories", combo.categories)
        if loader.get_collected_values("trading_type")[0] in ["auction", "competition"]:
            loader.add_value("start_date_trading", combo.auc.start_date_trading)
            loader.add_value("end_date_trading", combo.auc.end_date_trading)
        else:
            loader.add_value("periods", combo.offer.periods)
            loader.add_value("start_date_trading", combo.offer.start_date_trading)
            loader.add_value("end_date_trading", combo.offer.end_date_trading)
        lot_files = combo.download()
        loader.add_value("files", {"general": general_files, "lot": lot_files})
        yield loader.load_item()
