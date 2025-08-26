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
        loader.add_value("trading_org_contacts", combo.trading_org_contacts)
        loader.add_value("address", combo.address)
        loader.add_value("status", combo.status)
        loader.add_value("categories", combo.categories(lot))
        loader.add_value("lot_id", combo.lot_id)
        loader.add_value("lot_link", combo.lot_link)
        loader.add_value("lot_number", i + 1)
        loader.add_value("short_name", combo.short_name)
        loader.add_value("lot_info", combo.lot_info)
        loader.add_value("property_information", combo.property_information)
        loader.add_value("start_date_requests", combo.start_date_requests(lot))
        loader.add_value("end_date_requests", combo.end_date_requests(lot))
        loader.add_value("start_date_trading", combo.start_date_trading(lot))
        loader.add_value("end_date_trading", combo.end_date_trading)
        loader.add_value("start_price", combo.start_price(lot))
        loader.add_value("step_price", combo.step_price(lot))
        loader.add_value("periods", combo.periods)
        loader.add_value(
            "files",
            {"general": combo.download_general(), "lot": combo.download_lot(lot)},
        )
        # TODO: ИНН парсится на отдельной страницы организации, контактные данные на лоте
        trading_org_data = combo.get_trading_org_data()
        if trading_org_data:
            trading_org_link = trading_org_data.find_next('span').find('a').get('href')
            yield Request(
                url=URL.url_join(data_origin, trading_org_link),
                callback=self.get_trading_org_info,
                cb_kwargs={'loader': loader}
            )

    def get_trading_org_info(self, response, loader):
        combo = Combo(response=response)
        loader.add_value("trading_org_inn", combo.trading_org_inn)
        yield loader.load_item()


class ZakupkigovFz44Spider(ZakupkigovBaseSpider):
    name = "zakupkigov_fz44"
    property_type = AuctionPropertyType.fz44


class ZakupkigovCapitalRepairSpider(ZakupkigovBaseSpider):
    name = "zakupkigov_capital_repair"
    property_type = AuctionPropertyType.capital_repair
