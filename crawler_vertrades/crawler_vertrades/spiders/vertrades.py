from typing import Iterable

import scrapy
from scrapy import Request, FormRequest

from ..utils.config import format_parse_date, start_time_from
from ..utils.params_data import params_data
from ..trades.app import Combo


class VertradesSpider(scrapy.Spider):
    name = "vertrades"
    allowed_domains = ["bankrot.vertrades.ru"]
    start_urls = ["https://bankrot.vertrades.ru/bidding"]

    def start_requests(self) -> Iterable[Request]:
        params_data['from'] = start_time_from
        yield FormRequest(self.start_urls[0], callback=self.parse, formdata=params_data, method='GET')

    def parse(self, response):
        combo = Combo(response)
        for link in combo.serp.get_trading_links():
            yield response.follow(link, callback=self.parse_trading)

    def parse_trading(self, response):

        ...
