import scrapy
from scrapy import FormRequest, Request

from ..app import Combo
from ..config import formdata, search_link, data_origin
from general_utils import DBHelper, UrlConfig


class RoseltorgSpider(scrapy.Spider):
    name = "roseltorg"
    start_urls = [search_link]
    unique_links = set()

    def __init__(self):
        super(RoseltorgSpider).__init__()
        self.db_check = DBHelper(f'lots_{self.name}')
        self.previous_lots = self.db_check.get_latest_lot()

    def start_requests(self):
        yield FormRequest(self.start_urls[0], self.parse_serp, formdata=formdata, method='GET')

    def parse_serp(self, response):
        combo = Combo(response)
        for link in combo.get_trade_links():
            if (link,) not in self.previous_lots:
                self.unique_links.add(link)
        if next_page := combo.get_next_page_link():
            yield Request(next_page, self.parse_serp)
        else:
            for link in self.unique_links:
                yield Request(UrlConfig.url_join(data_origin, link), self.parse_trade)

    def parse_trade(self, response):
        combo = Combo(response)
