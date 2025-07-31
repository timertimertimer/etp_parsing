import json
from urllib.parse import urlencode

from scrapy import FormRequest, Request

from app.crawlers.base import BaseSpider
from app.crawlers.crawler_ei.crawler_ei.config import data_origin, params, types
from app.db.models import AuctionPropertyType


class EiBaseSpider(BaseSpider):
    name = "base"
    start_urls = ['https://api.ei.ru/v1/lot/index']

    def __init__(self):
        super().__init__(data_origin)

    def start_requests(self):
        params["filter[type][]"] = types[self.property_type.value]
        for i in range(1, 51):
            params['page'] = i
            query_string = urlencode(params, doseq=True)
            url = f"{self.start_urls[0]}?{query_string}"
            yield Request(
                url=url,
                method="GET",
                headers={"Accept": "application/json, text/plain, */*"},
                callback=self.parse_serp,
            )

    def parse_serp(self, response):
        data = json.loads(response.text)
        for lot in data:
            pass

class EiBankruptcySpider(EiBaseSpider):
    name = "ei_bankruptcy"
    property_type = AuctionPropertyType.bankruptcy

class EiArrestedSpider(EiBaseSpider):
    name = "ei_arrested"
    property_type = AuctionPropertyType.arrested

class EiCommercialSpider(EiBaseSpider):
    name = "ei_commercial"
    property_type = AuctionPropertyType.commercial
