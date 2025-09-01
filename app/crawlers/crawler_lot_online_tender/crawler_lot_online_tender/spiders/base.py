import json

from scrapy import FormRequest, Request

from app.crawlers.base import BaseSpider
from app.crawlers.crawler_lot_online_tender.crawler_lot_online_tender.combo import Combo
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
            eis_number = lot['eisNumber'] or lot['etpNumber']
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
        combo = Combo(response)
        loader = EtpItemLoader(item=EtpItem(), response=response)
        loader.add_value('data_origin', data_origin)
        loader.add_value('property_type', self.property_type.value)
        loader.add_value("trading_id", combo.trading_id)
        loader.add_value("trading_link", combo.trading_link)
        loader.add_value("trading_number", combo.trading_number)  # trading_id
        loader.add_value("trading_type", combo.trading_type)
        loader.add_value("trading_form", combo.trading_form)  # open
        loader.add_value("trading_org", combo.trading_org)
        loader.add_value("trading_org_inn", combo.trading_org_inn)
        loader.add_value("trading_org_contacts", combo.trading_org_contacts)
        loader.add_value("address", combo.address)
        loader.add_value("lot_number", combo.lot_number)
        loader.add_value("categories", combo.categories)
        dates = combo.dates()
        loader.add_value("start_date_requests", dates['start_date_requests'])
        loader.add_value("end_date_requests", dates['end_date_requests'])
        loader.add_value("start_date_trading", dates['start_date_trading'])
        loader.add_value("end_date_trading", dates['end_date_trading'])
        loader.add_value("start_price", combo.start_price)
        if combo.trading_type in ["auction", "competition"]:
            loader.add_value("step_price", combo.step_price)
        loader.add_value("periods", combo.periods)
        loader.add_value(
            "files",
            {"general": combo.download_general(), "lot": combo.download_lot()},
        )
        yield loader.load_item()
