import copy
import re
from random import randint

from scrapy import Request, FormRequest
from scrapy_splash import SplashRequest, SlotPolicy

from app.crawlers.items import EtpItem, EtpItemLoader
from app.crawlers.base import BaseSpider
from app.db.models import AuctionPropertyType
from app.utils import logger
from app.utils.config import write_log_to_file
from app.crawlers.crawler_itender.crawler_itender.manage_spiders.combo import Combo
from app.crawlers.crawler_itender.crawler_itender.config import (
    return_auction_link,
    data_origin,
    return_offer_link,
    return_compet_link,
    post_data_auction,
    post_data_offer,
    post_data_competition,
    start_date,
    script_lua_nojs,
    common_data, urls,
)


class ItenderBaseSpider(BaseSpider):
    name = "base"
    property_type = AuctionPropertyType.bankruptcy
    custom_settings = {
        "LOG_FILE": f"{name}.log" if write_log_to_file else None,
    }

    @classmethod
    def set_links(cls):
        cls.data_origin = data_origin.get(cls.name)

    def __init__(self):
        self.set_links()
        super(ItenderBaseSpider, self).__init__(urls[self.name])

    def start_requests(self):
        yield Request(self.data_origin, self.choose_datatype)

    def choose_datatype(self, response):
        for _type in ["auction", "offer", "competition"]:
            if _type == "auction":
                yield Request(
                    return_auction_link(self.data_origin),
                    self.parse_,
                    cb_kwargs={"_type": "auction"},
                )
            if _type == "offer":
                yield Request(
                    return_offer_link(self.data_origin),
                    self.parse_,
                    cb_kwargs={"_type": "offer"},
                )
            if _type == "competition":
                yield Request(
                    return_compet_link(self.data_origin),
                    self.parse_,
                    cb_kwargs={"_type": "competition"},
                )

    def parse_(self, response, _type: str):
        first_post = None
        function_for_parse = None
        combo = Combo(response)
        if _type == "auction":
            first_post = copy.deepcopy(post_data_auction)
            function_for_parse = self.parse_serp_auction
            first_post[
                (
                    "ctl00$ctl00$MainExpandableArea$phExpandCollapse$PurchasesSearchCriteria$vPurchaseLot_auctionStartDate_"
                    "Датапроведенияс_dateInput"
                )
            ] = start_date
        if _type == "offer":
            first_post = copy.deepcopy(post_data_offer)
            function_for_parse = self.parse_serp_offer
            first_post[
                (
                    "ctl00$ctl00$MainExpandableArea$phExpandCollapse$PurchasesSearchCriteria$vPurchaseLot_"
                    "bidSubmissionStartDate_Датаначалапредставлениязаявокнаучастиес_dateInput"
                )
            ] = start_date
        if _type == "competition":
            first_post = copy.deepcopy(post_data_competition)
            function_for_parse = self.parse_competiton_serp
            first_post[
                (
                    "ctl00$ctl00$MainExpandableArea$phExpandCollapse$PurchasesSearchCriteria$vPurchaseLot_auctionStartDate_"
                    "Датапроведенияс_dateInput"
                )
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
        if combo.serp.body_scripts():
            data_next_page_post = combo.serp.body_scripts()
            first_post["ctl00$ctl00$BodyScripts$BodyScripts$scripts"] = (
                "ctl00$ctl00$MainContent$ContentPlaceHolderMiddle$UpdatePanel2|"
                + data_next_page_post
            )
            first_post["__CVIEWSTATE"] = cviewstate
            first_post["__EVENTVALIDATION"] = eventvalidation
            first_post["__EVENTTARGET"] = data_next_page_post
            if first_post.get(
                "ctl00$ctl00$MainExpandableArea$phExpandCollapse$SearchButton"
            ):
                del first_post[
                    "ctl00$ctl00$MainExpandableArea$phExpandCollapse$SearchButton"
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

    async def parse_trading_page_auction(
        self, response, lot_number, lot_link, link_trade, attemp
    ):
        combo = Combo(response=response)
        loader = EtpItemLoader(EtpItem(), response=response)
        loader.add_value("data_origin", self.data_origin)
        loader.add_value("property_type", self.property_type.value)
        loader.add_value("trading_id", "".join(re.findall(r"\d+", response.url)))
        loader.add_value("trading_link", response.url)
        trading_number = combo.auc.trading_number
        if trading_number is not None and attemp < 5:
            loader.add_value("trading_number", trading_number)
            loader.add_value("trading_type", "auction")
            loader.add_value("trading_form", combo.auc.trading_form)
            loader.add_value("trading_org", combo.auc.trading_org)
            loader.add_value("trading_org_inn", combo.auc.trading_org_inn)
            loader.add_value("trading_org_contacts", combo.auc.trading_org_contacts)
            loader.add_value("msg_number", combo.auc.msg_number)
            loader.add_value("case_number", combo.auc.case_number)
            loader.add_value("debtor_inn", combo.auc.debtor_inn)
            loader.add_value("address", combo.auc.address)
            loader.add_value("arbit_manager", combo.auc.arbit_manager)
            loader.add_value("arbit_manager_inn", combo.auc.arbit_manager_inn)
            loader.add_value("arbit_manager_org", combo.auc.arbit_manager_org)
            start_date_trading = combo.auc.start_date_trading
            loader.add_value("start_date_requests", combo.auc.start_date_requests)
            loader.add_value("end_date_requests", combo.auc.end_date_requests)
            loader.add_value("start_date_trading", start_date_trading)
            loader.add_value("end_date_trading", None)
            _id = "".join(loader.get_collected_values("trading_id"))
            general_files = combo.offer.download(self.name)
            common_data["__CVIEWSTATE"] = combo.mpost.get_post_data_values(
                "input", "__CVIEWSTATE"
            )
            common_data["__EVENTVALIDATION"] = combo.mpost.get_post_data_values(
                "input", "__EVENTVALIDATION"
            )
            common_data["__EVENTTARGET"] = combo.serp.body_scripts()
            common_data["__SCROLLPOSITIONY"] = str(randint(2289, 3662))
            yield Request(
                lot_link,
                callback=self.parse_lot_page,
                dont_filter=True,
                cb_kwargs={
                    "loader": loader,
                    "lot_number": lot_number,
                    "general": general_files,
                },
            )
        else:
            attemp += 1
            yield SplashRequest(
                link_trade,
                callback=self.parse_trading_page_auction,
                cache_args=["lua_source"],
                args={"lua_source": script_lua_nojs},
                slot_policy=SlotPolicy.PER_DOMAIN,
                dont_send_headers=True,
                cb_kwargs={
                    "lot_number": lot_number,
                    "lot_link": lot_link,
                    "link_trade": link_trade,
                    "attemp": attemp,
                },
                dont_filter=True,
            )

    async def parse_lot_page(self, response, loader, lot_number, general: dict):
        combo = Combo(response=response)
        lot_num = combo.auc.lot_number_on_lot_page(response.url, lot_number)
        if lot_number:
            loader.add_value("status", combo.auc.status)
            loader.add_value("lot_id", "".join(re.findall(r"\d+", str(response.url))))
            loader.add_value("lot_link", response.url)
            loader.add_value("lot_number", lot_num)
            loader.add_value("short_name", combo.auc.short_name)
            loader.add_value("lot_info", combo.auc.lot_info)
            loader.add_value("property_information", combo.auc.property_information)
            loader.add_value("start_price", combo.auc.start_price)
            loader.add_value("step_price", combo.auc.step_price)
            loader.add_value("categories", combo.auc.categories)
            _id = "".join(loader.get_collected_values("trading_id"))
            lot_file = combo.offer.download(self.name)
            loader.add_value("files", {"general": general, "lot": lot_file})
            yield loader.load_item()

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
        if combo.serp.body_scripts():
            data_next_page_post = combo.serp.body_scripts()
            first_post["ctl00$ctl00$BodyScripts$BodyScripts$scripts"] = (
                "ctl00$ctl00$MainContent$ContentPlaceHolderMiddle$UpdatePanel2|"
                + data_next_page_post
            )
            first_post["__CVIEWSTATE"] = cviewstate
            first_post["__EVENTVALIDATION"] = eventvalidation
            first_post["__EVENTTARGET"] = data_next_page_post
            if first_post.get(
                "ctl00$ctl00$MainExpandableArea$phExpandCollapse$SearchButton"
            ):
                del first_post[
                    "ctl00$ctl00$MainExpandableArea$phExpandCollapse$SearchButton"
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

    def parse_trade_page_offer(self, response, lot_number, lot_link, attemp):
        combo = Combo(response=response)
        loader = EtpItemLoader(EtpItem(), response=response)
        loader.add_value("data_origin", self.data_origin)
        loader.add_value("property_type", self.property_type.value)
        loader.add_value("trading_id", "".join(re.findall(r"\d+", response.url)))
        loader.add_value("trading_link", response.url)
        loader.add_value("trading_number", combo.offer.trading_number)
        loader.add_value("trading_type", "offer")
        loader.add_value("trading_form", combo.offer.trading_form)
        loader.add_value("trading_org", combo.auc.trading_org)
        loader.add_value("trading_org_inn", combo.auc.trading_org_inn)
        loader.add_value("trading_org_contacts", combo.auc.trading_org_contacts)
        loader.add_value("msg_number", combo.offer.msg_number)
        loader.add_value("case_number", combo.auc.case_number)
        loader.add_value("debtor_inn", combo.auc.debtor_inn)
        loader.add_value("address", combo.auc.address)
        loader.add_value("arbit_manager", combo.auc.arbit_manager)
        loader.add_value("arbit_manager_inn", combo.auc.arbit_manager_inn)
        loader.add_value("arbit_manager_org", combo.auc.arbit_manager_org)
        _id = "".join(loader.get_collected_values("trading_id"))
        general_files = combo.offer.download(self.name)
        common_data["__CVIEWSTATE"] = combo.mpost.get_post_data_values(
            "input", "__CVIEWSTATE"
        )
        common_data["__EVENTVALIDATION"] = combo.mpost.get_post_data_values(
            "input", "__EVENTVALIDATION"
        )
        common_data["__EVENTTARGET"] = combo.serp.body_scripts()
        common_data["__SCROLLPOSITIONY"] = str(randint(2289, 3662))
        yield Request(
            lot_link,
            callback=self.parse_lot_page_offer,
            cb_kwargs={
                "loader": loader,
                "lot_number": lot_number,
                "general": general_files,
                "pdata_lot_page_period": common_data,
            },
            dont_filter=True,
        )

    async def parse_lot_page_offer(
        self, response, loader, lot_number, general, pdata_lot_page_period
    ):
        combo = Combo(response=response)
        lot_num = combo.auc.lot_number_on_lot_page(response.url, lot_number)
        pager = combo.serp.get_href_post_lot_page()
        if lot_number and pager is None:
            loader.add_value("status", combo.auc.status)
            loader.add_value("lot_id", "".join(re.findall(r"\d+", str(response.url))))
            loader.add_value("lot_link", response.url)
            loader.add_value("lot_number", lot_num)
            loader.add_value("short_name", combo.auc.short_name)
            loader.add_value("lot_info", combo.auc.lot_info)
            loader.add_value("property_information", combo.offer.property_information)
            loader.add_value("periods", combo.offer.periods)
            loader.add_value(
                "start_date_requests", combo.offer.start_date_requests
            )
            loader.add_value("end_date_requests", combo.offer.end_date_requests)
            loader.add_value("start_date_trading", combo.offer.start_date_trading)
            loader.add_value("end_date_trading", combo.offer.end_date_trading)
            loader.add_value("start_price", combo.offer.start_price)
            loader.add_value("categories", combo.auc.categories)
            _id = "".join(loader.get_collected_values("trading_id"))
            lot_file = combo.offer.download(self.name)
            loader.add_value("files", {"general": general, "lot": lot_file})
            yield loader.load_item()
        else:
            pages = combo.serp.fetch_pagination_links_lot_page()
            cviewstate = combo.mpost.get_post_data_values("input", "__CVIEWSTATE")
            eventvalidation = combo.mpost.get_post_data_values(
                "input", "__EVENTVALIDATION"
            )
            if cviewstate is None or len(cviewstate) < 0:
                cviewstate = "".join(
                    re.findall(
                        r"hiddenField\|__CVIEWSTATE\|(.*)\|",
                        response.body.decode("utf-8"),
                    )
                )
                eventvalidation = "".join(
                    re.findall(
                        r"hiddenField\|__EVENTVALIDATION\|(.*)\|.*\|asyncPostBackControlIDs",
                        response.body.decode("utf-8"),
                    )
                )
            if cviewstate is None or len(cviewstate) < 0:
                cviewstate = pdata_lot_page_period["__CVIEWSTATE"]
                eventvalidation = pdata_lot_page_period["__EVENTVALIDATION"]
            common_data["__EVENTTARGET"] = combo.serp.body_scripts()
            common_data["__EVENTARGUMENT"] = pdata_lot_page_period["__EVENTARGUMENT"]
            common_data["__CVIEWSTATE"] = cviewstate
            common_data["__VIEWSTATE"] = pdata_lot_page_period["__VIEWSTATE"]
            common_data["__SCROLLPOSITIONY"] = pdata_lot_page_period[
                "__SCROLLPOSITIONY"
            ]
            common_data["__EVENTVALIDATION"] = eventvalidation
            period_from_current_page = combo.offer.periods
            yield FormRequest(
                response.url,
                callback=self.parse_lot_page_offer_next_page,
                formdata=common_data,
                method="POST",
                cb_kwargs={
                    "loader": loader,
                    "lot_number": lot_number,
                    "general": general,
                    "period_current_page": period_from_current_page,
                    "pages": pages,
                    "post_data_period": common_data,
                },
                dont_filter=True,
            )

    async def parse_lot_page_offer_next_page(
        self,
        response,
        loader,
        lot_number,
        general,
        post_data_period,
        pages: list,
        period_current_page: list,
    ):
        combo = Combo(response=response)
        pages.pop(0)
        if len(pages) > 0:
            cviewstate = combo.mpost.get_post_data_values("input", "__CVIEWSTATE")
            eventvalidation = combo.mpost.get_post_data_values(
                "input", "__EVENTVALIDATION"
            )
            if cviewstate is None or len(cviewstate) < 0:
                cviewstate = "".join(
                    re.findall(
                        r"hiddenField\|__CVIEWSTATE\|(.*)\|",
                        response.body.decode("utf-8"),
                    )
                )
                eventvalidation = "".join(
                    re.findall(
                        r"hiddenField\|__EVENTVALIDATION\|(.*)\|.*\|asyncPostBackControlIDs",
                        response.body.decode("utf-8"),
                    )
                )
            if cviewstate is None or len(cviewstate) < 0:
                cviewstate = post_data_period["__CVIEWSTATE"]
                eventvalidation = post_data_period["__EVENTVALIDATION"]
            common_data["__EVENTTARGET"] = combo.serp.body_scripts()
            common_data["__EVENTARGUMENT"] = post_data_period["__EVENTARGUMENT"]
            common_data["__CVIEWSTATE"] = cviewstate
            common_data["__VIEWSTATE"] = post_data_period["__VIEWSTATE"]
            common_data["__SCROLLPOSITIONY"] = post_data_period["__SCROLLPOSITIONY"]
            common_data["__EVENTVALIDATION"] = eventvalidation
            period_from_current_page = combo.offer.periods
            period_current_page.extend(period_from_current_page)
            yield FormRequest(
                response.url,
                callback=self.parse_lot_page_offer_next_page,
                formdata=common_data,
                method="POST",
                cb_kwargs={
                    "loader": loader,
                    "lot_number": lot_number,
                    "general": general,
                    "period_current_page": period_current_page,
                    "pages": pages,
                    "post_data_period": common_data,
                },
                dont_filter=True,
            )
        else:
            error_ = combo.serp.find_error_page()
            if error_ is None:
                lot_num = combo.auc.lot_number_on_lot_page(response.url, lot_number)
                period_second_page = combo.offer.periods
                full_periods = period_current_page
                for dict_ in period_second_page:
                    full_periods.append(dict_)
                loader.add_value("status", combo.auc.status)
                loader.add_value(
                    "lot_id", "".join(re.findall(r"\d+", str(response.url)))
                )
                loader.add_value("lot_link", response.url)
                loader.add_value("lot_number", lot_num)
                loader.add_value("short_name", combo.auc.short_name)
                loader.add_value("lot_info", combo.auc.lot_info)
                loader.add_value(
                    "property_information", combo.offer.property_information
                )
                loader.add_value("periods", full_periods)
                start_date_request_offer = full_periods[0]["start_date_requests"]
                end_date_request_offer = full_periods[-1]["end_date_requests"]
                price_offer = full_periods[0]["current_price"]
                loader.add_value("start_date_requests", start_date_request_offer)
                loader.add_value("end_date_requests", end_date_request_offer)
                loader.add_value("start_date_trading", start_date_request_offer)
                loader.add_value("end_date_trading", end_date_request_offer)
                loader.add_value("start_price", price_offer)
                loader.add_value("categories", combo.auc.categories)
                _id = "".join(loader.get_collected_values("trading_id"))
                lot_file = combo.offer.download(self.name)
                loader.add_value("files", {"general": general, "lot": lot_file})
                yield loader.load_item()
            else:
                logger.error(f"TWO PAGE PERIODS ERROR ERROR, {response.url}")

    def parse_competiton_serp(self, response, first_post, trading_type: str):
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
        if combo.serp.body_scripts():
            data_next_page_post = combo.serp.body_scripts()
            first_post["ctl00$ctl00$BodyScripts$BodyScripts$scripts"] = (
                "ctl00$ctl00$MainContent$ContentPlaceHolderMiddle$UpdatePanel2|"
                + data_next_page_post
            )
            first_post["__CVIEWSTATE"] = cviewstate
            first_post["__EVENTVALIDATION"] = eventvalidation
            first_post["__EVENTTARGET"] = data_next_page_post
            if first_post.get(
                "ctl00$ctl00$MainExpandableArea$phExpandCollapse$SearchButton"
            ):
                del first_post[
                    "ctl00$ctl00$MainExpandableArea$phExpandCollapse$SearchButton"
                ]
            first_post[""] = ""
        for link in combo.serp.get_link_to_lot(current_page, self.data_origin):
            if link[0] not in self.previous_trades:
                yield Request(
                    link[0],
                    callback=self.parse_trade_page_competition,
                    cb_kwargs={"lot_number": link[1], "lot_link": link[2]},
                    dont_filter=True,
                )
        if current_page and next_page:
            if int(current_page) < int(next_page):
                yield FormRequest(
                    response.url,
                    formdata=first_post,
                    callback=self.parse_competiton_serp,
                    cb_kwargs={"first_post": first_post, "trading_type": trading_type},
                    dont_filter=True,
                )

    async def parse_trade_page_competition(self, response, lot_number, lot_link):
        combo = Combo(response=response)
        loader = EtpItemLoader(EtpItem(), response=response)
        loader.add_value("data_origin", self.data_origin)
        loader.add_value("property_type", self.property_type.value)
        loader.add_value("trading_id", "".join(re.findall(r"\d+", response.url)))
        loader.add_value("trading_link", response.url)
        loader.add_value("trading_number", combo.compet.trading_number)
        loader.add_value("trading_type", "competition")
        loader.add_value("trading_form", combo.compet.trading_form)
        loader.add_value("trading_org", combo.auc.trading_org)
        loader.add_value("trading_org_inn", combo.auc.trading_org_inn)
        loader.add_value("trading_org_contacts", combo.auc.trading_org_contacts)
        loader.add_value("msg_number", combo.compet.msg_number)
        loader.add_value("case_number", combo.auc.case_number)
        loader.add_value("debtor_inn", combo.auc.debtor_inn)
        loader.add_value("address", combo.auc.address)
        loader.add_value("arbit_manager", combo.auc.arbit_manager)
        loader.add_value("arbit_manager_inn", combo.auc.arbit_manager_inn)
        loader.add_value("arbit_manager_org", combo.auc.arbit_manager_org)
        loader.add_value("start_date_requests", combo.compet.start_date_requests)
        loader.add_value("end_date_requests", combo.compet.end_date_requests)
        loader.add_value("start_date_trading", combo.compet.start_date_trading)
        loader.add_value("end_date_trading", None)
        _id = "".join(loader.get_collected_values("trading_id"))
        general_files = combo.offer.download(self.name)
        common_data["__CVIEWSTATE"] = combo.mpost.get_post_data_values(
            "input", "__CVIEWSTATE"
        )
        common_data["__EVENTVALIDATION"] = combo.mpost.get_post_data_values(
            "input", "__EVENTVALIDATION"
        )
        common_data["__EVENTTARGET"] = combo.serp.body_scripts()
        common_data["__SCROLLPOSITIONY"] = str(randint(2289, 3662))
        yield Request(
            lot_link,
            callback=self.parse_lot_page_competition,
            cb_kwargs={
                "loader": loader,
                "lot_number": lot_number,
                "general": general_files,
            },
            dont_filter=True,
        )

    def parse_lot_page_competition(self, response, loader, lot_number, general: dict):
        """parse lot page Competition"""
        combo = Combo(response=response)
        lot_num = combo.auc.lot_number_on_lot_page(response.url, lot_number)
        if lot_number:
            loader.add_value("status", combo.auc.status)
            loader.add_value("lot_id", "".join(re.findall(r"\d+", str(response.url))))
            loader.add_value("lot_link", response.url)
            loader.add_value("lot_number", lot_num)
            loader.add_value("short_name", combo.auc.short_name)
            loader.add_value("lot_info", combo.auc.lot_info)
            loader.add_value("property_information", combo.compet.property_information)
            loader.add_value("start_price", combo.auc.start_price)
            loader.add_value("categories", combo.auc.categories)
            loader.add_value("step_price", combo.auc.step_price)
            _id = "".join(loader.get_collected_values("trading_id"))
            lot_file = combo.offer.download(self.name)
            loader.add_value("files", {"general": general, "lot": lot_file})
            yield loader.load_item()
