import json
import re
from itertools import chain

from scrapy import Request, FormRequest
from scrapy.spidermiddlewares.httperror import HttpError
from scrapy_splash import SplashRequest, SlotPolicy
from twisted.internet.error import DNSLookupError, TCPTimedOutError
from general_utils.base_spider import BaseSpider
from general_utils.config import write_log_to_file
from general_utils.items import CrawlerNonBankruptItem, CrawlerNonBankruptItemLoader
from ..manage_spider.app import Combo
from ..utils.config import start_url, data_pagination, pagination_url, organization_ids
from ..utils.data_for_requests import script_lua


class ZalogLotOnlineSpider(BaseSpider):
    name = 'zalog_lot_online'
    custom_settings = {
        'LOG_FILE': f'{name}.log' if write_log_to_file else None,
    }
    
    def __init__(self):
        super().__init__()  # FIXME

    def start_requests(self):
        yield SplashRequest(
            start_url, callback=self.go_to, endpoint='execute',
            cache_args=['lua_source'], args={'lua_source': script_lua},
            slot_policy=SlotPolicy.PER_DOMAIN,
            errback=self.errback_httpbin
        )

    def go_to(self, response, next_page: int = 1):
        data_pagination['organizationId'] = organization_ids[self.domain]
        data_pagination['page'] = str(next_page)
        if next_page > 1:
            json_res = json.loads(response.text)
            for lot in list(map(lambda x: x['id'], json_res['rows'])):
                link = f'https://zalog.lot-online.ru/user/collateral/catalog_page.html?id={lot}'
                if (link,) not in self.previous_lots:
                    yield Request(link, self.parse_lot_page)
            if next_page - 1 < int(json_res['total']):
                next_page += 1
                yield FormRequest(
                    pagination_url, callback=self.go_to, formdata=data_pagination, cb_kwargs={'next_page': next_page}
                )
        else:
            next_page += 1
            yield FormRequest(
                pagination_url, callback=self.go_to, formdata=data_pagination, cb_kwargs={'next_page': next_page}
            )

    async def parse_lot_page(self, response):
        """ parse main page of lot """
        combo = Combo(response_=response)
        short_name = combo.lot.get_short_name()
        match = re.match(r'.+?аренд.+', short_name, re.IGNORECASE)
        match1 = re.match(r'^arend.+', short_name, re.IGNORECASE)
        if not match and not match1:
            loader = CrawlerNonBankruptItemLoader(CrawlerNonBankruptItem(), response=response)
            loader.add_value('data_origin', start_url)
            loader.add_value('trading_id', combo.lot.get_trading_id())
            loader.add_value('trading_link', response.url)
            loader.add_value('trading_number', combo.lot.get_trading_id())
            loader.add_value('trading_type', 'competition')
            loader.add_value('trading_form', 'open')
            loader.add_value('trading_org', 'Россельхозбанк')
            loader.add_value('trading_org_contacts', combo.lot.get_trading_org_contact())
            loader.add_value('status', 'active')
            loader.add_value('category', combo.lot.get_categories())
            address = combo.lot.address
            loader.add_value('address', address)
            loader.add_value('index', get_index(address))
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
            lot_pictures = combo.lot.download_img(pictures, self.domain)
            general_lot = {'general': []}
            total_files = dict(chain(general_lot.items(), lot_pictures.items()))
            loader.add_value('files', total_files)
            yield loader.load_item()

    def errback_httpbin(self, failure):
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
