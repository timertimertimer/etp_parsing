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
from app.utils import URL, logger
from app.utils.config import start_date, write_log_to_file


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
                        "max": 20,
                        "updateTotalCount": True,
                    }
                ),
            },
            callback=self.parse,
        )

    def parse(self, response, parsed_all: bool = False):
        data = json.loads(response.text)
        total = data["totalCount"]
        if total > 20 and not parsed_all:
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
            offers = data["list"]
            for offer in offers:
                offer_link = offer["offerLink"]
                if (
                    offer_link not in self.auctions
                    and offer_link not in self.previous_trades
                ):
                    self.auctions.add(offer_link)
                else:
                    continue
                trading_type = {
                    "auction": [
                        "Аукцион",
                        "Аукцион в электронной форме",
                        "Аукцион на повышение",
                        "Аукцион на понижение",
                        "Аукцион в электронной форме (продажа)",
                        "Открытый аукцион в электронной форме",
                    ],
                    "offer": ["Публичное предложение"],
                }
                status = {
                    "active": ["Идет прием заявок", "Объявлен"],
                    "pending": ["Заключение договора", "Работа комиссии"],
                    "ended": [
                        "Приостановлено проведение торгов",
                        "Процедура не состоялась",
                        "Отказ от проведения",
                    ],
                }
                loader = EtpItemLoader(EtpItem(), response=response)
                loader.add_value("data_origin", data_origin[self.name])
                loader.add_value("property_type", self.property_type)
                loader.add_value("trading_id", offer["identifier"])
                loader.add_value("trading_link", offer_link)
                loader.add_value("trading_number", offer["identifier"])
                for key, value in trading_type.items():
                    if offer["placementType"] in value:
                        loader.add_value("trading_type", key)
                        break
                else:
                    logger.warning(
                        f"{response.url} | Could not parse trading type: {offer['placementType']}"
                    )
                loader.add_value("trading_org", offer["organizer"].get("title"))
                loader.add_value("trading_org_inn", offer["organizer"].get("inn"))
                for key, value in status.items():
                    if offer["state"]["title"] in value:
                        loader.add_value("status", key)
                        break
                else:
                    logger.warning(
                        f"{response.url} | Could not parse status: {offer['state']['title']}"
                    )
                lot_link = offer["lotLink"]
                loader.add_value("lot_link", lot_link)
                loader.add_value("lot_number", offer["lotNumber"])
                yield Request(
                    lot_link, callback=self.parse_lot, cb_kwargs={"loader": loader}
                )

    def parse_lot(self, response, loader):
        combo = Combo(response)
        loader.add_value("trading_form", combo.trading_form)
        loader.add_value("short_name", combo.short_name)
        loader.add_value("start_date_requests", combo.start_date_requests)
        loader.add_value("end_date_requests", combo.end_date_requests)
        if loader.get_collected_values("trading_type")[0] == "offer":
            periods = combo.periods
            loader.add_value("periods", periods)
            loader.add_value("start_date_trading", periods[0]["start_date_requests"])
            loader.add_value("end_date_trading", periods[-1]["end_date_requests"])
        else:
            loader.add_value("start_date_trading", combo.start_date_requests)
            loader.add_value("end_date_trading", combo.end_date_requests)
            loader.add_value("start_price", combo.start_price)
            loader.add_value("step_price", combo.step_price)
        files = combo.download_files()
        loader.add_value("files", {"general": [], "lot": files})
        yield loader.load_item()


class CdtrfArrestedSpider(SitesoftBaseSpider):
    name = "cdtrf_arrested"
    property_type = AuctionPropertyType.arrested
    custom_settings = {
        "LOG_FILE": f"{name}.log" if write_log_to_file else None,
    }


class EtpuArrestedSpider(SitesoftBaseSpider):
    name = "etpu_arrested"
    property_type = AuctionPropertyType.arrested
    custom_settings = {
        "LOG_FILE": f"{name}.log" if write_log_to_file else None,
    }


class EtpuCommercialSpider(SitesoftBaseSpider):
    name = "etpu_commercial"
    property_type = AuctionPropertyType.commercial
    custom_settings = {
        "LOG_FILE": f"{name}.log" if write_log_to_file else None,
    }


class AlfalotCommercialSpider(SitesoftBaseSpider):
    name = "alfalot_commercial"
    property_type = AuctionPropertyType.commercial
    custom_settings = {
        "LOG_FILE": f"{name}.log" if write_log_to_file else None,
    }


class TenderOneCommercialSpider(SitesoftBaseSpider):
    name = "tender_one_commercial"
    property_type = AuctionPropertyType.commercial
    custom_settings = {
        "LOG_FILE": f"{name}.log" if write_log_to_file else None,
    }

class EtpuLegalEntitiesSpider(SitesoftBaseSpider):
    name = "etpu_legal_entities"
    property_type = AuctionPropertyType.legal_entities
    custom_settings = {
        "LOG_FILE": f"{name}.log" if write_log_to_file else None,
    }
