import json

import xmltodict
from scrapy import FormRequest, Request
from bs4 import BeautifulSoup as BS

from app.crawlers.crawler_sberbank.crawler_sberbank.spiders.base import (
    SberbankBaseSpider,
)
from app.crawlers.crawler_sberbank.crawler_sberbank.trades.html_combo import HTMLCombo
from app.crawlers.crawler_sberbank.crawler_sberbank.utils.config import (
    urls,
    data_origin_url,
)
from app.crawlers.crawler_sberbank.crawler_sberbank.utils.manage_spider import solve_challenge
from app.crawlers.items import EtpItemLoader, EtpItem
from app.db.models import AuctionPropertyType


class SberbankBaseHTMLSpider(SberbankBaseSpider):
    name = "base_html"

    def start_requests(self):
        yield Request(
            url=urls[self.property_type.value],
            callback=self.send_request_for_new_cookies,
        )

    def send_request_for_new_cookies(self, response):
        text = response.text
        challenge = text.split("Challenge=")[1].split(";")[0]
        challenge_id = text.split("ChallengeId=")[1].split(";")[0]
        result = solve_challenge(int(challenge))
        return Request(
            url=urls[self.property_type.value],
            method="POST",
            headers={
                "X-Aa-Challenge": str(challenge),
                "X-Aa-Challenge-ID": str(challenge_id),
                "X-Aa-Challenge-Result": result,
                "Content-Type": "text/plain",
                "sec-ch-ua-platform": '"Windows"',
                "sec-ch-ua-mobile": "?0",
                "sec-ch-ua": '"Chromium";v="140", "Not=A?Brand";v="24", "Google Chrome";v="140"',
                "content-length": "0"
            },
            callback=self.after_challenge,
            dont_filter=True,
        )

    def after_challenge(self, response):
        cookies = response.headers.get(b"Cookie")
        super().start_requests()

    def parse_table(self, response):
        soup = BS(json.loads(response.text)["data"]["Data"]["tableXml"], "lxml-xml")
        data = xmltodict.parse(str(soup))["datarow"]
        trades = set(lot["_source"]["objectHrefTerm"] for lot in data["hits"])
        for trade in trades:
            yield Request(trade, self.parse_trade)

    def parse_trade(self, response):
        combo = HTMLCombo(response)
        loader = EtpItemLoader(EtpItem(), response=response)
        loader.add_value("data_origin", data_origin_url)
        loader.add_value("property_type", self.property_type.value)
        loader.add_value("trading_link", response.url)
        yield loader.load_item()


class SberbankCommercialHTMLSpider(SberbankBaseHTMLSpider):
    name = "sberbank_commercial"
    property_type = AuctionPropertyType.commercial


class SberbankFz223HTMLSpider(SberbankBaseHTMLSpider):
    name = "sberbank_fz223"
    property_type = AuctionPropertyType.fz223


class SberbankFz44HTMLSpider(SberbankBaseHTMLSpider):
    name = "sberbank_fz44"
    property_type = AuctionPropertyType.fz44
