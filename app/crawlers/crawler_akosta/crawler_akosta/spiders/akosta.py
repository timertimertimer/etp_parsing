import copy
from datetime import datetime
from pprint import pprint

from scrapy import Request, FormRequest

from app.crawlers.base import BaseSpider
from app.utils import DateTimeHelper, logger
from app.utils.config import start_date
from app.crawlers.items import EtpItem, EtpItemLoader
from app.db.models import Auction, AuctionPropertyType
from ..manage_spider.combo import Combo
from ..utils.config import (
    search_link,
    data_origin,
    common_link,
    debtor_link,
    lot_link,
    link_post_period,
    urls,
    post_headers,
)
from ..utils.post_data import (
    post_date_dict,
    post_data_pagination,
    post_data_to_trade,
    post_panel_list_dict,
    post_data_debitor,
    post_data_lot_tab,
    post_data_unique_lot_page,
    post_data_period_offer_page,
    property_type_sgtable_id_map,
    post_property_type_choose_dict,
)


def _parse_response(response, post_data: dict):
    combo = Combo(response)
    viewstate = combo.pre.get_post_data_values("input", "j_id1:javax.faces.ViewState:0")
    data = copy.deepcopy(post_data)
    data["formMain:inputServerTime"] = DateTimeHelper.format_datetime(
        datetime.now(), "%H:%M:%S"
    )
    data["javax.faces.ViewState"] = viewstate
    return data


