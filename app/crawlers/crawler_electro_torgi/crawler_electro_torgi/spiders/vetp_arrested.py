from scrapy import Request

from app.db.models import AuctionPropertyType
from app.utils import URL
from app.utils.config import write_log_to_file
from .base import ElectroTorgiBaseSpider


class VetpArrestSpiderElectroTorgi(ElectroTorgiBaseSpider):
    name = "vetp_arrested"
    property_type = AuctionPropertyType.arrested
    custom_settings = {
        "LOG_FILE": f"{name}.log" if write_log_to_file else None,
    }

    def parse(self, response, **kwargs):
        links = response.xpath('//p[@class="block-lot"]/@href').getall()
        for link in links:
            link = URL.url_join(self.url, link)
            if link not in self.previous_trades:
                yield Request(link, self.parse_trade)

        pagination = response.xpath('//ul[@class="pagination"]').get()
        if pagination:
            next_page_link = response.xpath('//a[@rel="next"]/@href').get()
            if next_page_link:
                yield Request(next_page_link.replace("http://", "https://"), self.parse)
