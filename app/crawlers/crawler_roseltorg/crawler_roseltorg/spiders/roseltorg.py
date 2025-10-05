from urllib.parse import urlencode

from scrapy import Request

from app.db.models import AuctionPropertyType
from app.utils import URL, logger
from app.crawlers.items import EtpItemLoader, EtpItem
from app.crawlers.base import BaseSpider
from app.utils.config import write_log_to_file
from ..combo import Combo
from ..config import formdatas, search_link, data_origin, start_date


class RoseltorgBaseSpider(BaseSpider):
    name = "roseltorg"
    unique_links = set()

    def __init__(self):
        super().__init__(data_origin)
        self.total_trades = 0
        self.parsed_trades = 0

    def start_requests(self):
        yield Request(
            f'{search_link}?{urlencode(formdatas[self.property_type.value] | {"start_date_published": start_date}, doseq=True)}',
            self.parse_serp,
            cb_kwargs={'current_page': 1},
        )

    def parse_serp(self, response, current_page):
        combo = Combo(response)
        cards = combo.get_trading_cards()
        for trading_card in cards:
            link = combo.parse_link(
                URL.url_join(data_origin, combo.trading_link(trading_card))
            )
            if link not in self.previous_trades:
                trading_id = combo.trading_id(trading_card)
                trading_number = combo.trading_number(trading_card)
                yield Request(
                    link,
                    self.parse_trade,
                    cb_kwargs={
                        "trading_id": trading_id,
                        "trading_number": trading_number,
                    },
                )
                self.previous_trades.append(link)
                self.total_trades += 1
        if cards:
            current_page += 1
            yield Request(
                f'{search_link}?{urlencode(formdatas[self.property_type.value] | {"start_date_published": start_date, "page": current_page}, doseq=True)}',
                self.parse_serp,
                cb_kwargs={'current_page': current_page},
            )

    def parse_trade(self, response, trading_id, trading_number):
        combo = Combo(response)
        loader = EtpItemLoader(EtpItem(), response=response)
        loader.add_value("data_origin", data_origin)
        loader.add_value("property_type", self.property_type.value)
        loader.add_value("trading_id", trading_id)
        loader.add_value("trading_link", response.url)
        loader.add_value("trading_number", trading_number)
        loader.add_value("trading_type", combo.trading_type)
        loader.add_value("trading_form", combo.trading_form)
        loader.add_value("msg_number", combo.msg_number)
        loader.add_value("case_number", combo.case_number)
        loader.add_value("trading_org", combo.trading_org)
        loader.add_value("trading_org_inn", combo.trading_org_inn)
        loader.add_value("trading_org_contacts", combo.trading_org_contacts)
        loader.add_value("arbit_manager", combo.arbit_manager)
        loader.add_value("arbit_manager_inn", combo.arbit_manager_inn)
        loader.add_value("arbit_manager_org", combo.arbit_manager_org)
        loader.add_value("debtor_inn", combo.debtor_inn)
        for i, lot in enumerate(combo.get_lots()):
            loader.add_value("address", combo.address(lot))
            loader.add_value("status", combo.status)
            loader.add_value("categories", combo.categories(lot))
            loader.add_value("lot_id", combo.lot_id)
            loader.add_value("lot_link", combo.lot_link)
            loader.add_value("lot_number", i + 1)
            loader.add_value("short_name", combo.short_name)
            loader.add_value("lot_info", combo.lot_info)
            loader.add_value("property_information", combo.property_information)
            loader.add_value("start_date_requests", combo.start_date_requests(lot))
            loader.add_value("end_date_requests", combo.end_date_requests(lot))
            loader.add_value("start_date_trading", combo.start_date_trading(lot))
            loader.add_value("end_date_trading", combo.end_date_trading)
            loader.add_value("start_price", combo.start_price(lot))
            loader.add_value("step_price", combo.step_price(lot))
            loader.add_value("periods", combo.periods)
            if self.property_type not in [AuctionPropertyType.capital_repair]:
                # на момент 07/09/25 файлы качаются с https://zakupki.gov.ru/44fz/filestore/public/1.0/download/priz/file.html
                # в ответе приходит Запрашиваемая страница не существует.
                # 
                loader.add_value(
                    "files",
                    {"general": combo.download_general(), "lot": combo.download_lot(lot)},
                )
            yield loader.load_item()
        self.parsed_trades += 1
        logger.info(f"Parsed {self.parsed_trades}/{self.total_trades} trades")


class RoseltorgLegalEntitiesSpider(RoseltorgBaseSpider):
    name = 'roseltorg_legal_entities'
    property_type = AuctionPropertyType.legal_entities
    custom_settings = {
        "LOG_FILE": f"{name}.log" if write_log_to_file else None,
    }


class RoseltorgCapitalRepairSpider(RoseltorgBaseSpider):
    name = 'roseltorg_capital_repair'
    property_type = AuctionPropertyType.capital_repair
    custom_settings = {
        "LOG_FILE": f"{name}.log" if write_log_to_file else None,
    }


class RoseltorgFz223Spider(RoseltorgBaseSpider):
    name = 'roseltorg_fz223'
    property_type = AuctionPropertyType.fz223
    custom_settings = {
        "LOG_FILE": f"{name}.log" if write_log_to_file else None,
    }
