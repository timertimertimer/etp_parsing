from typing import Iterable

from bs4 import BeautifulSoup
from scrapy import Request, FormRequest

from app.crawlers.base import BaseSpider
from app.crawlers.crawler_b2b_center.crawler_b2b_center.config import data_origin, params
from app.db.models import AuctionPropertyType
from app.utils import URL


class B2bCenterBaseSpider(BaseSpider):
    name = "b2b_center"
    allowed_domains = ["www.b2b-center.ru"]
    start_urls = ["https://www.b2b-center.ru/market/"]

    def __init__(self, **kwargs):
        super().__init__(data_origin)

    def start_requests(self) -> Iterable[Request]:
        yield FormRequest(self.start_urls[0], formdata=params, method='GET', callback=self.parse_serp)

    def login(self, respose):
        ...

    def parse_serp(self, response):
        soup = BeautifulSoup(response.text, "lxml")
        table = response.xpath(
            '//table[@class="table table-hover table-filled search-results"]//tbody/tr//a[@class="search-results-title visited"]'
        ).getall()
        for link in table:
            link = URL.url_join(data_origin, link.get('href'))
            if link not in self.previous_trades:
                yield Request(link, callback=self.parse)

        # TODO: need cookies for pagination
        current_page = soup.find('li', class_='pagi-item pagi-item-current')
        next_page = current_page.find_next('li', class_='pagi-item')
        if next_page:
            params['from'] = str(20 * int(current_page.get_text(strip=True)))
            yield FormRequest(self.start_urls[0], formdata=params, method='GET', callback=self.parse_serp)


class B2bCenterFz223Spider(B2bCenterBaseSpider):
    name = "b2b_center_fz223"
    property_type = AuctionPropertyType.fz223
