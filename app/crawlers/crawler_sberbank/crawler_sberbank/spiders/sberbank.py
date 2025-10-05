import json
from asyncio import Lock
from pprint import pprint

from typing import Callable

import xmltodict
from scrapy import Request, FormRequest
from scrapy_playwright.page import PageMethod
from playwright.async_api import Page
from playwright._impl._errors import TimeoutError as PlaywrightTimeoutError
from bs4 import BeautifulSoup as BS

from app.crawlers.crawler_sberbank.crawler_sberbank.spiders.base import (
    SberbankBaseSpider,
)
from app.crawlers.crawler_sberbank.crawler_sberbank.trades.html_combo import NewCombo
from app.crawlers.crawler_sberbank.crawler_sberbank.utils.config import (
    data_origin_url,
)
from app.crawlers.crawler_sberbank.crawler_sberbank.utils.request import (
    Request as SavedRequest,
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
        # "PLAYWRIGHT_LAUNCH_OPTIONS": {"headless": False},
    }
    cookies_invalidated = False
    cookies_updating = False

    def start_requests(self, cookies: dict = None):
        yield from self.update_cookies(super().start_requests)

    def parse_table(self, response, **kwargs):
        if "Действия блокированы защитой ЭТП" in response.text:
            if not self.cookies_invalidated:
                logger.warning(f"{response.url} | Blocked, scheduling cookie refresh")
                self.cookies_invalidated = True
                if not self.cookies_updating:
                    self.cookies_updating = True
                    yield from self.update_cookies()
            else:
                self.failed_trades.append(
                    (
                        SavedRequest(
                            method="POST",
                            url=response.url,
                            body=response.request.content,
                        ),
                        kwargs,
                    )
                )
            return
        soup = BS(json.loads(response.text)["data"]["Data"]["tableXml"], "lxml-xml")
        data = xmltodict.parse(str(soup))["datarow"]
        trades = set(lot["_source"]["objectHrefTerm"] for lot in data["hits"])
        for trade in trades:
            if trade not in self.previous_trades:
                yield Request(
                    trade, self.parse_trade, cb_kwargs=kwargs, cookies=self.cookies
                )

    def parse_trade(self, response, **kwargs):
        if (
            "Действия блокированы защитой ЭТП" in response.text
            or "Слишком частые обращения к страницам сайта." in response.text
        ):
            if not self.cookies_invalidated:
                logger.warning(f"{response.url} | Blocked, scheduling cookie refresh")
                self.cookies_invalidated = True
                if not self.cookies_updating:
                    self.cookies_updating = True
                    yield from self.update_cookies()
            else:
                self.failed_trades.append((SavedRequest(url=response.url), kwargs))
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


class SberbankCommercialHTMLSpider(SberbankBaseHTMLSpider):
    name = "sberbank_commercial"
    property_type = AuctionPropertyType.commercial
    custom_settings = {
        "LOG_FILE": f"{name}.log" if write_log_to_file else None,
        "PLAYWRIGHT_ABORT_REQUEST": lambda request: request.resource_type
                                                    in trash_resources,
        # "PLAYWRIGHT_LAUNCH_OPTIONS": {"headless": False},
    }


class SberbankFz223HTMLSpider(SberbankBaseHTMLSpider):
    name = "sberbank_fz223"
    property_type = AuctionPropertyType.fz223
    custom_settings = {
        "LOG_FILE": f"{name}.log" if write_log_to_file else None,
        "PLAYWRIGHT_ABORT_REQUEST": lambda request: request.resource_type
                                                    in trash_resources,
        # "PLAYWRIGHT_LAUNCH_OPTIONS": {"headless": False},
    }


class SberbankFz44HTMLSpider(SberbankBaseHTMLSpider):
    name = "sberbank_fz44"
    property_type = AuctionPropertyType.fz44
    custom_settings = {
        "LOG_FILE": f"{name}.log" if write_log_to_file else None,
        "PLAYWRIGHT_ABORT_REQUEST": lambda request: request.resource_type
                                                    in trash_resources,
        # "PLAYWRIGHT_LAUNCH_OPTIONS": {"headless": False},
    }
