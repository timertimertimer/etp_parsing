import re

from scrapy_splash import SplashRequest
import scrapy_splash
from scrapy import Request
from bs4 import BeautifulSoup as BS

from app.crawlers.items import EtpItem, EtpItemLoader
from app.crawlers.base import BaseSpider
from app.db.models import AuctionPropertyType
from ..combo import Combo
from ..config import *


class SibtoptradeBaseSpider(BaseSpider):
    name = "sibtoptrade"
    start_urls = [data_origin]

    def __init__(self):
        super(SibtoptradeBaseSpider, self).__init__(data_origin)

    def start_requests(self):
        yield SplashRequest(
            self.start_urls[0],
            self.iterate_through_pages,
            endpoint="execute",
            cache_args=["lua_source"],
            args={"lua_source": script_lua},
            slot_policy=scrapy_splash.SlotPolicy.PER_DOMAIN,
            session_id=1,
            errback=self.errback_httpbin,
        )

    def iterate_through_pages(self, response):
        last_page = response.xpath(
            '//nav[@class="pagination"]//li[last()]/a/text()'
        ).get()
        for url in self.start_urls:
            current_page = "".join(
                re.findall(
                    r"page=(\d+).*",
                    url,
                )
            )
            if int(last_page) >= int(current_page):
                yield SplashRequest(
                    url,
                    self.parse,
                    endpoint="execute",
                    cache_args=["lua_source"],
                    args={"lua_source": script_lua},
                    slot_policy=scrapy_splash.SlotPolicy.PER_DOMAIN,
                    session_id=1,
                    errback=self.errback_httpbin,
                    dont_filter=True,
                )

    def parse(self, response):
        soup = BS(str(response.body.decode("utf-8")), "lxml")
        trades = soup.find("tbody").find_all("tr")
        for trade in trades:
            if trade.find("td", class_="td-divider"):
                continue
            link = trade.find("a")
            trading_number = "".join(link.get_text()).strip()
            status = (
                trade.find("td", class_="center")
                .find_next_sibling()
                .get_text()
                .strip()
                .lower()
            )
            link = link.get("href")
            if link not in self.previous_trades:
                yield Request(
                    url=link,
                    callback=self.parse_lots,
                    errback=self.errback_httpbin,
                    meta={"trading_number": trading_number, "status": status},
                )

    def parse_lots(self, response):
        loader = EtpItemLoader(EtpItem(), response=response)
        combo = Combo(response)
        loader.add_value("data_origin", data_origin)
        loader.add_value("property_type", self.property_type)
        loader.add_value("trading_id", combo.trading_id)
        loader.add_value("trading_link", combo.trading_link)
        loader.add_value("trading_number", response.meta["trading_number"])
        loader.add_value("trading_type", combo.trading_type)
        loader.add_value("trading_form", combo.trading_form)
        loader.add_value("msg_number", combo.msg_number)
        loader.add_value("case_number", combo.case_number)
        loader.add_value("debtor_inn", combo.debtor_inn)
        loader.add_value("address", combo.address)
        loader.add_value("trading_org", combo.trading_org)
        loader.add_value("trading_org_inn", combo.trading_org_inn)
        loader.add_value("trading_org_contacts", combo.trading_org_contacts)
        loader.add_value("arbit_manager", combo.arbit_manager)
        loader.add_value("arbit_manager_inn", combo.arbit_manager_inn)
        loader.add_value("arbit_manager_org", combo.arbit_manager_org)
        loader.add_value("status", response.meta["status"])
        loader.add_value("lot_id", None)
        loader.add_value("lot_link", None)
        loader.add_value("lot_info", None)
        loader.add_value("lot_number", combo.lot_number)
        loader.add_value("short_name", combo.short_name)
        loader.add_value("property_information", combo.property_information)
        loader.add_value("start_date_requests", combo.start_date_requests)
        loader.add_value("end_date_requests", combo.end_date_requests)
        loader.add_value("start_date_trading", combo.start_date_trading)
        loader.add_value("end_date_trading", combo.end_date_trading)
        loader.add_value("periods", combo.periods)
        loader.add_value("start_price", combo.start_price)
        loader.add_value("step_price", combo.step_price)
        loader.add_value("categories", None)
        loader.add_value(
            "files", {"general": combo.download_general(), "lot": combo.download_lot()}
        )
        return loader.load_item()


class SibtoptradeBankruptcySpider(SibtoptradeBaseSpider):
    name = "sibtoptrade_bankruptcy"
    property_type = AuctionPropertyType.bankruptcy
    start_urls = [url_bankruptcy]


class SibtoptradeCommercialSpider(SibtoptradeBaseSpider):
    name = "sibtoptrade_commercial"
    property_type = AuctionPropertyType.commercial
    start_urls = [url_commercial]
