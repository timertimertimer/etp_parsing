import re

from bs4 import BeautifulSoup

from app.db.models import DownloadData
from app.utils import DateTimeHelper, dedent_func, URL, contains, Contacts
from .auction import AuctionParse, logger
from .offer import OfferParse
from .serp import SerpParse
from ..config import data_origin
from ..locators.locator_trade import LocatorTrade


class Combo:
    addresses = dict()

    def __init__(self, response_):
        self.response = response_
        self.serp = SerpParse(self.response)
        self.auc = AuctionParse(self.response)
        self.offer = OfferParse(self.response)

    @property
    def trading_type(self):
        type_ = self.response.xpath(LocatorTrade.trading_type_loc).get()
        type_ = BeautifulSoup(str(type_), features="lxml").get_text().strip()
        d = dict(
            offer=[
                "Открытые торги посредством публичного предложения",
                "Закрытые торги посредством публичного предложения",
                "Открытые торги (конкурс) посредством публичного предложения",
                "Открытые торги (конкурс) посредством публичного предложения",
            ],
            auction=[
                "Открытый аукцион с открытой формой представления предложений о цене",
                "Открытый аукцион с закрытой формой представления предложений о цене",
                "Закрытый аукцион с открытой формой представления предложений о цене",
                "Закрытый аукцион с закрытой формой представления предложений о цене",
            ],
            competition=["ОКОФ", "ОКЗФ", "ЗКОФ", "ЗКЗФ"],
        )
        for k, v in d.items():
            if type_ in v:
                return k
        return None

    @property
    def trading_form(self):
        type_ = self.response.xpath(LocatorTrade.trading_type_loc).get()
        type_ = BeautifulSoup(str(type_), features="lxml").get_text().strip()
        d = dict(
            open=[
                "Открытые торги посредством публичного предложения",
                "Открытые торги (конкурс) посредством публичного предложения",
                "Открытый аукцион с открытой формой представления предложений о цене",
                "Открытый аукцион с закрытой формой представления предложений о цене",
                "ОКОФ",
                "ОКЗФ",
            ],
            closed=[
                "Закрытые торги посредством публичного предложения",
                "Закрытые торги (конкурс) посредством публичного предложения",
                "Закрытый аукцион с открытой формой представления предложений о цене",
                "Закрытый аукцион с закрытой формой представления предложений о цене"
                "ЗКОФ",
                "ЗКЗФ",
            ],
        )
        for k, v in d.items():
            if type_ in v:
                return k
        return None

    @property
    def status(self):
        active = (
            "Торги в стадии приема заявок",
            "Прием заявок",
        )
        pending = ("Объявленые торги", "Объявленные торги")
        ended = (
            "Прием заявок завершен",
            "Проведение аукциона",
            "Торги завершены",
            "Торги отменены",
            "Торги приостановлены",
            "Торги по лоту отменены",
            "Торги по лоту приостановлены",
        )
        status = self.response.xpath(LocatorTrade.status_loc).get()
        status = BeautifulSoup(str(status), features="lxml").get_text().strip()
        try:
            if status in active:
                return "active"
            elif status in pending:
                return "pending"
            elif status in ended:
                return "ended"
            else:
                return None
        except Exception as e:
            return None

    @property
    def trading_id(self):
        _id = re.findall(r"\d+", str(self.trading_link))
        return "".join(_id)

    @property
    def trading_link(self):
        return self.response.url

    @property
    def trading_number(self):
        h1 = self.response.xpath(LocatorTrade.trading_number_loc).get()
        div = BeautifulSoup(str(h1), features="lxml").get_text()
        match = "".join(re.findall(r"\d+\-\w+", str(div)))
        if len(match) < 0:
            logger.error(f"{self.response.url} | INVALID DATA TRADING NUMBER")
        else:
            return match

    @property
    def trading_org(self):
        try:
            td_org = self.response.xpath(LocatorTrade.trading_org_loc).get()
            td_org = dedent_func(
                BeautifulSoup(str(td_org), features="lxml").get_text()
            ).strip()
            return "".join(re.sub(r"\s+", " ", td_org))
        except Exception as e:
            logger.warning(
                f"{self.response.url} | INVALID DATA ORGANIZER", exc_info=True
            )
            return None

    def get_phone_number(self):
        try:
            phone = self.response.xpath(LocatorTrade.phone_org_loc).get()
            phone = (
                dedent_func(BeautifulSoup(str(phone), features="lxml").get_text())
                .replace(";", "")
                .strip()
            )
            return Contacts.check_phone(phone)
        except Exception as e:
            return None

    def get_email(self):
        try:
            email = self.response.xpath(LocatorTrade.email_org_loc).get()
            email = (
                dedent_func(BeautifulSoup(str(email), features="lxml").get_text())
                .replace(";", "")
                .strip()
            )
            return Contacts.check_email(email)
        except Exception as e:
            return None

    @property
    def trading_org_contacts(self):
        if self.get_phone_number():
            phone = self.get_phone_number()
        else:
            phone = None
        if self.get_email():
            email = self.get_email()
        else:
            email = None
        return {"email": email, "phone": phone}

    @property
    def msg_number(self):
        msg = self.response.xpath(LocatorTrade.msg_number_loc).get()
        if msg:
            msg = BeautifulSoup(str(msg), features="lxml").get_text()
            return " ".join(re.findall(r"\d{6,8}", dedent_func(msg)))

    @property
    def case_number(self):
        case = BeautifulSoup(
            str(self.response.xpath(LocatorTrade.case_number_loc).get()), "lxml"
        ).get_text()
        return Contacts.check_case_number(dedent_func(case))

    @property
    def debitor_inn(self):
        try:
            inn = (
                self.response.xpath(LocatorTrade.debitor_inn_loc).get()
                or self.response.xpath(LocatorTrade.debitor_inn_loc_2).get()
            )
            trade_inn = dedent_func(BeautifulSoup(inn, features="lxml").get_text())
            pattern = re.compile(r"\d{10,12}")
            if pattern:
                return "".join(pattern.findall(trade_inn))
        except Exception as e:
            return None

    @property
    def address(self):
        try:
            address = self.response.xpath(LocatorTrade.address_loc).get()
            if not address:
                address = self.response.xpath(LocatorTrade.sud_loc).get()
            address = dedent_func(BeautifulSoup(address, features="lxml").get_text())
            return address
        except Exception as e:
            logger.error(f"{self.response.url} | INVALID DATA ADDRESS\n{e}")

    @property
    def arbitr_manager(self):
        try:
            td_org = self.response.xpath(LocatorTrade.arbitr_manag_loc).get()
            if td_org is None:
                td_org = self.response.xpath(LocatorTrade.finance_manag_loc).get()
            td_org = dedent_func(
                BeautifulSoup(str(td_org), features="lxml").get_text()
            ).strip()
            if td_org != "None":
                return "".join(re.sub(r"\s+", " ", td_org))
        except Exception as e:
            logger.warning(f"{self.response.url} | INVALID DATA ARBITR NAME")

    @property
    def arbitr_inn(self):
        try:
            arbitr_inn = self.response.xpath(LocatorTrade.arbitr_inn_loc).get()
            if arbitr_inn is None:
                arbitr_inn = self.response.xpath(LocatorTrade.finance_inn_loc).get()
            arbitr_inn = dedent_func(
                BeautifulSoup(str(arbitr_inn), features="lxml").get_text()
            )
            pattern = re.compile(r"\d{10,12}")
            if pattern:
                return "".join(pattern.findall(arbitr_inn))
        except Exception as e:
            return None

    @property
    def arbitr_manager_org(self):
        try:
            td_company = self.response.xpath(LocatorTrade.arbitr_org_loc).get()
            if td_company is None:
                td_company = self.response.xpath(LocatorTrade.finance_org_loc).get()
            td_company = dedent_func(
                BeautifulSoup(str(td_company), features="lxml").get_text()
            )
            if td_company != "None":
                if "(" in td_company:
                    td_company = "".join(
                        [
                            x if len(td_company) > 0 else None
                            for x in re.split(r"\(", td_company, maxsplit=1)[0]
                        ]
                    )
                return "".join(dedent_func(td_company))
        except Exception as e:
            logger.warning(f"{self.response.url} | INVALID DATA ARBITR COMPANY")

    @property
    def start_date_requests(self):
        date = self.response.xpath(LocatorTrade.start_date_requests_loc).get()
        return DateTimeHelper.smart_parse(BeautifulSoup(str(date), features="lxml").get_text()).astimezone(DateTimeHelper.moscow_tz)

    @property
    def end_date_requests(self):
        date = self.response.xpath(LocatorTrade.end_date_requests_loc).get()
        return DateTimeHelper.smart_parse(BeautifulSoup(str(date), features="lxml").get_text()).astimezone(DateTimeHelper.moscow_tz)

    def get_lots(self):
        return self.response.xpath(LocatorTrade.lots_loc).getall()

    def download_general(self):
        files = list()
        for file in self.response.xpath(LocatorTrade.general_files_loc).getall():
            a = BeautifulSoup(str(file), features="lxml").find("a")
            link = URL.url_join(data_origin, a.get("href"))
            name = a.get_text(strip=True)
            files.append(
                DownloadData(
                    url=URL.url_join(data_origin, link),
                    file_name=name,
                    referer=self.response.url,
                )
            )
        return files

    def download_lot(self, lot):
        files = list()
        if not (
            lot_files := BeautifulSoup(str(lot), "lxml").find_all(
                "a", attrs={"target": "_blank"}
            )
        ):
            return []
        for a in lot_files:
            name = a.get_text()
            link = URL.url_join(data_origin, a.get("href"))
            files.append(
                DownloadData(url=link, file_name=name, referer=self.response.url)
            )
        return files

    def lot_number(self, lot):
        title = BeautifulSoup(lot, "lxml").find("th").get_text().strip()
        match = re.findall(r"\d+$", title)
        try:
            return "".join(match)
        except Exception as e:
            logger.warning(f"{self.response.url} | LOT WITHOUT NUMBER")
            return None

    def short_name(self, lot):
        try:
            short_name = dedent_func(
                BeautifulSoup(lot, "lxml")
                .find("td", text=contains("Наименование лота"))
                .find_next_sibling("td")
                .get_text()
            )
            if short_name != "None":
                return short_name
        except Exception as e:
            logger.warning(f"{self.response.url} | LOT INVALID DATA - SHORT NAME")
            return None

    def lot_info(self, lot):
        try:
            lot_info = BeautifulSoup(str(lot), "lxml").find(
                "td", text=contains("Cведения об имуществе должника")
            )
            if not lot_info:
                return
            return dedent_func(lot_info.find_next_sibling("td").get_text())
        except Exception as e:
            logger.warning(f"{self.response.url} | LOT INVALID DATA - LOT INFO")

    def property_information(self, lot):
        try:
            property_info = dedent_func(
                BeautifulSoup(str(lot), "lxml")
                .find("td", text=contains("Порядок ознакомления"))
                .find_next_sibling("td")
                .get_text()
            )
            if property_info != "None":
                return property_info
        except Exception as e:
            logger.warning(f"{self.response.url} | INVALID DATA - PROPERTY INFO")

    def start_price(self, lot):
        try:
            p = (
                BeautifulSoup(str(lot), "lxml")
                .find("td", text=contains("Начальная цена"))
                .find_next_sibling("td")
            )
            if p:
                p = re.sub(
                    r"\s", "", dedent_func(p.get_text().strip()).replace(",", ".")
                )
                p = "".join([x for x in p if x.isdigit() or x == "."])
                if len(p) > 0:
                    return round(float(p), 2)
        except Exception as e:
            logger.error(f"{self.response.url} | INVALID DATA START PRICE\n{e}")

    def categories(self, lot):
        categories = BeautifulSoup(str(lot), "lxml").find(
            "td", text=contains("Классификатор ЕФРСБ")
        )
        if categories:
            categories = categories.find_next_sibling("td")
            return categories.get_text(strip=True)
