import json
from typing import Callable

import xmltodict
from scrapy import Request
from scrapy_playwright.page import PageMethod
from playwright.async_api import Page
from playwright._impl._errors import TimeoutError as PlaywrightTimeoutError
from bs4 import BeautifulSoup as BS

from app.crawlers.crawler_sberbank.crawler_sberbank.spiders.base import (
    SberbankBaseSpider,
)
from app.crawlers.crawler_sberbank.crawler_sberbank.trades.html_combo import NewCombo
from app.crawlers.crawler_sberbank.crawler_sberbank.utils.config import (
    list_urls,
    data_origin_url,
)
from app.crawlers.items import EtpItemLoader, EtpItem
from app.db.models import AuctionPropertyType
from app.utils import logger
from app.utils.config import trash_resources, write_log_to_file, env

playwright_timeout = 30


async def wait_for_search_query(page: Page):
    for i in range(env.retry_count):
        try:
            await page.wait_for_event(
                "response",
                lambda r: "/SearchQuery/" in r.url and r.request.method == "POST",
                timeout=playwright_timeout * 1000,
            )
            return
        except PlaywrightTimeoutError as e:
            logger.warning(
                f"{page.url} | Timeout error ({playwright_timeout} sec), trying again {i + 1}/{env.retry_count}"
            )
            await page.reload()
    else:
        logger.error(
            f"{page.url} | Timeout error ({playwright_timeout} sec), tried {env.retry_count} times, stopping"
        )


class SberbankBaseHTMLSpider(SberbankBaseSpider):
    name = "base_html"
    custom_settings = {
        "LOG_FILE": f"{name}.log" if write_log_to_file else None,
        "PLAYWRIGHT_ABORT_REQUEST": lambda request: request.resource_type
        in trash_resources,
    }
    cookies_invalidated = False

    def invalidate_cookies(self):
        self.cookies_invalidated = True

    def update_cookies(
        self, after_func: Callable, after_args: list = None, after_kwargs: dict = None
    ):
        url = data_origin_url
        yield Request(
            url,
            callback=self.after_update_cookies,
            meta=dict(
                playwright=True,
                playwright_include_page=True,
                playwright_page_methods=[
                    PageMethod("goto", url)
                ],
                after_func=after_func,
                after_args=after_args or [],
                after_kwargs=after_kwargs or {},
            ),
        )

    def start_requests(self, cookies: dict = None):
        yield from self.update_cookies(super().start_requests)

    async def after_update_cookies(self, response):
        page = response.meta["playwright_page"]
        cookies = await page.context.cookies()
        self.cookies = {c["name"]: c["value"] for c in cookies}
        func = response.meta.get("after_func")
        args = response.meta.get("after_args", [])
        kwargs = response.meta.get("after_kwargs", {})
        if func:
            for req in func(*args, **kwargs):
                yield req

    def parse_table(self, response, **kwargs):
        soup = BS(json.loads(response.text)["data"]["Data"]["tableXml"], "lxml-xml")
        data = xmltodict.parse(str(soup))["datarow"]
        trades = set(lot["_source"]["objectHrefTerm"] for lot in data["hits"])
        for trade in trades:
            if trade not in self.previous_trades:
                yield Request(trade, self.parse_trade, cb_kwargs=kwargs, cookies=self.cookies)

    def parse_trade(self, response, **kwargs):
        if "Действия блокированы защитой ЭТП" in response.text:
            if not self.cookies_invalidated:
                logger.warning(
                    f"{response.url} | Blocked by protection, restarting playwright session"
                )
                self.invalidate_cookies()
                yield from self.update_cookies(
                    self._retry_trade,
                    after_args=[],
                    after_kwargs=dict(url=response.url, cb_kwargs=kwargs),
                )
            else:
                logger.error(f"{response.url} | Blocked again even after refresh, skipping")
            return
        self.previous_trades.append(response.url)
        combo = NewCombo(response)
        loader = EtpItemLoader(EtpItem(), response=response)
        loader.add_value("data_origin", data_origin_url)
        loader.add_value("property_type", self.property_type.value)
        loader.add_value("trading_id", combo.trading_id)
        loader.add_value("trading_link", combo.trading_link)
        loader.add_value("trading_number", combo.trading_number)
        loader.add_value("trading_type", combo.trading_type)
        loader.add_value("trading_form", combo.trading_form)
        loader.add_value("trading_org", combo.trading_org)
        loader.add_value("trading_org_inn", combo.trading_org_inn)
        loader.add_value("trading_org_contacts", combo.trading_org_contacts)
        loader.add_value("address", combo.address)
        loader.add_value("start_date_requests", combo.start_date_requests)
        loader.add_value("end_date_requests", combo.end_date_requests)
        loader.add_value(
            "files",
            {
                "general": combo.download(
                    response.request.headers[b"Cookie"].decode(),
                    self.property_type.value,
                    kwargs.get("org"),
                ),
                "lot": [],
            },
        )
        for lot in combo.get_lots():
            loader.add_value("lot_id", combo.lot_id(lot))
            loader.add_value("lot_number", combo.lot_number(lot))
            loader.add_value("short_name", combo.short_name(lot))
            loader.add_value("start_price", combo.start_price(lot))
            # loader.add_value("step_price", combo.step_price)
            yield loader.load_item()

    def _retry_trade(self, url: str, cb_kwargs: dict):
        yield Request(url, callback=self.parse_trade, cb_kwargs=cb_kwargs, dont_filter=True)


class SberbankCommercialHTMLSpider(SberbankBaseHTMLSpider):
    name = "sberbank_commercial"
    property_type = AuctionPropertyType.commercial


class SberbankFz223HTMLSpider(SberbankBaseHTMLSpider):
    name = "sberbank_fz223"
    property_type = AuctionPropertyType.fz223


class SberbankFz44HTMLSpider(SberbankBaseHTMLSpider):
    name = "sberbank_fz44"
    property_type = AuctionPropertyType.fz44
