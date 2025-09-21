from bs4 import BeautifulSoup
from scrapy import Request, FormRequest

from app.crawlers.base import BaseSpider
from app.crawlers.crawler_b2b_center.crawler_b2b_center.combo import Combo
from app.crawlers.crawler_b2b_center.crawler_b2b_center.config import data_origin, params, login_url, login_data
from app.crawlers.items import EtpItemLoader, EtpItem
from app.db.models import AuctionPropertyType, Auction
from app.utils import logger, URL


class B2bCenterBaseSpider(BaseSpider):
    name = "b2b_center"
    start_urls = ["https://www.b2b-center.ru/market/"]

    def __init__(self, **kwargs):
        super().__init__(data_origin, select_keys={Auction.ext_id})

    def start_requests(self):
        yield Request(self.start_urls[0], self.login)

    def login(self, response):
        yield FormRequest(
            login_url, formdata=login_data, callback=self.after_login,
            headers={
                'X-Requested-With': 'XMLHttpRequest'
            }
        )

    def after_login(self, response):
        yield FormRequest(self.start_urls[0], formdata=params, method='GET', callback=self.parse_serp)

    def parse_serp(self, response):
        logger.info(response.url)
        soup = BeautifulSoup(response.text, "lxml")
        links = response.xpath(
            '//table[@class="table table-hover table-filled search-results"]//tbody/tr//a[@class="search-results-title visited"]/@href'
        ).getall()
        for link in links:
            id_ = int(link.split('?id=')[1].split('#')[0])
            if id_ not in self.previous_trades:
                self.previous_trades.append(id_)
                link = f'https://www.b2b-center.ru/market/view.html?id={id_}'
                yield Request(link, callback=self.parse_trade)

        current_page = soup.find('li', class_='pagi-item pagi-item-current')
        next_page = current_page.find_next('li', class_='pagi-item')
        if next_page:
            params['from'] = str(20 * int(current_page.get_text(strip=True)))
            yield FormRequest(self.start_urls[0], formdata=params, method='GET', callback=self.parse_serp)

    def parse_trade(self, response):
        combo = Combo(response)
        loader = EtpItemLoader(EtpItem(), response=response)
        loader.add_value('data_origin', data_origin)
        loader.add_value('property_type', self.property_type.value)
        loader.add_value("trading_id", combo.trading_id)
        loader.add_value("trading_link", combo.trading_link)
        loader.add_value("trading_number", combo.trading_number)  # trading_id
        loader.add_value("trading_type", combo.trading_type)
        loader.add_value("trading_form", combo.trading_form)
        loader.add_value("trading_org", combo.trading_org)
        loader.add_value("trading_org_contacts", combo.trading_org_contacts)
        loader.add_value("address", combo.address)
        loader.add_value("status", 'active')
        loader.add_value("lot_number", '1')
        loader.add_value("short_name", combo.short_name)
        loader.add_value("lot_info", combo.lot_info)
        loader.add_value("categories", combo.categories)
        loader.add_value("property_information", combo.property_information)
        loader.add_value("start_date_requests", combo.start_date_requests)
        loader.add_value("end_date_requests", combo.end_date_requests)
        loader.add_value("start_date_trading", combo.start_date_trading)
        loader.add_value("end_date_trading", combo.end_date_trading)
        loader.add_value("start_price", combo.start_price)
        if combo.trading_type in ["auction", "competition"]:
            loader.add_value("step_price", combo.step_price)
        else:
            loader.add_value("periods", combo.periods)
        loader.add_value(
            "files",
            {"general": combo.download_general(), "lot": combo.download_lot()},
        )
        yield loader.load_item()
        # if trading_org_link := combo.get_trading_org_td().find('a').get('href'):
        #     yield Request(
        #         URL.url_join(data_origin, trading_org_link),
        #         callback=self.get_organizer_inn,
        #         cb_kwargs={'loader': loader},
        #     )

    def get_organizer_inn(self, response, loader):
        combo = Combo(response)
        loader.add_value("trading_org_inn", combo.trading_org_inn)
        yield loader.load_item()


class B2bCenterFz223Spider(B2bCenterBaseSpider):
    name = "b2b_center_fz223"
    property_type = AuctionPropertyType.fz223
