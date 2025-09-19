import json
import xmltodict
from bs4 import BeautifulSoup as BS
from scrapy import FormRequest

from app.crawlers.items import EtpItem, EtpItemLoader
from app.db.models import AuctionPropertyType
from app.utils import logger
from .base import SberbankBaseSpider
from ..trades.combo import ComposeTrades
from ..utils.config import *
from ..utils.manage_spider import *


class SberbankBaseAPISpider(SberbankBaseSpider):
    name = "base_api"

    def parse_table(self, response, **kwargs):
        soup = BS(json.loads(response.text)["data"]["Data"]["tableXml"], "lxml-xml")
        data = xmltodict.parse(str(soup))["datarow"]
        trades = set(lot["_source"]["objectHrefTerm"] for lot in data["hits"])
        for trade in trades:
            if api_map[self.property_type.value]:
                path = trade.removeprefix("https://utp.sberbank-ast.ru")
                yield FormRequest(
                    "https://utp.sberbank-ast.ru/api/Processing/main",
                    self.parse_trade,
                    method="POST",
                    body=json.dumps(
                        {
                            "actionCode": path,
                            "windowCode": path,
                            "actionType": "template",
                        }
                    ),
                    meta={"trade": trade},
                    cb_kwargs=kwargs,
                )
            else:
                logger.error(f"{self.name} is not in api_map, check config.py")

    def parse_trade(self, response, **kwargs):
        trading_link = response.meta["trade"]
        data = json.loads(response.text)
        combo = ComposeTrades(data, trading_link)
        lst_link_to_lots = list()
        lst_dict_lot_links = (  # FIXME
                data.get("Purchase", {})
                .get("BidsPanel", {})
                .get("Bids", {})
                .get("Bid") or
                data.get("Purchase", {}).get("Bids", {}).get("Bid").get("BidInfo", {})
        )
        if isinstance(lst_dict_lot_links, list):
            lst_link_to_lots = list(map(lambda x: x["BidId"], lst_dict_lot_links))
        if isinstance(lst_dict_lot_links, dict):
            lst_link_to_lots = data["Purchase"]["BidsPanel"]["Bids"]["Bid"][
                "BidId"
            ].split()
        if not lst_link_to_lots:
            return
        for link in lst_link_to_lots:
            _link = re.sub(part_path_to_trade, part_path_to_lot, response.meta["trade"])
            _link = re.sub(r"\d+$", link, _link)
            loader = EtpItemLoader(EtpItem(), response=response)
            loader.add_value("data_origin", data_origin_url)
            loader.add_value("property_type", self.property_type)
            loader.add_value("trading_id", combo.auc.trading_id)
            loader.add_value("trading_link", trading_link)
            loader.add_value("trading_number", combo.auc.trading_number_auc)
            loader.add_value("trading_type", combo.auc.trading_type_auc)
            loader.add_value("trading_form", combo.auc.trading_form_auc)
            loader.add_value("msg_number", combo.auc.get_msg_number)
            loader.add_value("trading_org", combo.auc.trading_org_auc)
            loader.add_value("trading_org_inn", combo.auc.trading_org_inn)
            loader.add_value("trading_org_contacts", combo.auc.trading_org_contacts)
            loader.add_value("case_number", combo.auc.get_case_number)
            loader.add_value("debtor_inn", combo.auc.get_debitor_inn)
            loader.add_value("address", combo.auc.address)
            loader.add_value("arbit_manager", combo.auc.get_arbitr_manager)
            loader.add_value("arbit_manager_inn", combo.auc.get_arbitr_manager_inn)
            loader.add_value("arbit_manager_org", combo.auc.get_arbitr_manager_org)
            loader.add_value("status", "active")
            if combo.auc.trading_type_auc == "auction":
                loader.add_value(
                    "start_date_requests", combo.auc.get_start_date_requests
                )
                loader.add_value("end_date_requests", combo.auc.get_end_date_requests)
                loader.add_value("start_date_trading", combo.auc.get_start_date_trading)
                loader.add_value("end_date_trading", combo.auc.get_end_date_trading)
            url = _link
            if url not in self.previous_trades:
                files_general = combo.offer.download(
                    data["Purchase"]["PurchaseinfoPanel"]["ContractInfo"][
                        "contractdoc"
                    ]["file"],
                    self.property_type.value,
                    kwargs.get("org"),
                )
                path = url.removeprefix("https://utp.sberbank-ast.ru")
                yield FormRequest(
                    "https://utp.sberbank-ast.ru/api/Processing/main",
                    self.parse_lot,
                    method="POST",
                    body=json.dumps(
                        {
                            "actionCode": path,
                            "windowCode": path,
                            "actionType": "template",
                        }
                    ),
                    meta={"lot": url},
                    cb_kwargs={
                        "loader": loader,
                        "files": files_general,
                        "org": kwargs.get("org"),
                    },
                )

    def parse_lot(self, response, loader, files, org):
        lot_link = response.meta["lot"]
        try:
            data = json.loads(response.text)
        except Exception as e:
            raise e  # слишком частые запросы (нужны прокси)
        combo = ComposeTrades(data, lot_link)
        loader.add_value("lot_id", combo.auc.get_lot_id)
        loader.add_value("lot_link", lot_link)
        loader.add_value("lot_number", combo.auc.get_lot_number)
        loader.add_value("short_name", combo.auc.get_short_name)
        loader.add_value("lot_info", combo.auc.get_lot_info)
        loader.add_value("property_information", combo.auc.get_property_info)
        if loader.get_output_value("trading_type") == "auction":
            loader.add_value("start_price", combo.auc.get_start_price)
            loader.add_value("step_price", combo.auc.get_step_price)
        else:
            loader.add_value("start_date_requests", combo.offer.start_date_request)
            loader.add_value("end_date_requests", combo.offer.end_date_request)
            loader.add_value("start_date_trading", combo.offer.start_date_trading)
            loader.add_value("end_date_trading", combo.offer.end_date_trading)
            loader.add_value("start_price", combo.offer.start_price)
            loader.add_value("periods", combo.offer.get_periods)
        docs = data["BidView"]["Bids"]["BidDebtorInfo"].get("BidAdditionalDocEDS", [])
        if docs:
            docs = [docs["file"]] if isinstance(docs["file"], dict) else docs["file"]
        photos = data["BidView"]["Bids"]["BidDebtorInfo"].get("BidPicture", [])
        if photos:
            photos = (
                [photos["file"]] if isinstance(photos["file"], dict) else photos["file"]
            )
        files_lot = combo.offer.download(docs + photos, self.property_type.value, org)
        loader.add_value("files", {"general": files, "lot": files_lot})
        yield loader.load_item()


class SberbankBankruptcyAPISpider(SberbankBaseAPISpider):
    name = "sberbank_bankruptcy"
    property_type = AuctionPropertyType.bankruptcy


class SberbankCapitalRepairAPISpider(SberbankBaseAPISpider):
    name = "sberbank_capital_repair"
    property_type = AuctionPropertyType.capital_repair


class SberbankLegalEntitiesAPISpider(SberbankBaseAPISpider):
    name = "sberbank_legal_entities"
    property_type = AuctionPropertyType.legal_entities
