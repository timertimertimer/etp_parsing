import json

from scrapy import FormRequest, Request

from app.crawlers.base import BaseSpider
from app.crawlers.crawler_lot_online_tender.crawler_lot_online_tender.config import search_link, formdata, lot_link, \
    data_origin
from app.crawlers.items import EtpItem, EtpItemLoader
from app.db.models import AuctionPropertyType, Auction


class LotOnlineTenderBaseSpider(BaseSpider):
    name = "lot_online_tender"
    property_type = AuctionPropertyType.fz223

    def __init__(self, **kwargs):
        super().__init__(data_origin, select_keys={Auction.ext_id})
        self.unique_links = set()

    def start_requests(self):
        yield FormRequest(
            url=search_link,
            callback=self.parse_serp,
            formdata=formdata,
            method='GET',
            cb_kwargs={'current_page': 0},
        )

    def parse_serp(self, response, current_page):
        data = json.loads(response.text)
        lots = data['data']
        for lot in lots:
            eis_number = lot['eisNumber']
            if eis_number not in self.previous_trades:
                self.unique_links.add(eis_number)
                yield Request(lot_link.format(procedure_id=eis_number), callback=self.parse_procedure)
        if lots:
            current_page += 1
            formdata['page'] = str(current_page)
            yield FormRequest(
                url=search_link,
                callback=self.parse_serp,
                formdata=formdata,
                method='GET',
                cb_kwargs={'current_page': current_page}
            )

    def parse_procedure(self, response):
        data = json.loads(response.text)
        common_info = data['commonInfo']
        loader = EtpItemLoader(item=EtpItem(), response=response)
        loader.add_value('data_origin', data_origin)
        loader.add_value('property_type', self.property_type.value)
        loader.add_value("trading_id", common_info['eisNumber'])
        if
        loader.add_value("trading_link", f'https://tender.lot-online.ru/procedure?procedureNumber={common_info["eisNumber"]}&lotNumber=1')
        loader.add_value("trading_number", common_info['eisNumber'])
        loader.add_value("")
        yield loader.load_item()