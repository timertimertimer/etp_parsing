import json
from datetime import timedelta
from math import ceil

import pandas as pd
import xmltodict
from scrapy import FormRequest
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

    def start_requests(self):
        date_range = pd.date_range(start_date, periods=periods_, freq=format_period)
        for start_date_ in date_range:
            end_date = DateTimeHelper.format_datetime(
                start_date_ + timedelta(weeks=1), "%d.%m.%Y %H:%M"
            )
            start_date_ = start_date_.strftime("%d.%m.%Y %H:%M")
            start_url = search_query_urls[self.property_type.value]
            url = []
            xmls_prefix = []
            if isinstance(start_url, str):
                url = [start_url]
                xmls_prefix = [self.property_type.value]
            elif isinstance(start_url, dict):
                url_data = start_url[self.property_type.value]
                url = list(url_data.values())
                xmls_prefix = [
                    f"{self.property_type.value}_{el}" for el in url_data.keys()
                ]
            for u, p in zip(url, xmls_prefix):
                xml_request_data = get_xml_request_data(p)
                yield FormRequest(
                    u,
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
                        "start_url": u,
                    },
                )

    def make_second_request(self, response, **kwargs):
        soup = BS(json.loads(response.text)["data"]["Data"]["tableXml"], "lxml-xml")
        data = xmltodict.parse(str(soup))["datarow"]
        total = int(data["total"]["value"])
        logger.info(f"Total lots: {total}")
        for page in range(ceil(total / 20)):
            yield FormRequest(
                response.meta["start_url"],
                self.parse_table,
                formdata={
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
                },
                headers={
                    "x-requested-with": "XMLHttpRequest",
                },
            )
