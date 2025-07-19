import json

from scrapy import FormRequest, Request

from app.crawlers.base import BaseSpider
from app.crawlers.crawler_sitesoft.crawler_sitesoft.combo import Combo
from app.crawlers.crawler_sitesoft.crawler_sitesoft.config import (
    data_origin,
    urls,
    types,
)
from app.crawlers.items import EtpItemLoader, EtpItem
from app.utils import URL
from app.utils.config import start_date


class SitesoftBaseSpider(BaseSpider):
    name = "base"

    def __init__(self):
        self.start_urls = [URL.url_join(urls[self.name], "/searchServlet")]
        self.auctions = set()
        super().__init__(data_origin[self.name])

    def start_requests(self):
        yield FormRequest(
            method="GET",
            url=self.start_urls[0],
            formdata={
                "query": json.dumps({"types": types[self.property_type.value]}),
                "filter": json.dumps({"state": ["ALL"]}),
                "sort": json.dumps({"placementDate": {"min": start_date}}),
                "limit": json.dumps(
                    {"min": "0", "max": "20", "updateTotalCount": "true"}
                ),
            },
            callback=self.parse,
        )

    def parse(self, response, parsed_all: bool = False):
        data = json.loads(response.text)
        if data["totalCount"] > 20 and not parsed_all:
            yield FormRequest(
                method="GET",
                url=self.start_urls[0],
                formdata={
                    "query": json.dumps({"types": types[self.property_type.value]}),
                    "filter": json.dumps({"state": ["ALL"]}),
                    "sort": json.dumps({"placementDate": {"min": start_date}}),
                    "limit": json.dumps(
                        {
                            "min": "0",
                            "max": data["totalCount"],
                            "updateTotalCount": "true",
                        }
                    ),
                },
                callback=self.parse,
                cb_kwargs={"parsed_all": True},
            )
        else:
            links = response.xpath('//a[@class="gwt-Anchor"]/@href').getall()
            for link in links:
                yield Request(
                    link, callback=self.get_auction_from_lot
                )

    def get_auction_from_lot(self, response):
        auction_link = response.xpath('//a[@id="ParametrizedPageLink_5"]/@href').get()
        yield Request(auction_link, callback=self.parse_auction)
        
    def parse_auction(self, response):
        combo = Combo(response)
        loader = EtpItemLoader(EtpItem(), response=response)
        loader.add_value("data_origin", data_origin[self.name])
        loader.add_value('property_type', self.property_type)
        loader.add_value("trading_id", combo.trading_id)
        loader.add_value("trading_link", combo.trading_link)
        loader.add_value("trading_number", combo.trading_number)
        loader.add_value("trading_type", combo.trading_type)
        loader.add_value("trading_org", combo.trading_org)
        loader.add_value("trading_org_inn", combo.trading_org_inn)
        loader.add_value("trading_org_contacts", combo.trading_org_contacts)
        loader.add_value("msg_number", combo.msg_number)
        loader.add_value("case_number", combo.case_number)
        loader.add_value("debtor_inn", combo.debtor_inn)
        loader.add_value("address", combo.address)
        loader.add_value("arbit_manager", combo.arbit_manager)
        loader.add_value("arbit_manager_inn", combo.arbit_manager_inn)
        loader.add_value("arbit_manager_org", combo.arbit_manager_org)
        loader.add_value("property_information", combo.property_information)
        for

    def parse_lot(self, response, loader):
        combo = Combo(response)
        loader.add_value('trading_form', combo.trading_form)
        loader.add_value('status', combo.status)
        loader.add_value("trading_form", combo.trading_form)
        loader.add_value("short_name", combo.short_name)
        loader.add_value("lot_link", combo.lot_link)
        loader.add_value("lot_number", combo.lot_number)
        loader.add_value("start_date_requests", combo.start_date_requests)
        loader.add_value("end_date_requests", combo.end_date_requests)
        loader.add_value("start_date_trading", combo.start_date_trading)
        loader.add_value("end_date_trading", combo.end_date_trading)
        loader.add_value("start_price", combo.start_price)
        yield loader.load_item()
