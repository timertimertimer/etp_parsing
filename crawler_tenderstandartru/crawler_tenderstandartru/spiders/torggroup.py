import scrapy


class TorggroupSpider(scrapy.Spider):
    name = "torggroup"
    allowed_domains = ["bankrot.torggroup.org"]
    start_urls = ["https://bankrot.torggroup.org/"]

    def parse(self, response):
        pass
