import copy
import json
import re
from itertools import chain
from random import choice

from scrapy import Request, FormRequest
from scrapy.spidermiddlewares.httperror import HttpError
from scrapy.spiders import Spider
from scrapy_splash import SplashRequest, SlotPolicy
from twisted.internet.error import DNSLookupError, TCPTimedOutError

from ..items import CrawlerZalogItem, CrawlerZalogItemLoader
from ..manage_spider.app import Combo
from ..utils.config import start_url, sber_url, user_agent, pagination_url
from ..utils.data_for_requests import script_lua
from ..utils.form_data.param_data_pagination import data_pagination
from ..utils.get_data_from_table import DbConnectCheckLots
from ..utils.headers.headers_sber import headers_to_sber, pagination_headers
from ..utils.work_with_text_and_number import return_main_cookies, cookie_parser
from ..utils.working_with_time import return_parse_date


class ZalogSberSpider(Spider):
    name = 'zalog_sber'
    custom_settings = {
        # 'LOG_FILE': './zalog_sber.log',
        # 'LOG_LEVEL': 'INFO',
        'ITEM_PIPELINES': {
            'crawler_zalog.pipelines.CrawlerZalogPipeline': 300,
            'crawler_zalog.pipelines.ZalogSberConnect': 350,
        }

    }

    def __init__(self):
        super(ZalogSberSpider, self).__init__()
        self.db_check = DbConnectCheckLots()
        self.previous_lots = self.db_check.get_latest_lot()

    def start_requests(self):
        yield SplashRequest(start_url, callback=self.go_to_sber_page, endpoint='execute',
                            cache_args=['lua_source'], args={'lua_source': script_lua},
                            slot_policy=SlotPolicy.PER_DOMAIN,
                            errback=self.errback_httpbin)

    def go_to_sber_page(self, response):
        """ follow to sberbank page with lots """
        headers_to_sber['User-Agent'] = choice(user_agent)
        yield SplashRequest(sber_url, callback=self.parse_main_page_sber, endpoint='execute',
                            cache_args=['lua_source'], args={'lua_source': script_lua},
                            slot_policy=SlotPolicy.PER_DOMAIN, splash_headers=headers_to_sber,
                            errback=self.errback_httpbin)

    def parse_main_page_sber(self, response):
        """ fetch links to lots and get all data for post request """
        combo = Combo(response_=response)
        param = copy.deepcopy(data_pagination)
        param['organizationId'] = combo.serp.get_org_id()
        param['priceTo'] = str(combo.serp.get_priceTo())
        pagination_last_page = combo.serp.get_last_page()
        current_page = 1
        cookie = response.data['cookies']
        headers_to_sber['User-Agent'] = choice(user_agent)
        headers_to_sber['Referer'] = response.url
        first_lot_url = combo.serp.get_first_lot_link()
        if first_lot_url:
            for link in combo.serp.get_links_lot():
                yield Request(link, callback=self.parse_lot_page, headers=headers_to_sber,
                              cookies=cookie_parser(return_main_cookies(cookie)))
            if current_page <= pagination_last_page:
                current_page += 1
                param['page'] = str(current_page)
                pagination_headers['User-Agent'] = choice(user_agent)
                pagination_headers['Referer'] = response.url
                yield FormRequest(pagination_url, callback=self.pagination_circle, formdata=param,
                                  headers=pagination_headers,
                                  cb_kwargs={'current_page': current_page, 'last_page': pagination_last_page,
                                             'first_url': first_lot_url, 'param': param, 'cookie': cookie})

    async def pagination_circle(self, response, current_page, last_page, first_url, param, cookie):
        """ follow next link pagination  and fetch request to lot page """
        combo = Combo(response_=response)
        json_res = json.loads(response.text)
        id_lots = list(map(lambda x: x['id'], json_res['rows']))
        url_lst = [first_url] * len(id_lots)
        links_to_lots = list(map(combo.serp.update_url_lot_param, url_lst, id_lots))
        for link in links_to_lots:
            headers_to_sber['User-Agent'] = choice(user_agent)
            headers_to_sber['Referer'] = response.url
            yield Request(link, callback=self.parse_lot_page, headers=headers_to_sber,
                          cookies=cookie_parser(return_main_cookies(cookie)))

        if current_page < last_page:
            current_page += 1
            param['page'] = str(current_page)
            pagination_headers['User-Agent'] = choice(user_agent)
            pagination_headers['Referer'] = response.url
            yield FormRequest(pagination_url, callback=self.pagination_circle, formdata=param,
                              headers=pagination_headers, cookies=cookie_parser(return_main_cookies(cookie)),
                              cb_kwargs={'current_page': current_page, 'last_page': last_page,
                                         'first_url': first_url, 'param': param, 'cookie': cookie})

    def parse_lot_page(self, response):
        """ parse main page of lot """
        combo = Combo(response_=response)
        short_name = combo.lot.get_short_name()
        match = re.match(r'.+?аренд.+', short_name, re.IGNORECASE)
        match1 = re.match(r'^arend.+', short_name, re.IGNORECASE)
        if not match and not match1:
            loader = CrawlerZalogItemLoader(CrawlerZalogItem(), response=response)
            loader.add_value('data_origin', start_url)
            loader.add_value('trading_id', combo.lot.get_trading_id())
            loader.add_value('trading_link', response.url)
            loader.add_value('trading_number', combo.lot.get_trading_id())
            loader.add_value('trading_type', 'competition')
            loader.add_value('trading_form', 'open')
            loader.add_value('trading_org', 'Сбербанк')
            loader.add_value('trading_org_contacts', combo.lot.get_trading_org_contact())
            loader.add_value('status', 'active')
            loader.add_value('category', combo.lot.get_categories())
            loader.add_value('address', combo.lot.get_address())
            loader.add_value('encumbrance', combo.lot.get_encumbrance())
            loader.add_value('description_encumbrance', combo.lot.get_description_encumbrance())
            loader.add_value('lot_number', '1')
            loader.add_value('short_name', short_name)
            loader.add_value('lot_info', combo.lot.return_complete_lot_info())
            loader.add_value('property_information', combo.lot.property_info())
            loader.add_value('start_date_requests', combo.lot.start_date_requests())
            loader.add_value('end_date_requests', None)
            loader.add_value('start_date_trading', combo.lot.start_date_requests())
            loader.add_value('end_date_trading', None)
            loader.add_value('start_price', combo.lot.start_price())
            pictures = combo.lot.get_all_pictures_link()
            lot_pictures = combo.lot.download_img(pictures)
            general_lot = {'general': []}
            total_files = dict(
                chain(
                    general_lot.items(),
                    lot_pictures.items()))
            loader.add_value('files', total_files)
            loader.add_value('created_at', return_parse_date())
            yield loader.load_item()

    def errback_httpbin(self, failure):
        # logs failures

        self.logger.error(repr(failure))

        if failure.check(HttpError):
            response = failure.value.response
            self.logger.error("HttpError occurred on %s", response.url, )

        elif failure.check(DNSLookupError):
            request = failure.request
            self.logger.error("DNSLookupError occurred on %s", request.url)

        elif failure.check(TimeoutError, TCPTimedOutError):
            request = failure.request
            self.logger.error("TimeoutError occurred on %s", request.url)
