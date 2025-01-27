import asyncio
import logging
import re
from typing import Iterable

import scrapy
from playwright.async_api import Page
from scrapy import Request
from scrapy.spidermiddlewares.httperror import HttpError
from scrapy_playwright.page import PageMethod
from bs4 import BeautifulSoup as BS
from twisted.internet.error import DNSLookupError, TCPTimedOutError

from general_utils import CrawlerBankruptItem, CrawlerBankruptItemLoader
from general_utils.config import trash_resources, start_date
from ..trades.combo import ComposeTrades
from ..utils.manage_spider import sort_trading_type, get_trading_form
from ..utils.working_with_time import return_parse_date
from ..locators.serp_locator import SerpLocator
from ..utils.get_data_from_table import DbConnectCheckLots
from ..utils.working_with_url import UrlConfig
from ..utils.config import data_origin_url, start_date


async def filter_lots(page: Page) -> str:
    await page.route("**/*", lambda route,
                                    request: route.abort() if request.resource_type in trash_resources else route.continue_())
    is_bankr_selector = 'input[name="isbankr"]'
    await page.wait_for_selector(selector=is_bankr_selector, state="attached")
    await page.evaluate("document.querySelector('input[name=\"isbankr\"]').click()")
    await asyncio.sleep(0.5)
    await page.evaluate("document.querySelector('input[name=\"isauk\"]').click()")
    await asyncio.sleep(0.5)
    await page.evaluate("document.querySelector('input[name=\"ispub\"]').click()")
    await asyncio.sleep(0.5)
    await page.evaluate(f"document.querySelector('input[name=\"date_nach_ot\"]').value = '{start_date}'")
    await asyncio.sleep(0.5)
    await page.click('.search-submit')
    await asyncio.sleep(5)
    return page.url


logger = logging.getLogger(__name__)


