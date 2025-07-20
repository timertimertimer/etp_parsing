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
from app.db.models import AuctionPropertyType
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
                    "query": json.dumps(
                        {
                            "types": [types[self.property_type.value]],
                            "placementDate": {"min": start_date},
                        }
                    ),
                    "filter": json.dumps({"state": ["ALL"]}),
                    "sort": json.dumps({"placementDate": False}),
                    "limit": json.dumps(
                        {
                            "min": 0,
                            "max": data["totalCount"],
                            "updateTotalCount": True,
                        }
                    ),
                },
                callback=self.parse,
                cb_kwargs={"parsed_all": True},
            )
        else:
            for offer in data['list']:
                trading_type = {
                    'Аукцион на повышение': 'auction',
                }
                status = {
                    'active': ['Идет прием заявок'],
                    'pending': ['Заключение договора'],
                    'ended': ['Приостановлено проведение торгов']
                }
                loader = EtpItemLoader(EtpItem(), response=response)
                loader.add_value("data_origin", data_origin[self.name])
                loader.add_value("property_type", self.property_type)
                loader.add_value("trading_id", offer['identifier'])
                loader.add_value("trading_link", offer['offerLink'])
                loader.add_value("trading_number", offer['identifier'])
                loader.add_value("trading_type", trading_type[data['placementType']])
                loader.add_value("trading_org", data['organizer'].get('title'))
                loader.add_value("trading_org_inn", data['organizer'].get('inn'))
                for key, value in status.items():
                    if data['state']['title'] in value:
                        loader.add_value('status', key)
                lot_link = data['lotLink']
                loader.add_value("lot_link", lot_link)
                loader.add_value("lot_number", data['lot_number'])
                yield Request(lot_link)


    def parse_lot(self, response, loader):
        combo = Combo(response)
        loader.add_value("trading_form", combo.trading_form)
        loader.add_value("short_name", combo.short_name)
        loader.add_value("start_date_requests", combo.start_date_requests)
        loader.add_value("end_date_requests", combo.end_date_requests)
        loader.add_value("start_date_trading", combo.start_date_trading)
        loader.add_value("end_date_trading", combo.end_date_trading)
        loader.add_value("start_price", combo.start_price)
        yield loader.load_item()


class CdtrfArrestedSpider(SitesoftBaseSpider):
    name = "cdtrf_arrested"
    property_type = AuctionPropertyType.arrested


class EtpuArrestedSpider(SitesoftBaseSpider):
    name = "etpu_arrested"
    property_type = AuctionPropertyType.arrested


class EtpuCommercialSpider(SitesoftBaseSpider):
    name = "etpu_commercial"
    property_type = AuctionPropertyType.commercial


class AlfalotCommercialSpider(SitesoftBaseSpider):
    name = "alfalot_commercial"
    property_type = AuctionPropertyType.commercial
