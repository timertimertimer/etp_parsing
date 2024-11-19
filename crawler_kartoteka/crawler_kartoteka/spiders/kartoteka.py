import json
from typing import Iterable

import scrapy
from scrapy import Request, FormRequest
from scrapy_splash import SplashRequest, SlotPolicy

from ..locators.serp_locator import SerpLocator
from ..settings import DEFAULT_REQUESTS_HEADERS
from ..trades.app import Combo
from ..utils.config import format_parse_date, time_delta, trash_resources, data_origin_url
from ..utils.data_for_requests import script_lua
from ..utils.get_data_from_table import DbConnectCheckLots
from ..utils.post_data import form_data
from ..utils.working_with_url import UrlConfig


class KartotekaSpider(scrapy.Spider):
    name = "kartoteka"
    start_urls = ["https://www.kartoteka.ru/bankruptcy2/"]
    custom_settings = {
        'PLAYWRIGHT_ABORT_REQUEST': lambda request: request.resource_type in trash_resources
    }

    def __init__(self):
        super(KartotekaSpider, self).__init__()
        self.db_check = DbConnectCheckLots()
        self.previous_lots = self.db_check.get_latest_lot()
        self.url = UrlConfig()
        self.loc = SerpLocator

    def start_requests(self):
        for url in self.start_urls:
            yield Request(url, callback=self.get_validate_data, meta=dict(
                playwright=True,
            ))

    def get_validate_data(self, response) -> Iterable[Request]:
        validate_data = response.xpath('//input[@name="validate"]/@value').get()
        data_trade_begin = format_parse_date(time_delta)
        form_data['data-trade-begin'] = data_trade_begin
        form_data['validate'] = validate_data
        yield FormRequest(
            f'{self.start_urls[0]}/?action=Hash', self.get_hash, method='POST', formdata=form_data,
            headers={'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8'}
        )

    def get_hash(self, response):
        hash = json.loads(response.text)['hash']
        yield Request(f'{self.start_urls[0]}{hash}', self.parse_serp)

    def parse_serp(self, response):
        links_to_trade = response.xpath(self.loc.link_to_trade_loc).getall()
        for link in links_to_trade:
            link = self.url.url_join(data_origin_url, link)
            yield Request(link, self.parse_trade)
        pagination = response.xpath(self.loc.pagination_loc).get()
        if pagination:
            next_page = response.xpath(self.loc.next_page_loc).get()
            if next_page:
                form_data['page'] = next_page
                yield FormRequest(
                    f'{self.start_urls[0]}/?action=Hash', self.get_hash, method='POST', formdata=form_data,
                    headers={'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8'}
                )

    def parse_trade(self, response):
        combo = Combo(response)
        trading_type, trading_form = combo.trading_type_and_form