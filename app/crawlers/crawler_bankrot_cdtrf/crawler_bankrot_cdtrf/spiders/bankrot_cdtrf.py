import copy
import re

from scrapy import Request, FormRequest

from app.crawlers.items import EtpItemLoader, EtpItem
from app.db.models import AuctionPropertyType
from app.utils import logger
from ..locators_and_attributes.locators_attributes import Offer
from ..manage_spiders.combo import Compose
from app.crawlers.base import BaseSpider
from ..config import data_origin_url, start_date


class BankrotCDTRFSpider(BaseSpider):
    name = "bankrot_cdtrf"
    property_type = AuctionPropertyType.bankruptcy

    def __init__(self):
        super().__init__(data_origin_url)

    def start_requests(self):
        yield Request(
            "https://bankrot.cdtrf.ru/public/undef/card/tradel.aspx",
            self.making_post_request,
        )

    def making_post_request(self, response):
        combo = Compose(response_=response)
        format_post_data = dict()
        format_post_data["ctl00_ToolkitScriptManager1_HiddenField"] = (
            combo.offer.get_ajax_and_token()
        )
        format_post_data["ctl00$ToolkitScriptManager1"] = (
            Offer.ToolkitScriptManager1_first_query
        )
        format_post_data["ctl00$cph1$tbRequestTimeBegin1"] = start_date
        format_post_data["ctl00$cph1$pgvTrades$ctl22$ddlPager"] = "Номер страницы"
        format_post_data["ctl00$cph1$hiddenRequestTimeBegin1"] = start_date
        format_post_data["ctl00$cph1$hiddenPriceTypeID"] = "0"
        format_post_data["ctl00$cph1$hiddenFilterShowed"] = "1"
        format_post_data["ctl00$cph1$ddlPriceTypeID"] = "0"
        format_post_data["__VIEWSTATEGENERATOR"] = combo.offer.get_post_data_values(
            "input", "__VIEWSTATEGENERATOR"
        )
        format_post_data["__VIEWSTATE"] = combo.offer.get_post_data_values(
            "input", "__VIEWSTATE"
        )
        format_post_data["__PREVIOUSPAGE"] = combo.offer.get_post_data_values(
            "input", "__PREVIOUSPAGE"
        )
        format_post_data["__LASTFOCUS"] = combo.offer.get_post_data_values(
            "input", "__LASTFOCUS"
        )
        format_post_data["__EVENTVALIDATION"] = combo.offer.get_post_data_values(
            "input", "__EVENTVALIDATION"
        )
        format_post_data["__EVENTTARGET"] = Offer.EVENTTARGET_1st_post
        format_post_data["__EVENTARGUMENT"] = combo.offer.get_post_data_values(
            "input", "__EVENTARGUMENT"
        )
        format_post_data["__ASYNCPOST"] = "true"
        format_post_data["ctl00$cph1$ddlTradeTypeID"] = "0"
        yield FormRequest(
            response.url,
            callback=self.parse_serp,
            formdata=format_post_data,
            cb_kwargs={"format_post_data": format_post_data, "current_page": 1},
        )

    def parse_serp(self, response, format_post_data, current_page):
        combo = Compose(response_=response)
        list_tag_links = combo.offer.trade_link_serp
        for link in list_tag_links:
            if link not in self.previous_trades:
                self.previous_trades.append(link)
                yield Request(link, callback=self.parse_auction_page)
        next_page = response.css("#ctl00_cph1_pgvTrades_ctl22_lnkNext").get()
        last_page_visible = combo.offer.get_total_visible_pages(
            current_page, format_post_data["ctl00$cph1$tbRequestTimeBegin1"]
        )
        total_pages = combo.offer.get_total_pages()
        logger.info(f"Current page: {current_page}/{total_pages}")
        current_page += 1
        pagination_form = copy.deepcopy(format_post_data)
        pagination_form["ctl00$ToolkitScriptManager1"] = (
            "ctl00$cph1$upList|ctl00$cph1$pgvTrades$ctl22$lnkNext"
        )
        pagination_form["ctl00$cph1$pgvTrades$ctl22$ddlPager"] = "Номер страницы"
        pagination_form["__EVENTTARGET"] = Offer.EVENTTARGET_next_page
        EVENTVALIDATION = combo.offer.get_post_data_values("input", "__EVENTVALIDATION")
        if len(EVENTVALIDATION) > 0:
            pagination_form["__EVENTVALIDATION"] = EVENTVALIDATION
        pagination_form["ctl00$cph1$hiddenPrepare"] = "0"
        pagination_form["ctl00$cph1$hiddenFormed"] = "0"
        pagination_form["ctl00$cph1$hiddenRegister"] = "0"
        pagination_form["ctl00$cph1$hiddenDeclare"] = "0"
        pagination_form["ctl00$cph1$hiddenRecieveReq"] = "0"
        pagination_form["ctl00$cph1$hiddenDefinePart"] = "0"
        pagination_form["ctl00$cph1$hiddenTradeGo"] = "0"
        pagination_form["ctl00$cph1$hiddenSummingUp"] = "0"
        pagination_form["ctl00$cph1$hiddenComplete"] = "0"
        pagination_form["ctl00$cph1$hiddenNotHeld"] = "0"
        pagination_form["ctl00$cph1$hiddenSignContract"] = "0"
        pagination_form["ctl00$cph1$hiddenSuspend"] = "0"
        pagination_form["ctl00$cph1$hiddenCancel"] = "0"
        pagination_form["ctl00$cph1$hiddenDelete"] = "0"
        pagination_form["ctl00$cph1$hiddenNotProt"] = "0"
        viewstate = "".join(
            re.findall(
                r"hiddenField\|__VIEWSTATE\|(.*)\|.*\|hiddenField\|__VIEWSTATEGENERATOR\|",
                response.body.decode("utf-8"),
            )
        )
        previouspage = "".join(
            re.findall(
                r"hiddenField\|__PREVIOUSPAGE\|(.*)\|.*\|hiddenField\|__EVENTVALIDATION\|",
                response.body.decode("utf-8"),
            )
        )
        eventvalidation = "".join(
            re.findall(
                r"hiddenField\|__EVENTVALIDATION\|(.*)\|.*\|asyncPostBackControlIDs\|",
                response.body.decode("utf-8"),
            )
        )
        if len(viewstate) > 0:
            pagination_form["__VIEWSTATE"] = viewstate
        if len(previouspage) > 0:
            pagination_form["__PREVIOUSPAGE"] = previouspage
        if len(eventvalidation) > 0:
            pagination_form["__EVENTVALIDATION"] = eventvalidation
        if next_page and current_page <= last_page_visible and current_page < 2400:
            yield FormRequest(
                response.url,
                callback=self.parse_serp,
                formdata=pagination_form,
                dont_filter=True,
                method="POST",
                cb_kwargs={
                    "format_post_data": pagination_form,
                    "current_page": current_page,
                },
            )

    async def parse_auction_page(self, response):
        combo = Compose(response_=response)
        loader = EtpItemLoader(EtpItem(), response=response)
        trading_id = "".join(re.findall(r"\d+$", response.url))
        trading_type_2 = combo.get_trading_type
        loader.add_value("data_origin", data_origin_url)
        loader.add_value("property_type", self.property_type.value)
        loader.add_value("trading_id", trading_id)
        loader.add_value("trading_link", response.url)
        loader.add_value("trading_number", combo.offer.trading_number)
        loader.add_value("trading_type", trading_type_2)
        loader.add_value("trading_form", combo.offer.trading_form)
        loader.add_value("status", combo.offer.status)
        loader.add_value("trading_org", combo.offer.trading_org)
        loader.add_value("trading_org_inn", combo.offer.trading_org_inn)
        loader.add_value("trading_org_contacts", combo.offer.trading_org_contacts)
        loader.add_value("msg_number", combo.offer.msg_number)
        loader.add_value("case_number", combo.offer.case_number)
        loader.add_value("debtor_inn", combo.offer.debtor_inn)
        loader.add_value("address", combo.offer.address)
        loader.add_value("arbit_manager", combo.offer.arbit_manager)
        loader.add_value("arbit_manager_inn", combo.offer.arbit_manager_inn)
        loader.add_value("arbit_manager_org", combo.offer.arbit_manager_org)
        loader.add_value("short_name", combo.offer.lot_info)
        loader.add_value("lot_info", combo.offer.short_name)
        loader.add_value("lot_number", combo.offer.lot_number)
        loader.add_value("property_information", combo.offer.property_information)
        loader.add_value("start_date_requests", combo.auction.start_date_requests)
        loader.add_value("end_date_requests", combo.auction.end_date_requests)
        loader.add_value("start_date_trading", combo.auction.start_date_trading)
        loader.add_value("start_price", combo.auction.start_price)
        if trading_type_2 in ("auction", "competition"):
            loader.add_value("step_price", combo.auction.step_price)
            loader.add_value("end_date_trading", combo.auction.end_date_trading)
        else:
            loader.add_value("end_date_trading", combo.offer.end_date_trading)
            loader.add_value("periods", combo.offer.periods)
        loader.add_value("categories", None)
        link_to_lot_file = combo.auction.clean_files_lot_links
        link_to_doc_1 = combo.auction.general_file_link_doc_1()
        link_to_doc_2 = combo.auction.general_file_link_doc_2()
        yield Request(
            link_to_doc_1,
            callback=self.get_document_1,
            cb_kwargs={
                "loader": loader,
                "lot_files": list(),
                "link_to_doc_2": link_to_doc_2,
                "lot_link": response.url,
                "link_to_lot_file": link_to_lot_file,
            },
        )

    async def get_document_1(
        self, response, loader, lot_files, link_to_doc_2, lot_link, link_to_lot_file
    ):
        """get document for general"""
        combo = Compose(response_=response)
        get_files_lst = combo.auction.find_all_files(lot_link)
        yield Request(
            link_to_doc_2,
            callback=self.get_document_2,
            cb_kwargs={
                "loader": loader,
                "lot_files": lot_files,
                "files_gen_2": get_files_lst,
                "lot_link": lot_link,
                "link_to_lot_file": link_to_lot_file,
            },
        )

    async def get_document_2(
        self, response, loader, lot_files, files_gen_2, lot_link, link_to_lot_file
    ):
        combo = Compose(response_=response)
        get_files_lst_2 = combo.auction.find_all_files(lot_link)
        get_files_lst_2.extend(files_gen_2)
        general_files_dict = combo.auction.download(get_files_lst_2)
        if link_to_lot_file:
            if isinstance(link_to_lot_file, set) and len(link_to_lot_file) > 0:
                link_to_lot_file = list(link_to_lot_file)
                link = link_to_lot_file.pop(0)
                yield Request(
                    link,
                    callback=self.lot_doc_page,
                    cb_kwargs={
                        "loader": loader,
                        "lot_files": lot_files,
                        "general_files_dict": general_files_dict,
                        "lot_link": lot_link,
                        "link_to_lot_file": link_to_lot_file,
                    },
                )
        else:
            lot_files = list()
            loader.add_value("files", {"general": general_files_dict, "lot": lot_files})
            yield loader.load_item()

    def lot_doc_page(
        self,
        response,
        loader,
        general_files_dict,
        lot_link,
        link_to_lot_file,
        lot_files: list,
    ):
        combo = Compose(response_=response)
        files_on_page = combo.auction.find_all_files(lot_link)
        lot_files.extend(files_on_page)
        if len(link_to_lot_file) == 0:
            l_files = combo.auction.download(lot_files)
            loader.add_value("files", {"general": general_files_dict, "lot": l_files})
            yield loader.load_item()
        else:
            link = link_to_lot_file.pop(0)
            yield Request(
                link,
                callback=self.lot_doc_page,
                cb_kwargs={
                    "loader": loader,
                    "lot_files": lot_files,
                    "general_files_dict": general_files_dict,
                    "lot_link": lot_link,
                    "link_to_lot_file": link_to_lot_file,
                },
            )
