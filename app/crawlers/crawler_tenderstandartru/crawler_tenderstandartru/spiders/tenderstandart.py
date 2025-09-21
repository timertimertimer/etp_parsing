from scrapy import Request

from app.crawlers.items import EtpItemLoader, EtpItem
from app.utils.config import write_log_to_file
from .base import TenderstandartBaseSpider
from ..trades.combo import Combo


class TenderstandartSpider(TenderstandartBaseSpider):
    name = "tenderstandart"
    custom_settings = {
        "LOG_FILE": f"{name}.log" if write_log_to_file else None,
    }

    def parse_serp(self, response, page, trading_type):
        combo = Combo(response)
        for lot_data in combo.serp.get_lots_data_from_div_table(self.name):
            status = combo.serp.get_status(lot_data[4]) if any(lot_data) else None
            if status == "active" or status == "pending":
                transfer = EtpItem()
                transfer["trading_type"] = trading_type
                transfer["data_origin"] = self.data_origin
                transfer["trading_id"] = combo.serp.get_trading_id(lot_data[0])
                transfer["trading_number"] = transfer["trading_id"]
                transfer["trading_link"] = lot_data[0]
                transfer["trading_org"] = lot_data[3]
                transfer["status"] = status
                transfer["lot_number"] = lot_data[2]
                transfer["lot_link"] = lot_data[1]
                transfer["start_price"] = lot_data[5]
                transfer["start_date_trading"] = lot_data[6]
                if lot_data[0] not in self.previous_trades:
                    yield Request(
                        url=lot_data[0],
                        callback=self.parse_trading_page,
                        cb_kwargs={"transfer": transfer, "trading_type": trading_type},
                        dont_filter=True,
                        errback=self.errback_httpbin,
                    )
        page += 1
        if next_page := combo.serp.get_next_page_link(page, self.data_origin):
            yield Request(
                url=next_page,
                callback=self.parse_serp,
                cb_kwargs={"page": page, "trading_type": trading_type},
                errback=self.errback_httpbin,
            )

    def parse_trading_page(self, response, transfer, trading_type):
        combo = Combo(response)
        transfer["trading_org_inn"] = combo.auc.trading_org_inn
        transfer["trading_org_contacts"] = combo.auc.trading_org_contacts
        transfer["case_number"] = combo.auc.case_number
        transfer["debtor_inn"] = combo.auc.debtor_inn
        transfer["address"] = combo.auc.address
        transfer["arbit_manager"] = combo.auc.arbit_manager
        transfer["arbit_manager_org"] = combo.auc.arbit_manager_org
        transfer["property_information"] = combo.auc.property_information
        general_files = combo.gen.download_files(data_origin=self.data_origin)
        if trading_type == "offer":
            yield Request(
                url="".join(transfer["lot_link"]),
                callback=self.parse_periods_offer,
                cb_kwargs={
                    "transfer": transfer,
                    "general_files": general_files,
                    "page_offer": 1,
                    "periods": list(),
                },
            )
        else:
            yield Request(
                url="".join(transfer["lot_link"]),
                callback=self.parse_auction_lot,
                cb_kwargs={"transfer": transfer, "general_files": general_files},
            )

    def parse_periods_offer(
        self, response, transfer, page_offer, general_files, periods
    ):
        combo = Combo(response)
        page_offer += 1
        next_page = combo.serp.get_next_page_link(page_offer, self.data_origin)
        period = combo.offer.periods
        periods.extend(period)
        if next_page:
            yield Request(
                url=next_page,
                callback=self.parse_periods_offer,
                cb_kwargs={
                    "transfer": transfer,
                    "general_files": general_files,
                    "page_offer": page_offer,
                    "periods": periods,
                },
                errback=self.errback_httpbin,
            )
        else:
            yield Request(
                url="".join(transfer["lot_link"]),
                callback=self.parse_offer_lot,
                dont_filter=True,
                cb_kwargs={
                    "transfer": transfer,
                    "general_files": general_files,
                    "periods": periods,
                },
            )

    def parse_auction_lot(self, response, transfer, general_files):
        combo = Combo(response)
        loader = EtpItemLoader(EtpItem(), response=response)
        loader.add_value("data_origin", transfer["data_origin"])
        loader.add_value("trading_id", transfer["trading_id"])
        loader.add_value("trading_link", transfer["trading_link"])
        loader.add_value("trading_number", transfer["trading_number"])
        loader.add_value("trading_type", transfer["trading_type"])
        loader.add_value("trading_form", combo.auc.trading_form)
        loader.add_value("trading_org", transfer["trading_org"])
        loader.add_value("trading_org_inn", transfer["trading_org_inn"])
        loader.add_value("trading_org_contacts", transfer["trading_org_contacts"])
        loader.add_value("msg_number", combo.auc.msg_number)
        loader.add_value("case_number", transfer["case_number"])
        loader.add_value("debtor_inn", transfer["debtor_inn"])
        loader.add_value("address", transfer["address"])
        loader.add_value("arbit_manager", transfer["arbit_manager"])
        loader.add_value("arbit_manager_org", transfer["arbit_manager_org"])
        loader.add_value("status", transfer["status"])
        loader.add_value("lot_id", combo.serp.get_trading_id(response.url))
        loader.add_value("lot_link", transfer["lot_link"])
        loader.add_value("lot_number", transfer["lot_number"])
        loader.add_value("short_name", combo.auc.short_name)
        loader.add_value("lot_info", combo.auc.lot_info)
        loader.add_value("property_information", transfer["property_information"])
        loader.add_value("start_date_requests", combo.auc.start_date_requests)
        loader.add_value("end_date_requests", combo.auc.end_date_requests)
        loader.add_value("start_date_trading", transfer["start_date_trading"])
        loader.add_value("start_price", transfer["start_price"])
        loader.add_value(
            "step_price",
            combo.auc.get_step_price(loader.get_collected_values("start_price")),
        )
        loader.add_value("categories", None)
        lot_files = combo.gen.download_files(data_origin=self.data_origin)
        loader.add_value("files", {"general": general_files, "lot": lot_files})
        yield loader.load_item()

    def parse_offer_lot(self, response, transfer, general_files, periods):
        combo = Combo(response)
        loader = EtpItemLoader(EtpItem(), response=response)
        loader.add_value("data_origin", transfer["data_origin"])
        loader.add_value("trading_id", transfer["trading_id"])
        loader.add_value("trading_link", transfer["trading_link"])
        loader.add_value("trading_number", transfer["trading_number"])
        loader.add_value("trading_type", transfer["trading_type"])
        loader.add_value("trading_form", combo.auc.trading_form)
        loader.add_value("trading_org", transfer["trading_org"])
        loader.add_value("trading_org_inn", transfer["trading_org_inn"])
        loader.add_value("trading_org_contacts", transfer["trading_org_contacts"])
        loader.add_value("msg_number", combo.auc.msg_number)
        loader.add_value("case_number", transfer["case_number"])
        loader.add_value("debtor_inn", transfer["debtor_inn"])
        loader.add_value("address", transfer["address"])
        loader.add_value("arbit_manager", transfer["arbit_manager"])
        loader.add_value("arbit_manager_org", transfer["arbit_manager_org"])
        loader.add_value("status", transfer["status"])
        loader.add_value("lot_id", combo.serp.get_trading_id(response.url))
        loader.add_value("lot_link", transfer["lot_link"])
        loader.add_value("lot_number", transfer["lot_number"])
        loader.add_value("short_name", combo.auc.short_name)
        loader.add_value("lot_info", combo.auc.lot_info)
        loader.add_value("property_information", transfer["property_information"])
        loader.add_value(
            "start_date_requests", combo.offer.get_start_date_request(periods)
        )
        loader.add_value("end_date_requests", combo.offer.get_end_date_request(periods))
        loader.add_value(
            "start_date_trading", combo.offer.get_start_date_request(periods)
        )
        loader.add_value("end_date_trading", combo.offer.get_end_date_request(periods))
        loader.add_value("start_price", transfer["start_price"])
        loader.add_value("periods", periods)
        loader.add_value("categories", None)
        lot_files = combo.gen.download_files(data_origin=self.data_origin)
        loader.add_value("files", {"general": general_files, "lot": lot_files})
        yield loader.load_item()
