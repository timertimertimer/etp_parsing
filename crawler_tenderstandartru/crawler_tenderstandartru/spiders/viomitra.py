import scrapy


class ViomitraSpider(scrapy.Spider):
    name = "viomitra"
    allowed_domains = ["bankrot.viomitra.ru"]
    start_urls = ["https://bankrot.viomitra.ru/"]

    def parse(self, response):
        pass
