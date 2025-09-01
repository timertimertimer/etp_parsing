from typing import Iterable
from scrapy import Request, FormRequest

from app.crawlers.items import EtpItem, EtpItemLoader
from app.crawlers.base import BaseSpider
from app.utils.config import start_date
from app.utils import URL
from ..config import data_origin_url
from ..combo import Combo


class MoiTenderSpider(BaseSpider):
    name = "moi_tender"
    start_urls = ["https://xn--d1abbnoievn.xn--p1ai/tenders.html"]

    def __init__(self):
        super(MoiTenderSpider, self).__init__(data_origin_url)
        self.trade_links = set()
        self.orgs_contacts = {}

    def start_requests(self) -> Iterable[Request]:
        params = {
            "q": "",
            "filter": "Y",
            "limit": "100",
            "sort": "p.date_start",
            "order": "DESC",
            "f_num": "",
            "f_section": "0",
            "f_price_min": "",
            "f_price_max": "",
            "f_date_start_min": start_date,
            "f_date_start_max": "",
            "f_date_finish_min": "",
            "f_date_finish_max": "",
        }
        for f_type, trading_type in enumerate(
            ["offer", "competition", "auction"], start=1
        ):
            params["f_type"] = str(f_type)
            yield FormRequest(
                self.start_urls[0],
                formdata=params,
                dont_filter=True,
                cb_kwargs={"trading_type": trading_type},
                method="GET",
            )

    def parse(self, response, trading_type):
        combo = Combo(response)
        for lot in combo.get_lots():
            lot["trading_type"] = trading_type
            if lot["trading_link"] not in self.previous_trades:
                if lot["org"] not in self.orgs_contacts:
                    yield Request(
                        URL.url_join(data_origin_url, lot["org_link"]),
                        self.parse_org,
                        cb_kwargs={"lot": lot},
                    )
                else:
                    yield Request(
                        lot["trading_link"], self.parse_trade, cb_kwargs={"lot": lot}
                    )

    def parse_org(self, response, lot):
        combo = Combo(response)
        self.orgs_contacts[lot["org"]] = {
            "contacts": combo.trading_org_contacts,
            "inn": combo.trading_org_inn,
        }
        yield Request(lot["trading_link"], self.parse_trade, cb_kwargs={"lot": lot})

    def parse_trade(self, response, lot):
        combo = Combo(response)
        loader = EtpItemLoader(EtpItem(), response=response)
        loader.add_value("data_origin", data_origin_url)
        loader.add_value("trading_id", lot["trading_id"])
        loader.add_value("trading_link", response.url)
        loader.add_value("trading_number", lot["trading_number"])
        loader.add_value("trading_type", lot["trading_type"])
        loader.add_value("trading_form", lot["trading_form"])
        loader.add_value("trading_org", lot["org"])
        loader.add_value("trading_org_inn", self.orgs_contacts[lot["org"]]["inn"])
        loader.add_value(
            "trading_org_contacts", self.orgs_contacts[lot["org"]]["contacts"]
        )
        loader.add_value("status", lot["status"])
        loader.add_value("address", lot["address"])
        loader.add_value("short_name", lot["short_name"])
        loader.add_value("start_price", lot["start_price"])
        loader.add_value("lot_info", combo.lot_info)
        loader.add_value("lot_number", combo.lot_number)
        loader.add_value("start_date_requests", combo.start_date_requests)
        loader.add_value("end_date_requests", combo.end_date_requests)
        loader.add_value(
            "files", {"general": combo.download_trade(), "lot": combo.download_lot()}
        )
        loader.add_value("categories", None)
        yield loader.load_item()
