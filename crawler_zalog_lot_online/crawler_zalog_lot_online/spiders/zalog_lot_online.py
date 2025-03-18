import json
import re

from scrapy import Request, FormRequest
from scrapy_splash import SplashRequest, SlotPolicy

from general_utils.base_spider import BaseSpider
from general_utils.config import write_log_to_file
from general_utils.items import EtpItem, EtpItemLoader
from ..config import start_url, data_pagination, pagination_url, organization_ids, script_lua, main_data_origin
from ..manage_spider.app import Combo


class ZalogLotOnlineSpider(BaseSpider):
    name = 'zalog_lot_online'
    custom_settings = {
        'LOG_FILE': f'{name}.log' if write_log_to_file else None,
    }

    def __init__(self, domain):
        self.domain = domain
        super().__init__(main_data_origin)

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
                if link not in self.previous_trades:
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
        combo = Combo(response_=response)
        short_name = combo.lot.get_short_name()
        match = re.match(r'.+?аренд.+', short_name, re.IGNORECASE)
        match1 = re.match(r'^arend.+', short_name, re.IGNORECASE)
        if not match and not match1:
            loader = EtpItemLoader(EtpItem(), response=response)
            loader.add_value('data_origin', start_url)
            loader.add_value('trading_id', combo.lot.get_trading_id())
            loader.add_value('trading_link', response.url)
            loader.add_value('trading_number', combo.lot.get_trading_id())
            loader.add_value('trading_type', 'competition')
            loader.add_value('trading_form', 'open')
            loader.add_value('trading_org', 'Россельхозбанк')
            loader.add_value('trading_org_contacts', combo.lot.get_trading_org_contact())
            loader.add_value('status', 'active')
            loader.add_value('address', combo.lot.address)
            loader.add_value('lot_number', '1')
            loader.add_value('short_name', short_name)
            loader.add_value('lot_info', combo.lot.return_complete_lot_info())
            loader.add_value('property_information', combo.lot.property_info())
            loader.add_value('start_date_requests', combo.lot.start_date_requests())
            loader.add_value('end_date_requests', None)
            loader.add_value('start_date_trading', combo.lot.start_date_requests())
            loader.add_value('end_date_trading', None)
            loader.add_value('start_price', combo.lot.start_price())
            loader.add_value('categories', combo.lot.get_categories())
            pictures = combo.lot.get_all_pictures_link()
            lot_pictures = combo.lot.download_img(pictures)
            loader.add_value('files', {'general': [], 'lot': lot_pictures})
            yield loader.load_item()
