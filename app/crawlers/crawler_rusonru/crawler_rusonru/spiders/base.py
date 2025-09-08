from scrapy import Request, FormRequest

from app.crawlers.base import BaseSpider
from app.utils.config import write_log_to_file
from app.utils import URL
from ..trades.combo import Combo
from ..config import trade_link, data_origin, serp_link, formdata
from app.crawlers.items import EtpItem, EtpItemLoader


class RusonBaseSpider(BaseSpider):
    name = "base"
    property_type = None
    custom_settings = {
        "LOG_FILE": f"{name}.log" if write_log_to_file else None,
    }

    def __init__(self):
        super().__init__(data_origin[self.name])

    def start_requests(self):
        yield FormRequest(
            url=serp_link[self.name],
            callback=self.parse_serp,
            method="GET",
            formdata=formdata,
            errback=self.errback_httpbin,
        )

    def parse_serp(self, response, all_links: set = None):
        combo = Combo(response)
        current_page = combo.serp.get_current_page()
        next_page = combo.serp.get_next_page()
        links = combo.serp.links_to_trade()
        all_links = (all_links or set()).union(links)
        if next_page and current_page < next_page:
            formdata["pagenum"] = str(next_page)
            yield FormRequest(
                url="".join(serp_link[self.name]),
                callback=self.parse_serp,
                formdata=formdata,
                method="GET",
                errback=self.errback_httpbin,
                cb_kwargs={"all_links": all_links},
            )
        else:
            for link in all_links:
                link = URL.url_join(trade_link[self.name], link[0])
                if link not in self.previous_trades:
                    yield Request(url=link, callback=self.parse_trade)

    def parse_trade(self, response):
        combo = Combo(response)
        transfer = EtpItem()
        transfer["data_origin"] = data_origin[self.name]
        transfer["trading_id"] = combo.trading_id
        transfer["trading_link"] = combo.trading_link
        transfer["trading_number"] = combo.trading_number
        transfer["trading_type"] = combo.trading_type
        transfer["trading_form"] = combo.trading_form
        transfer["trading_org"] = combo.trading_org
        transfer["trading_org_inn"] = combo.trading_org_inn
        transfer["trading_org_contacts"] = combo.trading_org_contacts
        transfer["msg_number"] = combo.msg_number
        transfer["case_number"] = combo.case_number
        transfer["debtor_inn"] = combo.debtor_inn
        transfer["address"] = combo.address
        transfer["arbit_manager"] = combo.arbit_manager
        transfer["arbit_manager_inn"] = combo.arbit_manager_inn
        transfer["arbit_manager_org"] = combo.arbit_manager_org
        if transfer["trading_type"] in ["auction", "competition"]:
            transfer["start_date_requests"] = combo.start_date_requests_auc
            transfer["end_date_requests"] = combo.end_date_requests_auc
            transfer["start_date_trading"] = combo.start_date_trading_auc
            transfer["end_date_trading"] = None
        general_files = combo.gen.download_general()
        transfer["property_information"] = combo.property_information
        lots_table = combo.count_lots()
        if "auction" in transfer["trading_type"]:
            return self.parse_auction(
                response=response,
                transfer_=transfer,
                lots_table=lots_table,
                files=general_files,
            )
        if "offer" in transfer["trading_type"]:
            return self.parse_offer(
                response=response,
                transfer_=transfer,
                lots_table=lots_table,
                files=general_files,
            )
        if "competition" in transfer["trading_type"]:
            return self.parse_auction(
                response=response,
                transfer_=transfer,
                lots_table=lots_table,
                files=general_files,
            )

    def parse_auction(self, response, transfer_, lots_table, files):
        """parse all auction lots"""
        combo = Combo(response)
        transfer = transfer_
        for i in range(len(lots_table)):
            loader = EtpItemLoader(EtpItem(), response=response)
            loader.add_value("data_origin", transfer["data_origin"])
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
            loader.add_value("arbit_manager_inn", transfer["arbit_manager_inn"])
            loader.add_value("arbit_manager_org", transfer["arbit_manager_org"])
            loader.add_value("status", combo.get_status(lots_table[i]))
            loader.add_value("lot_number", combo.get_lot_number(lots_table[i]))
            loader.add_value("property_information", transfer["property_information"])
            check_data = (
                "".join(transfer["trading_link"]),
                "".join(loader.get_collected_values("lot_number")),
            )
            if check_data[0] not in self.previous_trades:
                loader.add_value("short_name", combo.get_short_name(lots_table[i]))
                loader.add_value("lot_info", combo.get_lot_info(lots_table[i]))
                loader.add_value("start_date_requests", transfer["start_date_requests"])
                loader.add_value("end_date_requests", transfer["end_date_requests"])
                loader.add_value("start_date_trading", transfer["start_date_trading"])
                loader.add_value("end_date_trading", None)
                loader.add_value(
                    "start_price", combo.get_start_price_auc(lots_table[i])
                )
                loader.add_value("step_price", combo.get_step_price(lots_table[i]))
                loader.add_value("categories", None)
                lot_files = combo.lot.download_lot_files(table=lots_table[i])
                loader.add_value("files", {"general": files, "lot": lot_files})
                yield loader.load_item()

    def parse_offer(self, response, transfer_, lots_table, files):
        """parse all offer lots"""
        combo = Combo(response)
        transfer = transfer_
        for i in range(len(lots_table)):
            loader = EtpItemLoader(EtpItem(), response=response)
            loader.add_value("data_origin", transfer["data_origin"])
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
            loader.add_value("arbit_manager_inn", transfer["arbit_manager_inn"])
            loader.add_value("arbit_manager_org", transfer["arbit_manager_org"])
            loader.add_value("status", combo.get_status(lots_table[i]))
            loader.add_value("lot_number", combo.get_lot_number(lots_table[i]))
            loader.add_value("property_information", transfer["property_information"])
            check_data = (
                "".join(transfer["trading_link"]),
                "".join(loader.get_collected_values("lot_number")),
            )
            if check_data[0] not in self.previous_trades:
                loader.add_value("short_name", combo.get_short_name(lots_table[i]))
                loader.add_value("lot_info", combo.get_lot_info(lots_table[i]))
                loader.add_value(
                    "start_date_requests",
                    combo.get_start_date_requests_offer(lots_table[i]),
                )
                loader.add_value(
                    "end_date_requests",
                    combo.get_end_date_requests_offer(lots_table[i]),
                )
                loader.add_value(
                    "start_date_trading",
                    combo.get_start_date_trading_offer(lots_table[i]),
                )
                loader.add_value(
                    "end_date_trading", combo.get_end_date_trading_offer(lots_table[i])
                )
                loader.add_value(
                    "start_price", combo.get_start_price_offer(lots_table[i])
                )
                loader.add_value("step_price", None)
                loader.add_value("periods", combo.get_periods(lots_table[i]))
                lot_files = combo.lot.download_lot_files(table=lots_table[i])
                loader.add_value("files", {"general": files, "lot": lot_files})
                yield loader.load_item()
