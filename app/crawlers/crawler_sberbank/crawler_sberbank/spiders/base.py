import json
from datetime import timedelta
from math import ceil
from typing import Callable

import pandas as pd
import xmltodict
from scrapy import Request, FormRequest
from scrapy_playwright.page import PageMethod
from bs4 import BeautifulSoup as BS

from app.crawlers.base import BaseSpider
from app.crawlers.crawler_sberbank.crawler_sberbank.utils.config import (
    data_origin_url,
    start_date,
    periods_,
    format_period,
    search_query_urls,
    get_xml_request_data,
)
from app.utils import DateTimeHelper, logger


class SberbankBaseSpider(BaseSpider):
    name = "base"

    def __init__(self):
        super().__init__(data_origin_url)
        self.cookies = {}
        self.failed_trades = []

    def start_requests(self):
        date_range = pd.date_range(start_date, periods=periods_, freq=format_period)
        for start_date_ in date_range:
            end_date = DateTimeHelper.format_datetime(
                start_date_ + timedelta(weeks=1), "%d.%m.%Y %H:%M"
            )
            start_date_ = start_date_.strftime("%d.%m.%Y %H:%M")
            start_url = search_query_urls[self.property_type.value]
            if isinstance(start_url, str):
                start_url = {"": start_url}
            for property_type, url in start_url.items():
                xml_prefix_name = (
                    f"{self.property_type.value}_{property_type}"
                    if property_type
                    else self.property_type.value
                )
                xml_request_data = get_xml_request_data(xml_prefix_name)
                yield FormRequest(
                    url,
                    self.make_second_request,
                    formdata={
                        "xmlData": xml_request_data.format(
                            start_date=start_date_,
                            end_date=end_date,
                            total=100,
                            from_=0,
                        ),
                        "orgId": "0",
                        "buId": "0",
                        "personId": "0",
                        "buMainId": "0",
                        "personMainId": "0",
                    },
                    meta={
                        "start_date": start_date_,
                        "end_date": end_date,
                        "xml_request_data": xml_request_data,
                        "start_url": url,
                    },
                    cb_kwargs={'org': property_type},
                    cookies=self.cookies,
                )

    def make_second_request(self, response, **kwargs):
        soup = BS(json.loads(response.text)["data"]["Data"]["tableXml"], "lxml-xml")
        data = xmltodict.parse(str(soup))["datarow"]
        total = int(data["total"]["value"])
        logger.info(f"Total lots: {total}")
        for page in range(ceil(total / 20)):
            request_formdata = {
                    "xmlData": response.meta["xml_request_data"].format(
                        start_date=response.meta["start_date"],
                        end_date=response.meta["end_date"],
                        total=20,
                        from_=page * 20,
                    ),
                    "orgId": "0",
                    "buId": "0",
                    "personId": "0",
                    "buMainId": "0",
                    "personMainId": "0",
                }
            kwargs.update({'request_formdata': request_formdata})
            yield FormRequest(
                response.meta["start_url"],
                self.parse_table,
                formdata=request_formdata,
                headers={
                    "x-requested-with": "XMLHttpRequest",
                },
                cb_kwargs=kwargs,
                cookies=self.cookies
            )

    def update_cookies(
        self,
        after_func: Callable = None,
        after_args: list = None,
        after_kwargs: dict = None,
    ):
        url = data_origin_url
        yield Request(
            url,
            callback=self.after_update_cookies,
            meta=dict(
                playwright=True,
                playwright_include_page=True,
                playwright_page_methods=[PageMethod("goto", url)],
                playwright_context="cookie_refresh",
                playwright_context_close=True,
                playwright_page_close=True,
                after_func=after_func,
                after_args=after_args or [],
                after_kwargs=after_kwargs or {},
            ),
        )

    async def after_update_cookies(
        self, response
    ):
        page = response.meta["playwright_page"]
        cookies = await page.context.cookies()
        self.cookies = {c["name"]: c["value"] for c in cookies}
        await page.context.browser.close()
        logger.info("New cookies received")
        self.cookies_invalidated = False
        self.cookies_updating = False

        for request, kwargs in list(self.failed_trades):
            if request.method == "POST":
                yield FormRequest(
                    url=request.url,
                    body=request.body,
                    callback=self.parse_table,
                    headers={
                        "x-requested-with": "XMLHttpRequest",
                    },
                    cb_kwargs=kwargs,
                    cookies=self.cookies,
                    dont_filter=True,
                )
            else:
                yield Request(
                    request.url,
                    callback=self.parse_trade,
                    cb_kwargs=kwargs,
                    cookies=self.cookies,
                    dont_filter=True,
                )
        self.failed_trades.clear()

        func = response.meta.get("after_func")
        if func:
            for req in func(
                *response.meta.get("after_args", []),
                **response.meta.get("after_kwargs", {}),
            ):
                yield req
