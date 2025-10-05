import asyncio
from typing import Iterable

import scrapy
from playwright.async_api import Page
from scrapy import Request
from scrapy_playwright.page import PageMethod

from app.crawlers.items import EtpItem, EtpItemLoader
from app.crawlers.base import BaseSpider
from app.db.models import AuctionPropertyType
from app.utils import URL, logger
from app.utils.config import trash_resources, write_log_to_file
from ..trades.combo import ComposeTrades
from ..config import data_origin_url, start_date
from ..locators.serp_locator import SerpLocator


async def filter_lots(page: Page) -> str:
    await page.route(
        "**/*",
        lambda route, request: route.abort()
        if request.resource_type in trash_resources
        else route.continue_(),
    )
    is_bankr_selector = 'input[name="isbankr"]'
    await page.wait_for_selector(selector=is_bankr_selector, state="attached")
    await page.evaluate("document.querySelector('input[name=\"isbankr\"]').click()")
    await asyncio.sleep(0.5)
    await page.evaluate("document.querySelector('input[name=\"isauk\"]').click()")
    await asyncio.sleep(0.5)
    await page.evaluate("document.querySelector('input[name=\"ispub\"]').click()")
    await asyncio.sleep(0.5)
    await page.evaluate(
        f"document.querySelector('input[name=\"date_nach_ot\"]').value = '{start_date}'"
    )
    await asyncio.sleep(0.5)
    await page.click(".search-submit")
    await asyncio.sleep(5)
    return page.url


