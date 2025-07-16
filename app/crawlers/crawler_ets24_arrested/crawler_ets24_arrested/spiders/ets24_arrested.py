import re

from scrapy import FormRequest, Request

from app.crawlers.base import BaseSpider
from app.crawlers.crawler_ets24_arrested.crawler_ets24_arrested.combo import Combo
from app.crawlers.crawler_ets24_arrested.crawler_ets24_arrested.config import (
    data_origin_url,
    params,
)
from app.crawlers.items import EtpItemLoader, EtpItem
from app.db.models import AuctionPropertyType, Auction



class Ets24ArrestedSpider(BaseSpider):
    name = "ets24_arrested"
    property_type = AuctionPropertyType.arrested
    start_urls = ["https://ets24.ru/index.php?class=Auction&AuctionType=Arrest&action=List&mod=Open"]

    def __init__(self):
        super(Ets24ArrestedSpider, self).__init__(data_origin_url, select_keys={Auction.ext_id})

    def parse(self, response):
        params['form'] = response.xpath('//input[@class="form-button"]/@onclick').get().split('form=')[1].split('&')[0]
        params['PresentStartDateMin'] = '01.07.2023'
        yield FormRequest(
            'https://ets24.ru/index.php', formdata=params, callback=self.parse_serp, method='GET'
        )

    def parse_serp(self, response, current_page: int = 1):
        combo = Combo(response)
        lots = combo.get_lots()
        for lot in lots:
            if lot.split('OID=')[1] not in self.previous_trades:
                yield Request(lot, callback=self.parse_trade)
        next_page = response.xpath('//div[@id="page-divide"]//li').getall()
        if next_page:
            next_page = next_page[-1]
            match = re.search(r"[?;]page=(\d+)", next_page)
            if match:
                next_page = match.group(1)
                if int(next_page) > current_page:
                    params['page'] = next_page
                    yield FormRequest(
                        "https://ets24.ru/index.php", formdata=params, callback=self.parse_serp, method='GET'
                    )
        
    def parse_trade(self, response):
        combo = Combo(response)
        loader = EtpItemLoader(EtpItem(), response=response)
        loader.add_value("data_origin", data_origin_url)
        loader.add_value("property_type", self.property_type)
        loader.add_value("trading_id", combo.trading_id)
        loader.add_value("trading_link", response.url)
        loader.add_value("trading_number", combo.trading_number)
        loader.add_value("trading_type", combo.trading_type)
        loader.add_value("trading_form", combo.trading_form)
        loader.add_value("trading_org", combo.trading_org)
        loader.add_value("trading_org_contacts", combo.trading_org_contacts)
        loader.add_value("case_number", combo.case_number)
        loader.add_value("debtor_inn", combo.debtor_inn)
        loader.add_value("address", combo.address)
        loader.add_value("arbit_manager", combo.arbit_manager)
        loader.add_value("arbit_manager_inn", combo.arbit_manager_inn)
        loader.add_value("arbit_manager_org", combo.arbit_manager_org)
        loader.add_value("status", combo.status)
        loader.add_value("lot_id", combo.lot_id)
        loader.add_value("lot_link", combo.lot_link)
        loader.add_value("lot_number", combo.lot_number)
        loader.add_value("short_name", combo.short_name)
        loader.add_value("lot_info", combo.lot_info)
        loader.add_value("property_information", combo.property_information)
        loader.add_value("start_date_requests", combo.start_date_requests)
        loader.add_value("end_date_requests", combo.end_date_requests)
        loader.add_value("start_date_trading", combo.start_date_trading)
        loader.add_value("end_date_trading", combo.end_date_trading)
        loader.add_value("start_price", combo.start_price)
        loader.add_value("step_price", combo.step_price)
        loader.add_value("periods", combo.periods)
        loader.add_value("categories", None)
        loader.add_value(
            "files", {"general": combo.download_general(), "lot": combo.download_lot()}
        )
        yield loader.load_item()