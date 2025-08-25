import scrapy
from scrapy import FormRequest, Request

from app.crawlers.base import BaseSpider
from app.crawlers.crawler_zakupkigov.crawler_zakupkigov.combo import Combo
from app.crawlers.crawler_zakupkigov.crawler_zakupkigov.config import search_link, formdata, data_origin
from app.crawlers.items import EtpItemLoader, EtpItem
from app.db.models import AuctionPropertyType
from app.utils import URL


class ZakupkigovBaseSpider(BaseSpider):
    name = "zakupkigov"

    def __init__(self):
        super().__init__(data_origin)
        self.unique_links = set()

    def start_requests(self):
        yield FormRequest(
            url=search_link,
            formdata=formdata[self.property_type.value],
            method='GET',
            callback=self.parse_serp,
        )

    def parse_serp(self, response):
        links = set(response.xpath('//div[@class="registry-entry__header-mid__number"]//a/@href').getall())
        self.unique_links.update(links)
        for link in links:
            link = URL.url_join(data_origin, link)
            if link not in self.previous_trades:
                yield Request(url=link, callback=self.parse_trade)
        if next_page := response.xpath(
                '//a[@class="paginator-button paginator-button-next"]'
        ):
            next_page_number = next_page.attrib['data-pagenumber']
            formdata[self.property_type.value]['pageNumber'] = str(next_page_number)
            yield FormRequest(
                url=search_link,
                formdata=formdata[self.property_type.value],
                method='GET',
                callback=self.parse_serp,
            )

    def parse_trade(self, response):
        combo = Combo(response=response)
        loader = EtpItemLoader(EtpItem(), response=response)
        loader.add_value("data_origin", data_origin)
        loader.add_value("property_type", self.property_type.value)
        loader.add_value("trading_id", combo.trading_id)
        loader.add_value("trading_link", response.url)
        loader.add_value("trading_number", combo.trading_number)
        loader.add_value("trading_type", combo.trading_type)
        loader.add_value("trading_form", combo.trading_form)
        loader.add_value("trading_org", combo.trading_org)
        # TODO: ИНН парсится на отдельной страницы организации, контактные данные на лоте
        loader.add_value("trading_org_inn", combo.trading_org_inn)
        loader.add_value("trading_org_contacts", combo.trading_org_contacts)

        # yield loader.load_item()

    def get_trading_org_info(self):
        ...


class ZakupkigovFz44Spider(ZakupkigovBaseSpider):
    name = "zakupkigov_fz44"
    property_type = AuctionPropertyType.fz44


class ZakupkigovCapitalRepairSpider(ZakupkigovBaseSpider):
    name = "zakupkigov_capital_repair"
    property_type = AuctionPropertyType.capital_repair