class MetsSpider(BaseSpider):
    name = "mets"
    start_urls = ["https://m-ets.ru/search"]
    property_type = AuctionPropertyType.bankruptcy
    custom_settings = {
        "LOG_FILE": f"{name}.log" if write_log_to_file else None,
        "PLAYWRIGHT_ABORT_REQUEST": lambda request: request.resource_type
        in trash_resources,
        # "PLAYWRIGHT_LAUNCH_OPTIONS": {"headless": False},
    }

    def __init__(self):
        super().__init__(data_origin_url)
        self.formatted_url = ""

    def start_requests(self) -> Iterable[Request]:
        for url in self.start_urls:
            yield Request(
                url,
                callback=self.parse,
                meta=dict(
                    playwright=True,
                    playwright_page_methods=[
                        PageMethod("goto", url),
                        PageMethod(filter_lots),
                    ],
                ),
            )

    def parse(self, response: scrapy.http.Response, **kwargs) -> Iterable[Request]:
        self.formatted_url = self.formatted_url or response.url
        current_page = response.meta.get("current_page", 1)
        total_pages = int(
            response.xpath(SerpLocator.count_pagination_loc).get() or current_page
        )
        logger.info(f"Current page: {current_page}/{total_pages}")
        links_to_lots = response.xpath(SerpLocator.link_to_trade_loc).getall()
        trade_links = response.meta.get("trade_links", set())
        for link in links_to_lots:
            trading_link = "-".join(URL.url_join(data_origin_url, link).split("-")[:-1])
            if trading_link not in self.previous_trades:
                self.previous_trades.append(trading_link)
                trade_links.add(trading_link + "-1")
        if total_pages > 1 and int(current_page) < total_pages:
            current_page = int(current_page) + 1
            yield Request(
                self.formatted_url + f"&page={current_page}",
                callback=self.parse,
                dont_filter=True,
                meta={"current_page": current_page, "trade_links": trade_links},
            )
        else:
            for i, link in enumerate(trade_links):
                yield Request(
                    URL.parse_url(link),
                    callback=self.sort_trades,
                    errback=self.errback_httpbin,
                )
                logger.info(f"Parsed trades: {i + 1}/{len(trade_links)}")

    def sort_trades(self, response):
        comp = ComposeTrades(response=response)
        trading_type_ = comp.offer.trading_type
        trading_type = comp.sort_trading_type(trading_type_)
        trading_form = comp.get_trading_form(trading_type_)
        match trading_type:
            case "auction":
                yield from self.parse_auction(
                    response=response,
                    trading_type=trading_type,
                    trading_form=trading_form,
                )
            case "competition":
                yield from self.parse_auction(
                    response=response,
                    trading_type=trading_type,
                    trading_form=trading_form,
                )
            case "offer":
                yield from self.parse_offer(
                    response=response,
                    trading_type=trading_type,
                    trading_form=trading_form,
                )
            case _:
                pass

    def parse_auction(self, response, trading_type, trading_form):
        comp = ComposeTrades(response=response)
        property_info = comp.offer.property_info
        status = comp.offer.status
        for lot in comp.offer.count_lots:
            loader = EtpItemLoader(EtpItem(), response=response)
            loader.add_value("data_origin", data_origin_url)
            loader.add_value("property_type", self.property_type.value)
            loader.add_value("trading_id", comp.offer.trading_id)
            loader.add_value("trading_link", comp.offer.trading_link)
            loader.add_value("trading_number", comp.offer.trading_number)
            loader.add_value("trading_type", trading_type)
            loader.add_value("trading_form", trading_form)
            trading_number = loader.get_collected_values("trading_number")
            loader.add_value("trading_org", comp.offer.trading_org)
            loader.add_value("trading_org_inn", comp.offer.trading_org_inn)
            loader.add_value("trading_org_contacts", comp.offer.trading_org_contacts)
            loader.add_value("msg_number", comp.offer.msg_number)
            loader.add_value("case_number", comp.offer.case_number)
            loader.add_value("debtor_inn", comp.offer.debitor_inn)
            loader.add_value("arbit_manager", comp.offer.arbitr_manager_org)
            loader.add_value("arbit_manager_inn", comp.offer.arbitr_inn)
            loader.add_value("arbit_manager_org", comp.offer.arbitr_org)
            lot_number = comp.offer.get_lot_number(lot)
            loader.add_value("status", status)
            loader.add_value("lot_link", comp.offer.get_lot_link(lot_number))
            loader.add_value("lot_id", comp.offer.get_lot_id(lot))
            loader.add_value("lot_number", lot_number)
            loader.add_value("short_name", comp.offer.get_short_name(lot_number))
            loader.add_value("lot_info", comp.offer.get_lot_info(lot_number))
            loader.add_value("address", comp.offer.address)
            loader.add_value("property_information", property_info)
            loader.add_value("start_price", comp.offer.get_start_price(lot_number))
            loader.add_value(
                "step_price", comp.auc.get_step_price(trading_number, lot_number)
            )
            loader.add_value("start_date_requests", comp.auc.start_date_requests)
            loader.add_value("end_date_requests", comp.auc.end_date_requests)
            loader.add_value("start_date_trading", comp.auc.start_date_trading)
            loader.add_value("end_date_trading", comp.auc.end_date_trading)
            loader.add_value("periods", None)
            loader.add_value("categories", None)
            files_lot = comp.offer.download()
            loader.add_value("files", {"general": [], "lot": files_lot})
            yield loader.load_item()

    def parse_offer(self, response, trading_type, trading_form):
        comp = ComposeTrades(response=response)
        property_info = comp.offer.property_info
        status = comp.offer.status
        for lot in comp.offer.count_lots:
            loader = EtpItemLoader(EtpItem(), response=response)
            loader.add_value("data_origin", data_origin_url)
            loader.add_value("property_type", self.property_type)
            loader.add_value("trading_id", comp.offer.trading_id)
            loader.add_value("trading_link", comp.offer.trading_link)
            loader.add_value("trading_number", comp.offer.trading_number)
            loader.add_value("trading_type", trading_type)
            loader.add_value("trading_form", trading_form)
            loader.add_value("trading_org", comp.offer.trading_org)
            loader.add_value("trading_org_inn", comp.offer.trading_org_inn)
            loader.add_value("trading_org_contacts", comp.offer.trading_org_contacts)
            loader.add_value("msg_number", comp.offer.msg_number)
            loader.add_value("case_number", comp.offer.case_number)
            loader.add_value("debtor_inn", comp.offer.debitor_inn)
            loader.add_value("arbit_manager", comp.offer.arbitr_manager_org)
            loader.add_value("arbit_manager_inn", comp.offer.arbitr_inn)
            loader.add_value("arbit_manager_org", comp.offer.arbitr_org)
            lot_number = comp.offer.get_lot_number(lot)
            loader.add_value("status", status)
            loader.add_value("lot_link", comp.offer.get_lot_link(lot_number))
            loader.add_value("lot_id", comp.offer.get_lot_id(lot))
            loader.add_value("lot_number", lot_number)
            loader.add_value("short_name", comp.offer.get_short_name(lot_number))
            loader.add_value("lot_info", comp.offer.get_lot_info(lot_number))
            loader.add_value("address", comp.offer.address)
            loader.add_value("property_information", property_info)
            loader.add_value("start_price", comp.offer.get_start_price(lot_number))
            loader.add_value(
                "start_date_requests", comp.offer.get_start_date_requests(lot_number)
            )
            loader.add_value(
                "end_date_requests", comp.offer.get_end_date_requests(lot_number)
            )
            loader.add_value(
                "start_date_trading", comp.offer.get_start_date_requests(lot_number)
            )
            loader.add_value(
                "end_date_trading", comp.offer.get_end_date_requests(lot_number)
            )
            loader.add_value("periods", comp.offer.get_periods(lot_number))
            loader.add_value("categories", None)
            files_lot = comp.offer.download()
            loader.add_value("files", {"general": [], "lot": files_lot})
            yield loader.load_item()

    async def errback(self, failure):
        page = failure.request.meta["playwright_page"]
        await page.close()
