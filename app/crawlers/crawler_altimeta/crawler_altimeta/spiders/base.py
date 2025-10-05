import re
from scrapy import Request, FormRequest

from app.crawlers.items import EtpItem, EtpItemLoader
from app.crawlers.base import BaseSpider
from app.db.models import AuctionPropertyType
from app.utils import URL, logger
from app.utils.config import write_log_to_file
from ..manage_spiders.combo import Combo
from ..config import (
    data_origin,
    serp_link,
    lot_link,
    doc_link,
    url_file,
    query_param,
)


class AltimetaBaseSpider(BaseSpider):
    name = "base"
    property_type = AuctionPropertyType.bankruptcy
    custom_settings = {
        "LOG_FILE": f"{name}.log" if write_log_to_file else None,
    }

    @classmethod
    def set_links(cls):
        cls.data_origin = data_origin.get(cls.name)
        cls.lot_link = lot_link.get(cls.name)
        cls.serp_link = serp_link.get(cls.name)
        cls.doc_link = doc_link.get(cls.name)
        cls.main_url = url_file.get(cls.name)
        cls.start_url = [cls.serp_link]

    def __init__(self, *args, **kwargs):
        self.set_links()
        super().__init__(self.data_origin, *args, **kwargs)

    def start_requests(self):
        url = URL.unquote_url(self.start_url[0])
        yield Request(url, self.make_query_search)

    def make_query_search(self, response):
        yield FormRequest(
            response.url,
            callback=self.parse_serp,
            method="GET",
            formdata=query_param,
            dont_filter=True,
            cb_kwargs={"current_page": 1},
        )

    def parse_serp(self, response, current_page):
        combo = Combo(response_=response)
        if links := combo.serp.get_trading_number_from_serp_page():
            for link, trading_number in links:
                url = URL.unquote_url(
                    self.start_url[0].replace("/index.html", "").strip()
                )
                url = URL.url_join(url, link)
                if url not in self.previous_trades:
                    yield Request(
                        url,
                        callback=self.parse_trade_page,
                        dont_filter=True,
                        cb_kwargs={"trading_number": trading_number},
                    )
        next_page = combo.serp.get_one_next_link()
        if next_page:
            current_page += 1
            url = response.urljoin(next_page)
            yield Request(
                url,
                self.parse_serp,
                dont_filter=True,
                cb_kwargs={"current_page": current_page},
            )

    def parse_trade_page(self, response, trading_number):
        combo = Combo(response_=response)
        trading_form = combo.serp.trading_form
        if trading_form:
            trading_type = combo.serp.trading_type
            transfer = EtpItem()
            transfer["data_origin"] = self.data_origin
            id_trade = combo.serp.trading_id
            transfer["trading_id"] = id_trade
            transfer["trading_link"] = response.url
            transfer["trading_number"] = trading_number
            transfer["trading_type"] = trading_type
            transfer["trading_form"] = trading_form
            transfer["trading_org"] = combo.serp.trading_org
            transfer["trading_org_inn"] = None
            transfer["trading_org_contacts"] = combo.serp.trading_org_contacts
            transfer["msg_number"] = combo.serp.msg_number
            transfer["case_number"] = combo.serp.case_number
            transfer["debtor_inn"] = combo.serp.debtor_inn
            transfer["address"] = combo.serp.address
            transfer["arbit_manager"] = combo.serp.arbit_manager
            transfer["arbit_manager_inn"] = None
            transfer["arbit_manager_org"] = combo.serp.arbit_manager_org
            if trading_type == "auction" or trading_type == "competition":
                transfer["start_date_requests"] = combo.auc.start_date_requests
                transfer["end_date_requests"] = combo.auc.end_date_requests
                transfer["start_date_trading"] = combo.auc.start_date_trading
                transfer["end_date_trading"] = combo.auc.end_date_trading
            try:
                yield Request(
                    self.doc_link + f"{id_trade}&&id={id_trade}",
                    callback=self.parse_doc_page,
                    dont_filter=True,
                    cb_kwargs={
                        "transfer": transfer,
                        "_id": id_trade,
                        "trading_type": trading_type,
                    },
                )
            except Exception as e:
                logger.error(
                    f"{response.url} :: ERROR DURING REQUEST TO DOC PAGE {self.doc_link} {e}"
                )

    def parse_doc_page(self, response, transfer, _id, trading_type):
        """parse page with docs"""
        callback_func = None
        combo = Combo(response_=response)
        current_page = 1
        general_docs = combo.doc.general_docs(self.name)
        local_lot_link = (
            URL.unquote_url(self.lot_link) + f"{_id}&page={current_page}"
        )
        if trading_type == "auction":
            callback_func = self.parse_auction_lot
        if trading_type == "offer":
            callback_func = self.parse_offer_lot
        if trading_type == "competition":
            callback_func = self.parse_competition_lot
        if callback_func:
            yield Request(
                local_lot_link,
                callback=callback_func,
                dont_filter=True,
                cb_kwargs={
                    "general_docs": general_docs,
                    "current_page": current_page,
                    "transfer": transfer,
                    "link": local_lot_link,
                },
            )

    def parse_auction_lot(self, response, transfer, general_docs, current_page, link):
        """parse page with lots"""
        combo = Combo(response_=response)
        for table in combo.auc.get_all_lot_tables():
            loader = EtpItemLoader(EtpItem(), response=response)
            loader.add_value("data_origin", transfer["data_origin"])
            loader.add_value("property_type", self.property_type.value)
            loader.add_value("trading_id", transfer["trading_id"])
            loader.add_value("trading_link", transfer["trading_link"])
            loader.add_value("trading_number", transfer["trading_number"])
            loader.add_value("trading_type", transfer["trading_type"])
            loader.add_value("trading_form", transfer["trading_form"])
            loader.add_value("trading_org", transfer["trading_org"])
            loader.add_value("trading_org_inn", transfer["trading_org_inn"])
            loader.add_value("trading_org_contacts", transfer["trading_org_contacts"])
            loader.add_value("msg_number", transfer["msg_number"])
            loader.add_value("case_number", transfer["case_number"])
            loader.add_value("debtor_inn", transfer["debtor_inn"])
            loader.add_value("address", transfer["address"])
            loader.add_value("arbit_manager", transfer["arbit_manager"])
            loader.add_value("arbit_manager_inn", None)
            loader.add_value("arbit_manager_org", transfer["arbit_manager_org"])
            loader.add_value("status", combo.auc.get_status(table_=table))
            loader.add_value("start_date_requests", transfer["start_date_requests"])
            loader.add_value("end_date_requests", transfer["end_date_requests"])
            loader.add_value("start_date_trading", transfer["start_date_trading"])
            loader.add_value("end_date_trading", transfer["end_date_trading"])
            loader.add_value("lot_number", combo.auc.get_lot_number(table_=table))
            loader.add_value("short_name", combo.auc.get_short_name(table_=table))
            loader.add_value("lot_info", combo.auc.get_lot_info(table_=table))
            loader.add_value("categories", combo.auc.get_categories(table=table))
            loader.add_value(
                "property_information", combo.auc.get_property_info(table_=table)
            )
            loader.add_value("start_price", combo.auc.get_start_price(table_=table))
            loader.add_value("step_price", combo.auc.get_step_price(table_=table))
            lot_files = combo.doc.get_lot_docs(table_=table, crawler_name=self.name)
            loader.add_value("files", {"general": general_docs, "lot": lot_files})
            yield loader.load_item()

        next_page = combo.offer.get_next_page_number()
        if next_page:
            try:
                if isinstance(int(next_page), int):
                    current_page += 1
                    link = re.sub(r"page=\d+", f"page={current_page}", link)
                    yield Request(
                        link,
                        callback=self.parse_auction_lot,
                        dont_filter=True,
                        cb_kwargs={
                            "general_docs": general_docs,
                            "current_page": current_page,
                            "transfer": transfer,
                            "link": link,
                        },
                    )
            except Exception as e:
                logger.error(f"{response.url} :: ERROR NEXT PAGE {e}", exc_info=True)

    def parse_offer_lot(self, response, transfer, general_docs, current_page, link):
        combo = Combo(response_=response)
        for table in combo.offer.get_lot_tables():
            loader = EtpItemLoader(EtpItem(), response=response)
            loader.add_value("data_origin", transfer["data_origin"])
            loader.add_value("property_type", self.property_type.value)
            loader.add_value("trading_id", transfer["trading_id"])
            loader.add_value("trading_link", transfer["trading_link"])
            loader.add_value("trading_number", transfer["trading_number"])
            loader.add_value("trading_type", transfer["trading_type"])
            loader.add_value("trading_form", transfer["trading_form"])
            loader.add_value("trading_org", transfer["trading_org"])
            loader.add_value("trading_org_inn", transfer["trading_org_inn"])
            loader.add_value("trading_org_contacts", transfer["trading_org_contacts"])
            loader.add_value("msg_number", transfer["msg_number"])
            loader.add_value("case_number", transfer["case_number"])
            loader.add_value("debtor_inn", transfer["debtor_inn"])
            loader.add_value("address", transfer["address"])
            loader.add_value("arbit_manager", transfer["arbit_manager"])
            loader.add_value("arbit_manager_inn", None)
            loader.add_value("arbit_manager_org", transfer["arbit_manager_org"])
            loader.add_value("status", combo.auc.get_status(table_=table))
            loader.add_value("lot_number", combo.auc.get_lot_number(table_=table))
            loader.add_value("short_name", combo.auc.get_short_name(table_=table))
            loader.add_value("lot_info", combo.auc.get_lot_info(table_=table))
            loader.add_value("categories", combo.auc.get_categories(table=table))
            loader.add_value(
                "property_information", combo.auc.get_property_info(table_=table)
            )
            loader.add_value(
                "start_date_requests", combo.offer.get_start_date_requests(table_=table)
            )
            loader.add_value(
                "end_date_requests", combo.offer.get_end_date_requests(table_=table)
            )
            loader.add_value(
                "start_date_trading", combo.offer.get_start_date_trading(table_=table)
            )
            loader.add_value(
                "end_date_trading", combo.offer.get_end_date_trading(table_=table)
            )
            loader.add_value("periods", combo.offer.get_period(table_=table))
            loader.add_value("start_price", combo.offer.get_start_price_offer(table_=table))
            lot_files = combo.doc.get_lot_docs(table_=table, crawler_name=self.name)
            loader.add_value("files", {"general": general_docs, "lot": lot_files})
            yield loader.load_item()

        next_page = combo.offer.get_next_page_number()
        if next_page:
            try:
                if isinstance(int(next_page), int):
                    current_page += 1
                    link = re.sub(r"page=\d+", f"page={current_page}", link)
                    yield Request(
                        link,
                        callback=self.parse_offer_lot,
                        dont_filter=True,
                        cb_kwargs={
                            "general_docs": general_docs,
                            "current_page": current_page,
                            "transfer": transfer,
                            "link": link,
                        },
                    )
            except Exception as e:
                logger.error(f"{response.url} :: ERROR NEXT PAGE {e}", exc_info=True)

    def parse_competition_lot(
        self, response, transfer, general_docs, current_page, link
    ):
        combo = Combo(response_=response)
        for table in combo.auc.get_all_lot_tables():
            loader = EtpItemLoader(EtpItem(), response=response)
            loader.add_value("data_origin", transfer["data_origin"])
            loader.add_value("property_type", self.property_type.value)
            loader.add_value("trading_id", transfer["trading_id"])
            loader.add_value("trading_link", transfer["trading_link"])
            loader.add_value("trading_number", transfer["trading_number"])
            loader.add_value("trading_type", transfer["trading_type"])
            loader.add_value("trading_form", transfer["trading_form"])
            loader.add_value("trading_org", transfer["trading_org"])
            loader.add_value("trading_org_inn", transfer["trading_org_inn"])
            loader.add_value("trading_org_contacts", transfer["trading_org_contacts"])
            loader.add_value("msg_number", transfer["msg_number"])
            loader.add_value("case_number", transfer["case_number"])
            loader.add_value("debtor_inn", transfer["debtor_inn"])
            loader.add_value("address", transfer["address"])
            loader.add_value("arbit_manager", transfer["arbit_manager"])
            loader.add_value("arbit_manager_inn", None)
            loader.add_value("arbit_manager_org", transfer["arbit_manager_org"])
            loader.add_value("status", combo.auc.get_status(table_=table))
            loader.add_value("start_date_requests", transfer["start_date_requests"])
            loader.add_value("end_date_requests", transfer["end_date_requests"])
            loader.add_value("start_date_trading", transfer["start_date_trading"])
            loader.add_value("end_date_trading", transfer["end_date_trading"])
            loader.add_value("lot_number", combo.auc.get_lot_number(table_=table))
            loader.add_value("short_name", combo.auc.get_short_name(table_=table))
            loader.add_value("lot_info", combo.auc.get_lot_info(table_=table))
            loader.add_value(
                "property_information", combo.auc.get_property_info(table_=table)
            )
            loader.add_value("start_price", combo.auc.get_start_price(table_=table))
            loader.add_value("step_price", combo.auc.get_step_price(table_=table))
            lot_files = combo.doc.get_lot_docs(table_=table, crawler_name=self.name)
            loader.add_value("files", {"general": general_docs, "lot": lot_files})
            yield loader.load_item()

        next_page = combo.offer.get_next_page_number()
        if next_page:
            try:
                if isinstance(int(next_page), int):
                    current_page += 1
                    link = re.sub(r"page=\d+", f"page={current_page}", link)
                    yield Request(
                        link,
                        callback=self.parse_competition_lot,
                        dont_filter=True,
                        cb_kwargs={
                            "general_docs": general_docs,
                            "current_page": current_page,
                            "transfer": transfer,
                            "link": link,
                        },
                    )
            except Exception as e:
                logger.error(f"{response.url} :: ERROR NEXT PAGE {e}", exc_info=True)
