import scrapy


class BaseSpider(scrapy.Spider):
    name = "base"
    allowed_domains = ["tender.lot-online.ru"]
    start_urls = ["https://tender.lot-online.ru/search"]

    def parse(self, response):
        pass