class MetsSpider(scrapy.Spider):
    name = 'mets'
    start_urls = ['https://m-ets.ru/search']
    custom_settings = {
        'PLAYWRIGHT_ABORT_REQUEST': lambda request: request.resource_type in trash_resources
    }

    def __init__(self, name=None, **kwargs):
        super().__init__(name, **kwargs)
        self.loc = SerpLocator
        self.url = UrlConfig()
        self.db_check = DbConnectCheckLots()
        self.previous_lots = self.db_check.get_latest_lot()
        self.formatted_url = ''

    def start_requests(self) -> Iterable[Request]:
        for url in self.start_urls:
            yield Request(url, callback=self.parse, meta=dict(
                playwright=True,
                playwright_page_methods=[PageMethod("goto", url), PageMethod(filter_lots)]
            ))

    def parse(self, response: scrapy.http.Response, **kwargs) -> Iterable[Request]:
        self.formatted_url = self.formatted_url or response.url
        current_page = response.meta.get('current_page', 1)
        # amount_page = int(response.xpath(self.loc.count_pagination_loc).get() or current_page)
        amount_page = 5
        links_to_lots = response.xpath(self.loc.link_to_trade_loc).getall()
        trade_links = response.meta.get('trade_links', set())
        for link in links_to_lots:
            trade_links.add('-'.join(link.split('-')[:-1]) + '-1')
        if amount_page > 1 and int(current_page) < amount_page:
            current_page = int(current_page) + 1
            yield Request(
                self.formatted_url + f'&page={current_page}', callback=self.parse, dont_filter=True,
                meta={"current_page": current_page, "trade_links": trade_links}
            )
        else:
            for link in trade_links:
                yield Request(self.url.parse_url(link), callback=self.sort_trades, errback=self.errback_httpbin)

    def sort_trades(self, response):
        comp = ComposeTrades(response_=response)
        trading_type_ = comp.offer.trading_type
        trading_type = sort_trading_type(trading_type_)
        trading_form = get_trading_form(trading_type_)
        match trading_type:
            case 'auction':
                return self.parse_auction(response=response, trading_type=trading_type, trading_form=trading_form)
            case 'competition':
                return self.parse_auction(response=response, trading_type=trading_type, trading_form=trading_form)
            case 'offer':
                return self.parse_offer(response=response, trading_type=trading_type, trading_form=trading_form)
            case _:
                pass

    def parse_auction(self, response, trading_type, trading_form):
        """getting data from trade - auction"""
        comp = ComposeTrades(response_=response)
        files_general = comp.offer.download_general_files(comp.offer.trading_id)
        property_info = comp.offer.property_info
        status = comp.offer.status
        for lot in comp.offer.count_lots:
            loader = CrawlerBankruptItemLoader(CrawlerBankruptItem(), response=response)
            loader.add_value('data_origin', comp.offer.data_origin)
            loader.add_value('trading_id', comp.offer.trading_id)
            loader.add_value('trading_link', comp.offer.trading_link)
            loader.add_value('trading_number', comp.offer.trading_number)
            loader.add_value('trading_type', trading_type)
            loader.add_value('trading_form', trading_form)
            trading_number = loader.get_collected_values('trading_number')
            loader.add_value('trading_org', comp.offer.trading_org)
            loader.add_value('trading_org_inn', comp.offer.trading_org_inn)
            loader.add_value('trading_org_contacts', comp.offer.trading_org_contacts)
            loader.add_value('msg_number', comp.offer.msg_number)
            loader.add_value('case_number', comp.offer.case_number)
            loader.add_value('debtor_inn', comp.offer.debitor_inn)
            loader.add_value('arbit_manager', comp.offer.arbitr_manager_org)
            loader.add_value('arbit_manager_inn', comp.offer.arbitr_inn)
            loader.add_value('arbit_manager_org', comp.offer.arbitr_org)
            # PARSE LOT
            lot_number = comp.offer.lot_number(lot)
            loader.add_value('status', status)
            loader.add_value('lot_link', comp.offer.lot_link(lot_number))
            if (response.url, lot_number) not in self.previous_lots:
                loader.add_value('lot_number', lot_number)
                loader.add_value('short_name', comp.offer.short_name(lot_number))
                loader.add_value('lot_info', comp.offer.lot_info(lot_number))
                address, region = comp.offer.get_address() or (None, None)
                loader.add_value('address', address)
                loader.add_value('region', region)
                loader.add_value('property_information', property_info)
                loader.add_value('start_price', comp.offer.start_price(lot_number))
                loader.add_value('step_price', comp.auc.step_price(trading_number, lot_number))
                loader.add_value('start_date_requests', comp.auc.start_date_request)
                loader.add_value('end_date_requests', comp.auc.end_date_request)
                loader.add_value('start_date_trading', comp.auc.start_date_trading)
                loader.add_value('end_date_trading', comp.auc.end_date_trading)
                loader.add_value('periods', None)
                files_lot = comp.offer.download_lot_files(comp.offer.trading_id, lot_number)
                loader.add_value('files', {'general': files_general, 'lot': files_lot})
                loader.add_value('created_at', return_parse_date())
                yield loader.load_item()

    def parse_offer(self, response, trading_type, trading_form):
        """getting data from trade - offer"""
        comp = ComposeTrades(response_=response)
        files_general = comp.offer.download_general_files(comp.offer.trading_id)
        property_info = comp.offer.property_info
        status = comp.offer.status
        for lot in comp.offer.count_lots:
            loader = CrawlerBankruptItemLoader(CrawlerBankruptItem(), response=response)
            loader.add_value('data_origin', comp.offer.data_origin)
            loader.add_value('trading_id', comp.offer.trading_id)
            loader.add_value('trading_link', comp.offer.trading_link)
            loader.add_value('trading_number', comp.offer.trading_number)
            loader.add_value('trading_type', trading_type)
            loader.add_value('trading_form', trading_form)
            loader.add_value('trading_org', comp.offer.trading_org)
            loader.add_value('trading_org_inn', comp.offer.trading_org_inn)
            loader.add_value('trading_org_contacts', comp.offer.trading_org_contacts)
            loader.add_value('msg_number', comp.offer.msg_number)
            loader.add_value('case_number', comp.offer.case_number)
            loader.add_value('debtor_inn', comp.offer.debitor_inn)
            loader.add_value('arbit_manager', comp.offer.arbitr_manager_org)
            loader.add_value('arbit_manager_inn', comp.offer.arbitr_inn)
            loader.add_value('arbit_manager_org', comp.offer.arbitr_org)
            # PARSE LOT
            lot_number = comp.offer.lot_number(lot)
            loader.add_value('status', status)
            loader.add_value('lot_link', comp.offer.lot_link(lot_number))
            if (comp.offer.trading_link, lot_number) not in self.previous_lots:
                loader.add_value('lot_number', lot_number)
                loader.add_value('short_name', comp.offer.short_name(lot_number))
                loader.add_value('lot_info', comp.offer.lot_info(lot_number))
                address, region = comp.offer.get_address() or (None, None)
                loader.add_value('address', address)
                loader.add_value('region', region)
                loader.add_value('property_information', property_info)
                loader.add_value('start_price', comp.offer.start_price(lot_number))
                loader.add_value('start_date_requests', comp.offer.start_date_request(lot_number))
                loader.add_value('end_date_requests', comp.offer.end_date_request(lot_number))
                loader.add_value('start_date_trading', comp.offer.start_date_request(lot_number))
                loader.add_value('end_date_trading', comp.offer.end_date_request(lot_number))
                loader.add_value('periods', comp.offer.get_period(lot_number))
                files_lot = comp.offer.download_lot_files(comp.offer.trading_id, lot_number)
                loader.add_value('files', {'general': files_general, 'lot': files_lot})
                loader.add_value('created_at', return_parse_date())
                yield loader.load_item()

    async def errback(self, failure):
        page = failure.request.meta["playwright_page"]
        await page.close()

    def errback_httpbin(self, failure):
        self.logger.error(repr(failure))
        if failure.check(HttpError):
            response = failure.value.response
            self.logger.error("HttpError occurred on %s", response.url)
        elif failure.check(DNSLookupError):
            request = failure.request
            self.logger.error("DNSLookupError occurred on %s", request.url)
        elif failure.check(TimeoutError, TCPTimedOutError):
            request = failure.request
            self.logger.error("TimeoutError occurred on %s", request.url)
