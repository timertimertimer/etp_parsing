from scrapy import FormRequest, Request

from general_utils.base_spider import BaseSpider
from ..app import Combo
from ..config import formdata, search_link, data_origin
from general_utils import UrlConfig


class RoseltorgSpider(BaseSpider):
    name = "roseltorg"
    start_urls = [search_link]
    unique_links = set()

    def __init__(self):
        super().__init__(data_origin)

    def start_requests(self):
        yield FormRequest(self.start_urls[0], self.parse_serp, formdata=formdata, method='GET')

    def parse_serp(self, response):
        combo = Combo(response)
        for link in combo.get_trade_links():
            if link not in self.previous_trades:
                self.unique_links.add(link)
        if next_page := combo.get_next_page_link():
            yield Request(next_page, self.parse_serp)
        else:
            for link in self.unique_links:
                yield Request(UrlConfig.url_join(data_origin, link), self.parse_trade)

    def parse_trade(self, response):
        combo = Combo(response)
