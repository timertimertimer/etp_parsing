import scrapy


class TenderstandartruCompetitionSpider(scrapy.Spider):
    name = 'tenderstandartru_competition'
    allowed_domains = ['tenderstandart.ru']
    start_urls = ['http://tenderstandart.ru/']

    def parse(self, response):
        pass
