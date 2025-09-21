import copy
import re

from scrapy import Request, FormRequest

from app.db.models import AuctionPropertyType
from app.utils import logger
from app.utils.config import write_log_to_file
from .base import ItenderBaseSpider
from ..config import (
    centerr_commercial_offer_post_data,
    start_date,
    centerr_commercial_auction_post_data,
)
from ..manage_spiders.combo import Combo

mapping = {"auctions-up-all": "auction", "public-offers-all": "offer"}


class CenterrBankruptSpider(ItenderBaseSpider):
    name = "centerr_bankruptcy"
    property_type = AuctionPropertyType.bankruptcy
    custom_settings = {
        "LOG_FILE": f"{name}.log" if write_log_to_file else None,
    }


class CenterrCommercialSpider(ItenderBaseSpider):
    name = "centerr_commercial"
    property_type = AuctionPropertyType.commercial
    custom_settings = {
        "LOG_FILE": f"{name}.log" if write_log_to_file else None,
    }

    def choose_datatype(self, response):
        for _type in ["auctions-up-all", "public-offers-all"]:
            yield Request(
                f"https://business.centerr.ru/public/{_type}/",
                self.parse_,
                cb_kwargs={"_type": mapping[_type]},
            )

    def parse_(self, response, _type: str):
        first_post = None
        function_for_parse = None
        combo = Combo(response)
        if _type == "auction":
            first_post = copy.deepcopy(centerr_commercial_auction_post_data)
            function_for_parse = self.parse_serp_auction
            first_post[
                "ctl00$ctl00$MainExpandableArea$phExpandCollapse$ctl00$SearchCriteria1$vPurchaseLot_auctionStartDate_Датапроведенияс_dateInput"
            ] = start_date
        if _type == "offer":
            first_post = copy.deepcopy(centerr_commercial_offer_post_data)
            function_for_parse = self.parse_serp_offer
            first_post[
                "ctl00$ctl00$MainExpandableArea$phExpandCollapse$ctl00$SearchCriteria1$Purchase_bidSubmissionStartDate_Датаначалапредставлениязаявокнаучастиес_dateInput"
            ] = start_date
        first_post["__EVENTTARGET"] = combo.mpost.get_post_data_values(
            tag_html="input", post_argument="__EVENTTARGET"
        )
        first_post["__EVENTARGUMENT"] = combo.mpost.get_post_data_values(
            "input", "__EVENTARGUMENT"
        )
        first_post["__CVIEWSTATE"] = combo.mpost.get_post_data_values(
            "input", "__CVIEWSTATE"
        )
        first_post["__VIEWSTATE"] = combo.mpost.get_post_data_values(
            "input", "__VIEWSTATE"
        )
        first_post["__EVENTVALIDATION"] = combo.mpost.get_post_data_values(
            "input", "__EVENTVALIDATION"
        )
        yield FormRequest(
            response.url,
            formdata=first_post,
            callback=function_for_parse,
            cb_kwargs={"first_post": first_post, "trading_type": _type},
        )

    def parse_serp_auction(self, response, first_post, trading_type: str):
        combo = Combo(response=response)
        eventvalidation = "".join(
            re.findall(
                r"hiddenField\|__EVENTVALIDATION\|(.*)\|.*\|asyncPostBackControlIDs",
                response.body.decode("utf-8"),
            )
        )
        cviewstate = "".join(
            re.findall(
                r"hiddenField\|__CVIEWSTATE\|(.*)\|", response.body.decode("utf-8")
            )
        )
        current_page = combo.serp.get_current_page()
        logger.info(f"Current serp page ({trading_type}): {current_page}")
        next_page = combo.serp.get_next_page()
        if data_next_page_post := combo.serp.body_scripts():
            first_post["ctl00$ctl00$BodyScripts$ctl00$ctl00"] = (
                "ctl00$ctl00$MainContent$ContentPlaceHolderMiddle$ctl00$ctl00|"
                + data_next_page_post
            )
            first_post["__CVIEWSTATE"] = cviewstate
            first_post["__EVENTVALIDATION"] = eventvalidation
            first_post["__EVENTTARGET"] = data_next_page_post
            if first_post.get(
                "ctl00$ctl00$MainExpandableArea$phExpandCollapse$ctl00$btnSearch"
            ):
                del first_post[
                    "ctl00$ctl00$MainExpandableArea$phExpandCollapse$ctl00$btnSearch"
                ]
            first_post[""] = ""
        for link in combo.serp.get_link_to_lot(current_page, self.data_origin):
            if link[0] not in self.previous_trades:
                yield Request(
                    link[0],
                    callback=self.parse_trading_page_auction,
                    dont_filter=True,
                    cb_kwargs={
                        "lot_number": link[1],
                        "lot_link": link[2],
                        "link_trade": link[0],
                        "attemp": 1,
                    },
                )

        if current_page and next_page:
            if int(current_page) < int(next_page):
                yield FormRequest(
                    response.url,
                    formdata=first_post,
                    callback=self.parse_serp_auction,
                    cb_kwargs={"first_post": first_post, "trading_type": trading_type},
                    dont_filter=True,
                )

    def parse_serp_offer(self, response, first_post, trading_type: str):
        combo = Combo(response=response)
        eventvalidation = "".join(
            re.findall(
                r"hiddenField\|__EVENTVALIDATION\|(.*)\|.*\|asyncPostBackControlIDs",
                response.body.decode("utf-8"),
            )
        )
        cviewstate = "".join(
            re.findall(
                r"hiddenField\|__CVIEWSTATE\|(.*)\|", response.body.decode("utf-8")
            )
        )
        current_page = combo.serp.get_current_page()
        logger.info(f"Current serp page ({trading_type}): {current_page}")
        next_page = combo.serp.get_next_page()
        if data_next_page_post := combo.serp.body_scripts():
            first_post["ctl00$ctl00$BodyScripts$ctl00$ctl00"] = (
                "ctl00$ctl00$MainContent$ContentPlaceHolderMiddle$ctl00$ctl00|"
                + data_next_page_post
            )
            first_post["__CVIEWSTATE"] = cviewstate
            first_post["__EVENTVALIDATION"] = eventvalidation
            first_post["__EVENTTARGET"] = data_next_page_post
            if first_post.get(
                "ctl00$ctl00$MainExpandableArea$phExpandCollapse$ctl00$btnSearch"
            ):
                del first_post[
                    "ctl00$ctl00$MainExpandableArea$phExpandCollapse$ctl00$btnSearch"
                ]
            first_post[""] = ""
        for link in combo.serp.get_link_to_lot(current_page, self.data_origin):
            if link[0] not in self.previous_trades:
                yield Request(
                    link[0],
                    callback=self.parse_trade_page_offer,
                    cb_kwargs={"lot_number": link[1], "lot_link": link[2], "attemp": 1},
                    dont_filter=True,
                )

        if current_page and next_page:
            if int(current_page) < int(next_page):
                yield FormRequest(
                    response.url,
                    formdata=first_post,
                    callback=self.parse_serp_offer,
                    cb_kwargs={"first_post": first_post, "trading_type": trading_type},
                    dont_filter=True,
                )
