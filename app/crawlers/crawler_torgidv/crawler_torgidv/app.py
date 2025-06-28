import re

from bs4 import BeautifulSoup

from app.utils import URL, dedent_func, Contacts, format_time, logger
from app.db.models import DownloadData, AuctionPropertyType
from .config import urls
from .locators.locator_trade import LocatorTrade


class Combo:
    def __init__(self, response):
        self.response = response

    def get_trading_link(self, property_type: AuctionPropertyType):
        return URL.url_join(
            urls[property_type],
            self.response.xpath(LocatorTrade.trading_link_loc).extract_first(),
        )

    def get_lots(self):
        return self.response.xpath(LocatorTrade.lots_loc).getall()

    def download(self):
        files = list()
        for file in self.response.xpath(LocatorTrade.files_loc).getall():
            link_ = BeautifulSoup(str(file), features="lxml").find("a")
            link = link_.get("href")
            name = link_.get_text()
            files.append(
                DownloadData(url=link, referer=self.response.url, file_name=name)
            )
        return files

    @property
    def id_(self):
        _id = re.findall(r"\d+", str(self.response.url))
        return "".join(_id)

    @property
    def trading_type(self):
        type_ = self.response.xpath(LocatorTrade.trading_type_loc).get()
        d = {"Аукцион": "auction", "Конкурс": "competition", "Предложение": "offer"}
        return d[type_]

    @property
    def trading_form(self):
        text = self.response.xpath(LocatorTrade.trading_form_loc).get()
        if "Открытая" in text:
            return "open"
        elif "Закрытая" in text:
            return "closed"
        else:
            return None

    @property
    def trading_org(self):
        try:
            td_org = dedent_func(
                self.response.xpath(LocatorTrade.trading_org_sro_loc).get()
            ).strip()
            if not td_org:
                td_org = dedent_func(
                    self.response.xpath(LocatorTrade.trading_org_fio_loc).get()
                ).strip()
            return "".join(re.sub(r"\s+", " ", td_org))
        except Exception:
            logger.warning(
                f"{self.response.url} | INVALID DATA ORGANIZER", exc_info=True
            )
        return None

    @property
    def trading_org_inn(self):
        try:
            td_org_inn = (
                self.response.xpath(LocatorTrade.trading_org_inn_loc)
                .get()
                .split("/")[0]
                .strip()
            )
            if td_org_inn:
                return Contacts.check_inn(dedent_func(td_org_inn))
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
                dedent_func(self.response.xpath(LocatorTrade.phone_org_loc).get())
                .replace(";", "")
                .strip()
            )
            return Contacts.check_phone(phone)
        except Exception:
            return None

    def get_email(self):
        """get email of organizer"""
        try:
            email = (
                dedent_func(self.response.xpath(LocatorTrade.email_org_loc).get())
                .replace(";", "")
                .strip()
            )
            return Contacts.check_email(email)
        except Exception:
            return None

    @property
    def msg_number(self):
        msg = self.response.xpath(LocatorTrade.msg_number_loc).get()
        if msg:
            return " ".join(re.findall(r"\d{6,8}", dedent_func(msg)))
        return None

    @property
    def case_number(self):
        return Contacts.check_case_number(
            dedent_func(self.response.xpath(LocatorTrade.case_number_loc).get())
        )

    @property
    def start_date_requests(self):
        date = self.response.xpath(LocatorTrade.start_date_requests_loc).get()
        if date:
            return format_time(date)
        return None

    @property
    def end_date_requests(self):
        date = self.response.xpath(LocatorTrade.end_date_requests_loc).get()
        if date:
            return format_time(date)
        return None

    @property
    def start_date_trading(self):
        date = self.response.xpath(LocatorTrade.start_date_trading_loc).get()
        if date:
            return format_time(date)
        return None

    @property
    def end_date_trading(self):
        date = self.response.xpath(LocatorTrade.end_date_trading_loc).get()
        if date:
            return format_time(date)
        return None

    @property
    def debtor_inn(self):
        try:
            inn = self.response.xpath(LocatorTrade.debitor_inn_loc).get()
            if not inn:
                return None
            trade_inn = dedent_func(inn)
            pattern = re.compile(r"\d{10,12}")
            if pattern:
                return "".join(pattern.findall(trade_inn))
        except Exception:
            pass
        return None

    @property
    def address(self):
        try:
            address = dedent_func(self.response.xpath(LocatorTrade.region_loc).get())
            if not address:
                address = dedent_func(self.response.xpath(LocatorTrade.sud_loc).get())
            return address
        except Exception:
            pass
        return None

    @property
    def arbit_manager(self):
        try:
            arbit_name = self.response.xpath(LocatorTrade.arbit_first_name_loc).get()
            arbit_surname = self.response.xpath(LocatorTrade.arbit_last_name_loc).get()
            arbit_middle = self.response.xpath(LocatorTrade.arbit_middle_name_loc).get()
            if not arbit_name or not arbit_surname or not arbit_middle:
                return None
            arbit_manager = (
                f"{arbit_surname.strip()} {arbit_name.strip()} {arbit_middle.strip()}"
            )
            arbit_manager = dedent_func(arbit_manager).strip()
            return "".join(re.sub(r"\s+", " ", arbit_manager))
        except Exception:
            logger.warning(f"{self.response.url} | INVALID DATA ARBITR NAME")
        return None

    @property
    def arbit_manager_inn(self):
        try:
            arbitr_inn = dedent_func(
                self.response.xpath(LocatorTrade.arbit_manager_inn_loc).get()
            )
            pattern = re.compile(r"\d{10,12}")
            if pattern:
                return "".join(pattern.findall(arbitr_inn))
        except Exception:
            pass
        return None

    @property
    def arbit_manager_org(self):
        try:
            td_company = dedent_func(
                self.response.xpath(LocatorTrade.arbit_manager_org_loc).get()
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
        except Exception:
            logger.warning(f"{self.response.url} | INVALID DATA ARBITR COMPANY")
        return None

    @property
    def status(self):
        status = self.response.xpath(LocatorTrade.status_loc).get().strip()
        if status == "Открыт прием заявок":
            return "active"
        elif status in ["Торги не состоялись", "Завершенные", "Торги отменены"]:
            return "ended"
        return None

    @property
    def lot_number(self):
        return self.response.xpath(LocatorTrade.lot_number).get()

    @property
    def short_name(self):
        try:
            short_name = dedent_func(
                self.response.xpath(LocatorTrade.short_name_loc).get()
            )
            if short_name != "None":
                return short_name
        except Exception:
            logger.warning(f"{self.response.url} | LOT INVALID DATA - SHORT NAME")
        return None

    @property
    def lot_info(self):
        try:
            return dedent_func(self.response.xpath(LocatorTrade.lot_info_loc).get())
        except Exception:
            logger.warning(f"{self.response.url} | LOT INVALID DATA - LOT INFO")
        return None

    @property
    def property_information(self):
        try:
            property_info = dedent_func(
                self.response.xpath(LocatorTrade.property_information_loc).get()
            )
            if property_info != "None":
                return property_info
        except Exception:
            logger.warning(f"{self.response.url} | INVALID DATA - PROPERTY INFO")
        return None

    @property
    def start_price(self):
        try:
            p = self.response.xpath(LocatorTrade.start_price_loc).get()
            if p:
                p = re.sub(
                    r"\s", "", dedent_func(p.strip()).replace(",", ".").rstrip(".")
                )
                p = "".join([x for x in p if x.isdigit() or x == "."])
                if len(p) > 0:
                    return round(float(p), 2)
        except Exception as e:
            logger.error(f"{self.response.url} | INVALID DATA START PRICE\n{e}")
        return None

    @property
    def step_price(self):
        _div_step = self.response.xpath(LocatorTrade.step_price_loc).get()
        if _div_step:
            step = re.sub(
                r"\s", "", dedent_func(_div_step.strip()).replace(",", ".").rstrip(".")
            )
            step = "".join([x for x in step if x.isdigit() or x == "."])
            try:
                step = float(step)
                return round(self.start_price * step / 100, 2)
            except (ValueError, TypeError):
                pass
        return None

    @property
    def periods(self):
        return None

    @property
    def categories(self):
        categories = self.response.xpath(LocatorTrade.categories_loc).get()
        if categories:
            return categories.strip()
        return None
