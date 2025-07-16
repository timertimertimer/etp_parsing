import json

from scrapy import FormRequest

from app.crawlers.base import BaseSpider
from app.crawlers.crawler_sitesoft.crawler_sitesoft.config import (
    data_origin,
    urls,
    types,
)
from app.utils import URL
from app.utils.config import start_date


class SitesoftBaseSpider(BaseSpider):
    name = "base"

    def __init__(self):
        self.start_urls = [URL.url_join(urls[self.name], "/searchServlet")]
        super().__init__(data_origin[self.name])

    def start_requests(self):
        yield FormRequest(
            method="GET",
            url=self.start_urls[0],
            formdata={
                "query": json.dumps({"types": types[self.property_type.value]}),
                "filter": json.dumps({"state": ["ALL"]}),
                "sort": json.dumps({"placementDate": {"min": start_date}}),
                "limit": json.dumps(
                    {"min": "0", "max": "20", "updateTotalCount": "true"}
                ),
            },
            callback=self.parse,
        )

    def parse(self, response, parsed_all: bool = False):
        data = json.loads(response.text)
        if data["totalCount"] > 20 and not parsed_all:
            yield FormRequest(
                method="GET",
                url=self.start_urls[0],
                formdata={
                    "query": json.dumps({"types": types[self.property_type.value]}),
                    "filter": json.dumps({"state": ["ALL"]}),
                    "sort": json.dumps({"placementDate": {"min": start_date}}),
                    "limit": json.dumps(
                        {
                            "min": "0",
                            "max": data["totalCount"],
                            "updateTotalCount": "true",
                        }
                    ),
                },
                callback=self.parse,
                cb_kwargs={"parsed_all": True},
            )
        else:
            ...
        