class AkostaBaseSpider(BaseSpider):
    name = "akosta"

    def __init__(self):
        self.sg_table_id = property_type_sgtable_id_map[self.property_type.value]
        super(AkostaBaseSpider, self).__init__(data_origin, {Auction.ext_id})

    def start_requests(self):
        yield Request(
            urls[self.name],
            self.make_table_list,
        )

    def make_table_list(self, response, **kwargs):
        data = _parse_response(response, post_panel_list_dict)
        print("make_table_list")
        pprint(data)
        yield FormRequest(
            search_link,
            callback=self.refresh_panel_list,
            formdata=data,
            dont_filter=True,
            headers=post_headers,
        )

    def refresh_panel_list(self, response):
        yield Request(
            response.url,
            self.choose_property_type,
            dont_filter=True,
        )

    def choose_property_type(self, response):
        data = _parse_response(response, post_property_type_choose_dict)
        data = data | {
            "javax.faces.source": f"formMain:sgTable:{self.sg_table_id}:j_idt92",
            f"formMain:sgTable:{self.sg_table_id}:j_idt92_input": "on",
        }
        print("choose_property_type")
        pprint(data)
        yield FormRequest(
            search_link,
            callback=self.choose_date_range,
            formdata=data,
            dont_filter=True,
            cb_kwargs={"view_state": data["javax.faces.ViewState"]},
            headers=post_headers,
        )

    def choose_date_range(self, response, view_state):
        data = _parse_response(response, post_date_dict)
        data["javax.faces.ViewState"] = view_state
        data["formMain:fromIdAcceptancePeriod_input"] = start_date
        data[f"formMain:sgTable:{self.sg_table_id}:j_idt92_input"] = "on"
        print("choose_date_range")
        pprint(data)
        yield FormRequest(
            search_link,
            callback=self.refresh_date_range,
            formdata=data,
            dont_filter=True,
            headers=post_headers,
        )

    def refresh_date_range(self, response):
        yield Request(
            response.url,
            self.parse_trades,
            cb_kwargs={"page_number": 1, "total_pages": 0, "viewstate": None},
            dont_filter=True,
        )

    def parse_trades(self, response, page_number, total_pages, viewstate):
        combo = Combo(response)
        sources = dict()
        if page_number == 1:
            current_page, total_pages = combo.pre.get_total_and_current_page()
            trades = combo.pre.get_trade_links()
            logger.info(
                f"{self.name} | Found {len(trades)} trades on {current_page} page"
            )
            for tag_tr in trades:
                data, id_ = combo.pre.get_post_id_and_trading_id(tag_tr)
                if id_ in self.previous_trades:
                    continue
                if id_ not in sources:
                    sources[id_] = data
        else:
            for id_, data in combo.pre.get_trade_links_2().items():
                if id_ in self.previous_trades:
                    continue
                if id_ not in sources:
                    sources[id_] = data
        yield from self.process_trade_one_by_one(
            response, sources, page_number, total_pages, viewstate
        )

    def process_trade_one_by_one(
        self, response, sources, page_number, total_pages, viewstate
    ):
        combo = Combo(response)
        viewstate = viewstate or combo.pre.get_post_data_values(
            "input", "j_id1:javax.faces.ViewState:0"
        )
        if sources:
            id_, data = sources.popitem()
            post_data = copy.deepcopy(post_data_to_trade)
            post_data["javax.faces.source"] = data
            post_data["formMain:inputServerTime"] = DateTimeHelper.format_datetime(
                datetime.now(), "%H:%M:%S"
            )
            post_data["formMain:fromIdAcceptancePeriod_input"] = start_date
            post_data["javax.faces.ViewState"] = viewstate
            post_data[data] = data
            yield FormRequest(
                search_link,
                self.redirect_trade_page,
                formdata=post_data,
                dont_filter=True,
                cb_kwargs={
                    "sources": sources,
                    "page_number": page_number,
                    "total_pages": total_pages,
                    "trading_id": id_,
                },
                headers=post_headers,
            )
        else:
            if page_number < total_pages:
                page_number += 1
                data_lots = int(page_number) * 50 - 50
                post_data_pagination["formMain:lotListTable_first"] = str(data_lots)
                post_data_pagination["formMain:inputServerTime"] = (
                    DateTimeHelper.format_datetime(datetime.now(), "%H:%M:%S")
                )
                post_data_pagination["javax.faces.ViewState"] = viewstate
                post_data_pagination[
                    f"formMain:sgTable:{property_type_sgtable_id_map[self.property_type.value]}:j_idt92_input"
                ] = "on"
                yield FormRequest(
                    response.url,
                    callback=self.parse_trades,
                    formdata=post_data_pagination,
                    dont_filter=True,
                    cb_kwargs={
                        "page_number": page_number,
                        "total_pages": total_pages,
                        "viewstate": viewstate,
                    },
                    headers=post_headers,
                )

    def redirect_trade_page(
        self, response, trading_id, sources, page_number, total_pages
    ):
        combo = Combo(_response=response)
        url_to_trade = combo.main_.get_link_redirect()
        if url_to_trade:
            yield Request(
                url_to_trade,
                self.parse_trade_page,
                dont_filter=True,
                cb_kwargs={
                    "sources": sources,
                    "page_number": page_number,
                    "total_pages": total_pages,
                    "trading_id": trading_id,
                },
            )

    def parse_trade_page(self, response, sources, page_number, total_pages, trading_id):
        combo = Combo(_response=response)
        transfer = EtpItem()
        transfer["data_origin"] = data_origin
        transfer["trading_id"] = trading_id
        transfer["trading_link"] = response.url
        trading_type = combo.trade.trading_type
        transfer["trading_type"] = trading_type
        transfer["trading_form"] = combo.trade.trading_form
        transfer["trading_org"] = combo.trade.trading_org
        transfer["trading_org_contacts"] = combo.trade.trading_org_contacts
        if trading_type in ("auction", "competition"):
            transfer["start_date_requests"] = combo.main_.start_date_requests
            transfer["end_date_requests"] = combo.main_.end_date_requests
            transfer["start_date_trading"] = combo.main_.start_date_trading
            transfer["end_date_trading"] = combo.main_.end_date_trading

        # !!! DOCS !!!
        new_view = combo.pre.get_post_data_values(
            "input", "j_id1:javax.faces.ViewState:0"
        )
        general_files = combo.main_.download_trade(
            url=common_link,
            view=new_view,
            cookies=response.request.headers["Cookie"].decode(),
        )

        post_data = copy.deepcopy(post_data_debitor)
        post_data["formMain:inputServerTime"] = DateTimeHelper.format_datetime(
            datetime.now(), "%H:%M:%S"
        )
        post_data["javax.faces.ViewState"] = new_view
        for form_number_search in combo.deb.find_correct_form_number_collapsed():
            post_data[form_number_search] = "false"
        form_number = combo.deb.find_correct_form_number()
        post_data[form_number] = form_number
        yield FormRequest(
            common_link,
            callback=self.parse_debitor,
            dont_filter=True,
            formdata=post_data,
            cb_kwargs={
                "transfer": transfer,
                "trading_type": trading_type,
                "general_files": general_files,
                "sources": sources,
                "page_number": page_number,
                "total_pages": total_pages,
            }
        )

    def parse_debitor(
        self,
        response,
        transfer,
        trading_type,
        general_files,
        sources,
        page_number,
        total_pages,
    ):
        combo = Combo(_response=response)
        debtor_view_state = combo.pre.get_post_data_values(
            "input", "j_id1:javax.faces.ViewState:0"
        )
        transfer["trading_number"] = combo.deb.trading_number
        transfer["msg_number"] = combo.deb.msg_number
        transfer["case_number"] = combo.deb.case_number
        transfer["arbit_manager_inn"] = combo.deb.arbit_manager_inn
        transfer["arbit_manager"] = combo.deb.arbit_manager
        transfer["arbit_manager_org"] = combo.deb.arbit_manager_org
        transfer["debtor_inn"] = combo.deb.debtor_inn
        if (
            combo.deb.soup.find("input", type="checkbox").get("checked")
            or transfer["trading_org"] == transfer["arbit_manager"]
        ):
            transfer["trading_org_inn"] = transfer["arbit_manager_inn"]
        transfer["address"] = combo.deb.debtor_address
        post_data_lot_tab["formMain:inputServerTime"] = DateTimeHelper.format_datetime(
            datetime.now(), "%H:%M:%S"
        )
        post_data_lot_tab["javax.faces.ViewState"] = debtor_view_state
        yield FormRequest(
            debtor_link,
            callback=self.parse_lot_tab,
            formdata=post_data_lot_tab,
            dont_filter=True,
            cb_kwargs={
                "transfer": transfer,
                "trading_type": trading_type,
                "general_files": general_files,
                "lots": None,
                "sources": sources,
                "page_number": page_number,
                "total_pages": total_pages,
            }
        )

    def parse_lot_tab(
        self,
        response,
        transfer,
        trading_type,
        general_files,
        lots,
        sources,
        page_number,
        total_pages,
        current_lot=None,
    ):
        """fetch post data to all unique lot and make post request"""
        combo = Combo(_response=response)
        lot_tab_link = response.url
        if not current_lot:
            lots = lots if lots else combo.trade.get_post_lot_data()
            current_lot = lots.pop(0)
        post_lot = copy.deepcopy(post_data_unique_lot_page)
        post_lot["javax.faces.source"] = current_lot
        post_lot[current_lot] = current_lot
        post_lot["formMain:inputServerTime"] = DateTimeHelper.format_datetime(
            datetime.now(), "%H:%M:%S"
        )
        viewstate = combo.pre.get_post_data_values(
            "input", "j_id1:javax.faces.ViewState:0"
        )
        post_lot["javax.faces.ViewState"] = viewstate
        lot_number = combo.trade.get_lot_number(_id=current_lot)
        yield FormRequest(
            lot_link,
            callback=self.parse_pre_lot_page,
            formdata=post_lot,
            dont_filter=True,
            cb_kwargs={
                "general_files": general_files,
                "trading_type": trading_type,
                "transfer": transfer,
                "lot_number": lot_number,
                "sources": sources,
                "page_number": page_number,
                "total_pages": total_pages,
                "lots": lots,
                "current_lot": current_lot,
                "lot_tab_link": lot_tab_link,
            }
        )
        if len(lots) > 0:
            yield Request(
                lot_tab_link,
                callback=self.parse_lot_tab,
                cb_kwargs={
                    "transfer": transfer,
                    "trading_type": trading_type,
                    "general_files": general_files,
                    "lots": lots,
                    "sources": sources,
                    "page_number": page_number,
                    "total_pages": total_pages,
                },
                dont_filter=True,
            )
        else:
            yield Request(
                search_link,
                self.process_trade_one_by_one,
                dont_filter=True,
                cb_kwargs={
                    "sources": sources,
                    "page_number": page_number,
                    "total_pages": total_pages,
                    "viewstate": None,
                },
            )

    def parse_pre_lot_page(
        self,
        response,
        transfer,
        trading_type,
        general_files,
        lot_number,
        sources,
        page_number,
        total_pages,
        lots,
        current_lot,
        lot_tab_link,
    ):
        combo = Combo(_response=response)
        url_to_trade = combo.main_.get_link_redirect()
        if url_to_trade:
            if trading_type == "offer":
                yield Request(
                    url_to_trade,
                    callback=self.parse_lot_offer,
                    dont_filter=True,
                    cb_kwargs={
                        "transfer": transfer,
                        "url_to_trade": url_to_trade,
                        "lot_number": lot_number,
                        "general_files": general_files,
                        "sources": sources,
                        "page_number": page_number,
                        "total_pages": total_pages,
                    },
                )
            if trading_type == "auction":
                yield Request(
                    url_to_trade,
                    callback=self.parse_lot_auction,
                    dont_filter=True,
                    cb_kwargs={
                        "transfer": transfer,
                        "url_to_trade": url_to_trade,
                        "lot_number": lot_number,
                        "general_files": general_files,
                        "sources": sources,
                        "page_number": page_number,
                        "total_pages": total_pages,
                    },
                )

            if trading_type == "competition":
                yield Request(
                    url_to_trade,
                    callback=self.parse_lot_auction,
                    dont_filter=True,
                    cb_kwargs={
                        "transfer": transfer,
                        "url_to_trade": url_to_trade,
                        "lot_number": lot_number,
                        "general_files": general_files,
                        "sources": sources,
                        "page_number": page_number,
                        "total_pages": total_pages,
                    },
                )
        else:
            yield Request(
                lot_link,
                callback=self.parse_lot_tab,
                cb_kwargs={
                    "transfer": transfer,
                    "trading_type": trading_type,
                    "general_files": general_files,
                    "lots": lots,
                    "sources": sources,
                    "page_number": page_number,
                    "total_pages": total_pages,
                    "current_lot": current_lot,
                },
                dont_filter=True,
            )

    def parse_lot_offer(
        self,
        response,
        url_to_trade,
        transfer,
        lot_number,
        general_files: list,
        sources,
        page_number,
        total_pages,
    ):
        combo = Combo(_response=response)
        loader = EtpItemLoader(EtpItem(), response=response)
        loader.add_value("data_origin", transfer["data_origin"])
        loader.add_value("property_type", self.property_type.value)
        loader.add_value("trading_id", transfer["trading_id"])
        loader.add_value("trading_link", transfer["trading_link"])
        loader.add_value("trading_type", transfer["trading_type"])
        loader.add_value("trading_form", transfer["trading_form"])
        loader.add_value("trading_org", transfer["trading_org"])
        loader.add_value("trading_org_inn", transfer["trading_org_inn"])
        loader.add_value("trading_org_contacts", transfer["trading_org_contacts"])
        loader.add_value("trading_number", transfer["trading_number"])
        loader.add_value("msg_number", transfer["msg_number"])
        loader.add_value("case_number", transfer["case_number"])
        loader.add_value("debtor_inn", transfer["debtor_inn"])
        loader.add_value("address", transfer["address"])
        loader.add_value("arbit_manager", transfer["arbit_manager"])
        loader.add_value("arbit_manager_inn", transfer["arbit_manager_inn"])
        loader.add_value("arbit_manager_org", transfer["arbit_manager_org"])
        loader.add_value("status", combo.auc.lot_status)
        loader.add_value("lot_id", None)
        loader.add_value("lot_link", response.url)
        loader.add_value("lot_number", lot_number)
        loader.add_value("short_name", combo.auc.get_short_name(lot_number))
        loader.add_value("lot_info", combo.auc.lot_info)
        loader.add_value("property_information", combo.auc.property_information)
        loader.add_value("start_price", combo.start_price)
        loader.add_value("categories", combo.categories)
        lot_files = combo.download_lot()
        loader.add_value("files", dict(general=general_files, lot=lot_files))
        period_first_page = combo.offer.periods
        total_pages_period = combo.offer.return_period_pagination()
        # total_pages_period & total are info about how many pages has pariod table
        if total_pages_period:
            total = copy.deepcopy(total_pages_period)
            del total_pages_period
        else:
            total = 1
        if total > 1:
            _form = copy.deepcopy(post_data_period_offer_page)
            rsl_selection = combo.pre.get_post_data_values(
                tag_html="input", post_argument="formMain:dataRSList_selection"
            )
            _form["formMain:dataRSList_selection"] = rsl_selection
            lot_viewstate2 = combo.pre.get_post_data_values(
                "input", "j_id1:javax.faces.ViewState:0"
            )
            _form["javax.faces.ViewState"] = lot_viewstate2
            _form["formMain:inputServerTime"] = DateTimeHelper.format_datetime(
                datetime.now(), "%H:%M:%S"
            )
            # param data depend from page number -> second page has value - 10
            _form["formMain:dataRSList_first"] = str(10 * 2 - 10)
            if combo.offer.get_refresh_form_j_idt55():
                _form["formMain:j_idt55"] = combo.offer.get_refresh_form_j_idt55()
            yield FormRequest(
                link_post_period,
                callback=self.parse_period_offer_pages,
                formdata=_form,
                dont_filter=True,
                cb_kwargs={
                    "loader": loader,
                    "_form": _form,
                    "periods_": period_first_page,
                    "current": 1,
                    "total": total,
                    "sources": sources,
                    "page_number": page_number,
                }
            )
        else:
            loader.add_value(
                "start_date_requests",
                combo.offer.get_start_date_request(period_first_page),
            )
            loader.add_value(
                "end_date_requests", combo.offer.get_end_date_request(period_first_page)
            )
            loader.add_value(
                "start_date_trading",
                combo.offer.get_start_date_request(period_first_page),
            )
            loader.add_value(
                "end_date_trading", combo.offer.get_end_date_request(period_first_page)
            )
            loader.add_value("periods", period_first_page)
            yield loader.load_item()

    def parse_period_offer_pages(
        self,
        response,
        loader,
        _form,
        current,
        total,
        periods_: list,
        sources,
        page_number,
    ):
        combo = Combo(_response=response)
        next_periods: list = combo.offer.return_next_periods()
        periods_.extend(next_periods)
        if current < total:
            current += 1
            _form["formMain:dataRSList_first"] = str(10 * current - 10)
            _form["formMain:inputServerTime"] = DateTimeHelper.format_datetime(
                datetime.now(), "%H:%M:%S"
            )
            yield FormRequest(
                link_post_period,
                callback=self.parse_period_offer_pages,
                formdata=_form,
                dont_filter=True,
                cb_kwargs={
                    "loader": loader,
                    "_form": _form,
                    "periods_": periods_,
                    "current": current,
                    "total": total,
                    "sources": sources,
                    "page_number": page_number,
                }
            )
        else:
            loader.add_value("periods", periods_)
            loader.add_value(
                "start_date_requests", combo.offer.get_start_date_request(periods_)
            )
            loader.add_value(
                "end_date_requests", combo.offer.get_end_date_request(periods_)
            )
            loader.add_value(
                "start_date_trading", combo.offer.get_start_date_request(periods_)
            )
            loader.add_value(
                "end_date_trading", combo.offer.get_end_date_request(periods_)
            )
            yield loader.load_item()

    def parse_lot_auction(
        self,
        response,
        url_to_trade,
        transfer,
        lot_number,
        general_files,
        sources,
        page_number,
        total_pages,
    ):
        combo = Combo(_response=response)
        loader = EtpItemLoader(EtpItem(), response=response)
        loader.add_value("data_origin", transfer["data_origin"])
        loader.add_value("property_type", self.property_type.value)
        loader.add_value("trading_id", transfer["trading_id"])
        loader.add_value("trading_link", transfer["trading_link"])
        loader.add_value("trading_type", transfer["trading_type"])
        loader.add_value("trading_form", transfer["trading_form"])
        loader.add_value("trading_org", transfer["trading_org"])
        loader.add_value("trading_org_inn", transfer.get("trading_org_inn"))
        loader.add_value("trading_org_contacts", transfer["trading_org_contacts"])
        loader.add_value("trading_number", transfer["trading_number"])
        loader.add_value("msg_number", transfer["msg_number"])
        loader.add_value("case_number", transfer["case_number"])
        loader.add_value("debtor_inn", transfer["debtor_inn"])
        loader.add_value("address", transfer["address"])
        loader.add_value("arbit_manager", transfer["arbit_manager"])
        loader.add_value("arbit_manager_inn", transfer["arbit_manager_inn"])
        loader.add_value("arbit_manager_org", transfer["arbit_manager_org"])
        loader.add_value("start_date_requests", transfer["start_date_requests"])
        loader.add_value("end_date_requests", transfer["end_date_requests"])
        loader.add_value("start_date_trading", transfer["start_date_trading"])
        loader.add_value("end_date_trading", transfer["end_date_trading"])
        loader.add_value("status", combo.auc.lot_status)
        loader.add_value("lot_id", None)
        loader.add_value("lot_link", response.url)
        loader.add_value("lot_number", lot_number)
        loader.add_value("short_name", combo.auc.get_short_name(lot_number))
        loader.add_value("lot_info", combo.auc.lot_info)
        loader.add_value("property_information", combo.auc.property_information)
        loader.add_value("start_price", combo.start_price)
        loader.add_value("step_price", combo.step_price)
        loader.add_value("categories", combo.categories)
        lot_files = combo.download_lot()
        loader.add_value("files", dict(general=general_files, lot=lot_files))
        yield loader.load_item()


class AkostaArrestedSpider(AkostaBaseSpider):
    name = "akosta_arrested"
    property_type = AuctionPropertyType.arrested


class AkostaBankruptcySpider(AkostaBaseSpider):
    name = "akosta_bankruptcy"
    property_type = AuctionPropertyType.bankruptcy


class AkostaCommercialSpider(AkostaBaseSpider):
    name = "akosta_commercial"
    property_type = AuctionPropertyType.commercial
