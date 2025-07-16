import urllib.parse
from scrapy import Request
from bs4 import BeautifulSoup as BS
from scrapy_splash import SplashRequest
from scrapy_splash import SplashFormRequest, SlotPolicy

from app.crawlers.items import EtpItem, EtpItemLoader
from app.crawlers.base import BaseSpider
from app.db.models import AuctionPropertyType
from app.utils import URL
from ..combo import Combo
from ..config import *


class FabrikantBaseSpider(BaseSpider):
    name = "fabrikant"
    property_type = None

    def __init__(self):
        super(FabrikantBaseSpider, self).__init__(data_origin_url)

    def start_requests(self):
        yield SplashRequest(
            start_url,
            self.start_requests_query,
            endpoint="execute",
            cache_args=["lua_source"],
            args={"lua_source": script_lua},
            slot_policy=SlotPolicy.PER_DOMAIN,
            session_id=1,
            errback=self.errback_httpbin,
        )

    def start_requests_query(self, response):
        soup = BS(response.text, "lxml")
        formdata["type_hash"] = soup.find(attrs={"id": "type_hash"})["value"]
        formdata["filter_id"] = str(filter_ids[self.property_type.value])
        yield SplashFormRequest.from_response(
            response=response,
            url=response.url,
            formdata=formdata,
            callback=self.parse,
            meta={"current_page": 1},
        )

    def parse(self, response, all_links: set = None):
        current_page = response.meta["current_page"]
        links = response.css(".marketplace-unit.ready h4 a::attr(href)").getall()
        all_links = (all_links or set()).union(links)
        # next_page = response.xpath(
        #     '//a[contains(@class, "pagination__nav-btn")]/@href'
        # ).getall()[-1]
        next_page = None  # FIXME
        link = URL.url_join(data_origin_url, next_page)
        parse_link = urllib.parse.parse_qs(urllib.parse.urlsplit(link).query)
        if int(current_page) < int(parse_link.get("page", [0])[0]):
            yield SplashRequest(
                link,
                self.parse,
                endpoint="execute",
                cache_args=["lua_source"],
                args={"lua_source": script_lua},
                slot_policy=SlotPolicy.PER_DOMAIN,
                session_id=1,
                errback=self.errback_httpbin,
                meta={"current_page": "".join(parse_link["page"])},
                cb_kwargs={"all_links": all_links},
            )
        else:
            for link in all_links:
                link = link.replace("https://fabrikant.ru", "https://www.fabrikant.ru")
                if link not in self.previous_trades:
                    yield Request(link, self.parse_trade)

    async def parse_trade(self, response):
        combo = Combo(response)
        for lot in combo.count_lots():
            transfer = EtpItem()
            transfer["data_origin"] = data_origin_url
            transfer["property_type"] = self.property_type.value
            transfer["trading_id"] = combo.trading_id
            transfer["trading_link"] = combo.trading_link
            transfer["trading_number"] = combo.trading_number
            transfer["trading_type"] = combo.trading_type
            transfer["trading_form"] = combo.trading_form
            transfer["trading_org"] = combo.trading_org
            transfer["trading_org_inn"] = combo.trading_org_inn
            transfer["trading_org_contacts"] = combo.trading_org_contacts
            transfer["msg_number"] = combo.msg_number
            transfer["case_number"] = combo.case_number
            transfer["debtor_inn"] = combo.debtor_inn
            transfer["address"] = combo.address
            transfer["arbit_manager"] = combo.arbit_manager
            transfer["arbit_manager_inn"] = combo.arbit_manager_inn
            transfer["arbit_manager_org"] = combo.arbit_manager_org
            transfer["status"] = combo.get_status(lot)
            transfer["lot_id"] = combo.get_lot_id(lot)
            transfer["lot_link"] = combo.get_lot_link(lot)
            transfer["lot_number"] = combo.get_lot_number(lot)
            transfer["short_name"] = combo.get_short_name(lot)
            transfer["lot_info"] = combo.get_lot_info(lot)
            transfer["property_information"] = combo.get_property_information(lot)
            transfer["categories"] = combo.get_categories(lot)
            if transfer["trading_type"] in ["auction", "competition"]:
                transfer["start_date_requests"] = combo.get_start_date_requests(lot)
                transfer["end_date_requests"] = combo.get_end_date_requests(lot)
                transfer["start_date_trading"] = combo.get_start_date_trading(lot)
                transfer["end_date_trading"] = combo.get_end_date_trading(lot)
                transfer["start_price"] = combo.get_start_price(lot)
                transfer["step_price"] = combo.get_step_price(lot)
            else:
                transfer["periods"] = combo.get_periods(lot)
                transfer["start_date_requests"] = transfer["periods"][0][
                    "start_date_requests"
                ]
                transfer["end_date_requests"] = transfer["periods"][-1][
                    "start_date_requests"
                ]
                transfer["start_date_trading"] = transfer["periods"][0][
                    "start_date_requests"
                ]
                transfer["end_date_trading"] = transfer["periods"][-1][
                    "end_date_trading"
                ]
                transfer["start_price"] = transfer["periods"][0]["current_price"]
            yield Request(
                url=combo.link_doc_page(response.url),
                callback=self.documentation,
                cb_kwargs={"transfer": transfer},
                dont_filter=True,
            )

    def documentation(self, response, transfer):
        combo = Combo(response)
        general = combo.download_general()
        lot_file = combo.download_lot(transfer["lot_number"])
        if lot_file is None:
            lot_file = list()
        loader = EtpItemLoader(EtpItem(), response=response)
        loader.add_value("data_origin", transfer["data_origin"])
        loader.add_value("property_type", transfer["property_type"])
        loader.add_value("trading_id", transfer["trading_id"])
        loader.add_value("trading_link", transfer["trading_link"])
        loader.add_value("trading_number", transfer["trading_number"])
        loader.add_value("trading_type", transfer["trading_type"])
        loader.add_value("trading_form", transfer["trading_form"])
        loader.add_value("trading_org", transfer["trading_org"])
        loader.add_value("trading_org_inn", transfer["trading_org_inn"])
        loader.add_value("trading_org_contacts", transfer["trading_org_contacts"])
        loader.add_value("msg_number", transfer["msg_number"])
        loader.add_value("case_number", transfer["case_number"])
        loader.add_value("debtor_inn", transfer["debtor_inn"])
        loader.add_value("address", transfer["address"])
        loader.add_value("arbit_manager", transfer["arbit_manager"])
        loader.add_value("arbit_manager_inn", transfer["arbit_manager_inn"])
        loader.add_value("arbit_manager_org", transfer["arbit_manager_org"])
        loader.add_value("status", transfer["status"])
        loader.add_value("lot_id", transfer["lot_id"])
        loader.add_value("lot_link", transfer["lot_link"])
        loader.add_value("lot_number", transfer["lot_number"])
        loader.add_value("short_name", transfer["short_name"])
        loader.add_value("lot_info", transfer["lot_info"])
        loader.add_value("property_information", transfer["property_information"])
        loader.add_value("categories", transfer["categories"])
        loader.add_value("start_date_requests", transfer["start_date_requests"])
        loader.add_value("end_date_requests", transfer["end_date_requests"])
        loader.add_value("start_date_trading", transfer["start_date_trading"])
        loader.add_value("end_date_trading", transfer["end_date_trading"])
        loader.add_value("start_price", transfer["start_price"])
        loader.add_value("step_price", transfer.get("step_price"))
        loader.add_value("periods", transfer.get("periods"))
        loader.add_value("files", {"general": general, "lot": lot_file})
        yield loader.load_item()


class FabrikantBankruptcySpider(FabrikantBaseSpider):
    name = "fabrikant_bankruptcy"
    property_type = AuctionPropertyType.bankruptcy


class FabrikantCommercialSpider(FabrikantBaseSpider):
    name = "fabrikant_commercial"
    property_type = AuctionPropertyType.commercial


class FabrikantLegalEntitiesSpider(FabrikantBaseSpider):
    name = "fabrikant_legal_entities"
    property_type = AuctionPropertyType.legal_entities

class FabrikantFZ223Spider(FabrikantBaseSpider):
    name = "fabrikant_fz223"
    property_type = AuctionPropertyType.fz223
