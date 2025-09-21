import re

from bs4 import BeautifulSoup

from app.utils import dedent_func, DateTimeHelper, logger, Contacts, make_float
from app.db.models import DownloadData
from ..trades.auc import Auc
from ..trades.offer import Offer
from ..locators.locator_trade import LocatorTrade


class Combo:
    addresses = dict()

    def __init__(self, response):
        self.response = response
        self.loc = LocatorTrade()
        self.auc = Auc(response)
        self.offer = Offer(response)
        self.soup = BeautifulSoup(response.text, "lxml")

    def get_lots(self):
        lots = self.response.xpath(self.loc.lots_loc).getall()
        lots_data = []
        for lot in lots:
            soup = BeautifulSoup(lot, "lxml")
            lot_link = soup.find("a").get("href")
            status_and_number = soup.find_all("div", class_="light grey-text p5")[:2]
            lot_number = status_and_number[0].find("span").get_text().strip()
            status = status_and_number[1].find("span").get_text().strip().lower()
            status = self.get_status(status)
            lots_data.append((lot_link, lot_number, status))
        return lots_data

    @classmethod
    def get_status(cls, status):
        active = ("идёт приём заявок", "идет прием заявок")
        pending = ("объявлены", "объявлен", "на утверждении")
        ended = (
            "приём заявок завершен",
            "в стадии проведения",
            "подводятся итоги",
            "торги завершены",
            "торги отменены",
            "прием заявок завершен",
            "идёт приём заявок (приостановлены)",
            "торги приостановлены",
            "торги по лоту отменены",
        )
        if status in active:
            return "active"
        elif status in pending:
            return "pending"
        elif status in ended:
            return "ended"
        return None

    def download(self):
        files = list()
        for file in self.response.xpath(self.loc.files_loc).getall():
            a = BeautifulSoup(str(file), features="lxml").find("a", target="_blank")
            link = a.get("href")
            name = a.get_text()
            download_data = DownloadData(
                url=link, file_name=name, referer=self.response.url
            )
            files.append(download_data)
        return files

    @property
    def id_(self):
        _id = re.findall(r"\d+$", str(self.response.url))
        return "".join(_id)

    @property
    def trading_type_and_form(self):
        type_and_form = (
            self.response.xpath(self.loc.trading_type_and_form_loc).get().strip()
        )
        offer = ["ОТПП", "ЗТПП"]
        auction = ["ОАОФ", "ОАЗФ", "ЗАОФ", "ЗАОЗ"]
        competition = ["ОКОФ", "ОКЗФ", "ЗКОФ", "ЗКОЗ", "ЗКЗФ"]
        open_form = ["ОТПП", "ОАОФ", "ОАЗФ", "ОКОФ", "ОКЗФ"]
        close_form = ["ЗТПП", "ЗАОФ", "ЗАОЗ", "ЗКОФ", "ЗКОЗ", "ЗКЗФ"]
        trading_type = re.findall(r"\d+–[А-ЯA-Z]+", type_and_form)
        if len(trading_type) == 1:
            trading_type = re.findall(
                r"[А-ЯA-Z]+", trading_type[0].replace("-", "").strip()
            )
            trading_type = trading_type[0].strip().removesuffix("АИ")
            if trading_type in offer and trading_type in open_form:
                return "offer", "open"
            if trading_type in offer and trading_type in close_form:
                return "offer", "closed"
            if trading_type in auction and trading_type in open_form:
                return "auction", "open"
            if trading_type in auction and trading_type in close_form:
                return "auction", "closed"
            if trading_type in competition and trading_type in open_form:
                return "competition", "open"
            if trading_type in competition and trading_type in close_form:
                return "competition", "closed"
        return None

    @property
    def trading_org(self):
        org = (
            self.response.xpath(self.loc.trading_org_loc).get()
            or self.response.xpath(self.loc.trading_org_loc_2).get()
        )
        if not org:
            return None
        td_org = dedent_func(org).strip()
        return "".join(re.sub(r"\s+", " ", td_org))

    @property
    def trading_org_inn(self):
        try:
            td_org_inn = self.response.xpath(self.loc.trading_org_inn_loc).get()
            if td_org_inn:
                return Contacts.check_inn(dedent_func(td_org_inn.strip()))
        except Exception:
            logger.warning(
                f"{self.response.url} | INVALID DATA ORGANIZER INN", exc_info=True
            )
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

    def get_phone_number(self):
        try:
            phone = (
                dedent_func(self.response.xpath(self.loc.phone_org_loc).get())
                .replace(";", "")
                .strip()
            )
            return Contacts.check_phone(phone)
        except Exception:
            return None

    def get_email(self):
        try:
            email = (
                dedent_func(self.response.xpath(self.loc.email_org_loc).get())
                .replace(";", "")
                .strip()
            )
            return Contacts.check_email(email)
        except Exception:
            return None

    @property
    def msg_number(self):
        msg = self.response.xpath(self.loc.msg_number_loc).get()
        if msg:
            return " ".join(re.findall(r"\d{6,8}", dedent_func(msg)))
        return None

    @property
    def case_number(self):
        case_number = self.response.xpath(self.loc.case_number_loc).get()
        if not case_number:
            return None
        return Contacts.check_case_number(case_number.strip())

    @property
    def debtor_inn(self):
        inn = (
            self.response.xpath(self.loc.debitor_inn_loc).get()
            or self.response.xpath(self.loc.debitor_inn_loc_2).get()
        )
        if not inn:
            return None
        return Contacts.check_inn(inn.strip())

    @property
    def address(self):
        address = self.response.xpath(self.loc.region_loc).get()
        if not address:
            return None
        return dedent_func(address)

    @property
    def arbit_manager(self):
        arbit_manager = self.response.xpath(self.loc.arbit_manager_loc).get()
        if not arbit_manager:
            return None
        arbit_manager = dedent_func(arbit_manager)
        return "".join(re.sub(r"\s+", " ", arbit_manager))

    @property
    def arbit_manager_inn(self):
        inn = self.response.xpath(self.loc.arbit_manager_inn_loc).get()
        if not inn:
            return None
        inn = dedent_func(inn)
        return Contacts.check_inn(inn.strip())

    @property
    def arbit_manager_org(self):
        org = self.response.xpath(self.loc.arbit_manager_org_loc).get()
        if not org:
            return None
        if "(" in org:
            org = "".join(
                [
                    x if len(org) > 0 else None
                    for x in re.split(r"\(", org, maxsplit=1)[0]
                ]
            )
        return "".join(dedent_func(org))

    @property
    def short_name(self):
        short_name = (
            self.response.xpath(self.loc.short_name_loc).get()
            or self.response.xpath(self.loc.short_name_loc_2).get()
        )
        if not short_name:
            return None
        return dedent_func(short_name)

    @property
    def lot_info(self):
        lot_info = (
            self.response.xpath(self.loc.lot_info_loc).get()
            or self.response.xpath(self.loc.lot_info_loc_2).get()
        )
        if not lot_info:
            return None
        return dedent_func(lot_info)

    @property
    def property_information(self):
        property_information = self.response.xpath(
            self.loc.property_information_loc
        ).get()
        if not property_information:
            return None
        return dedent_func(property_information)

    @property
    def start_date_requests(self):
        date = self.response.xpath(self.loc.start_date_requests_loc).get()
        if not date:
            return None
        return DateTimeHelper.smart_parse(date).astimezone(DateTimeHelper.moscow_tz)

    @property
    def end_date_requests(self):
        date = self.response.xpath(self.loc.end_date_requests_loc).get()
        if not date:
            return None
        return DateTimeHelper.smart_parse(date).astimezone(DateTimeHelper.moscow_tz)

    @property
    def start_price(self):
        prices = self.response.xpath(self.loc.start_price_auc_loc).getall()
        for p in prices:
            try:
                if p and any(ch.isdigit() for ch in p):
                    return make_float(p)
            except Exception as e:
                continue
        return None

    @property
    def step_price(self):
        try:
            p = self.response.xpath(self.loc.step_price_auc_loc).get()
            if p:
                return make_float(p)
        except ValueError as e:
            logger.warning(f"{self.response.url} | INVALID DATA STEP PRICE\n{e}")
        return None

    @property
    def categories(self):
        categories = self.response.xpath(self.loc.categories_loc).getall()
        if not categories:
            return None
        return categories
