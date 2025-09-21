import re
from bs4 import BeautifulSoup

from app.utils import dedent_func, Contacts, DateTimeHelper, logger
from app.db.models import DownloadData
from .locators.trade_locator import TradeLocator


class Combo:
    def __init__(self, response):
        self.response = response

    def parse_status(self, status: str):
        active = (
            "Торги в стадии приема заявок",
            "Прием заявок",
            "Проводится приём заявок",
            "Идут торги",
        )
        pending = (
            "Объявлены торги",
            "Имущество не продано. Определяется дата новых торгов",
        )
        ended = (
            "Проведена инвентаризация",
            "Проведена оценка",
            "Имущество реализовано",
            "Имущество не реализовано",
            "Приём заявок завершен",
        )
        status = status.strip()
        try:
            if status in active:
                return "active"
            elif status in pending:
                return "pending"
            elif status in ended:
                return "ended"
            else:
                pass
        except Exception as e:
            pass

    @property
    def trading_id(self):
        _id = re.findall(r"\d+", str(self.trading_link))
        return "".join(_id)

    @property
    def trading_link(self):
        return self.response.url

    @property
    def trading_type_and_form(self):
        try:
            type_, form = (
                self.response.xpath(TradeLocator.trading_type_and_form_loc)
                .get()
                .strip()
                .lower()
                .split("/")
            )
        except Exception:
            return None, "open"
        if "закрыт" in form:
            form = "closed"
        elif "открыт" in form:
            form = "open"
        else:
            form = "open"
        if "аукцион" in type_:
            type_ = "auction"
        elif "конкурс" in type_:
            type_ = "competition"
        elif "предложение" in type_:
            type_ = "offer"
        return type_, form

    @property
    def trading_org(self):
        try:
            org = (
                BeautifulSoup(
                    self.response.xpath(TradeLocator.trading_org_loc).get(), "lxml"
                )
                .get_text()
                .strip()
            )
            return "".join(re.sub(r"\s+", " ", org))
        except Exception as e:
            logger.warning(
                f"{self.response.url} :: INVALID DATA ORGANIZER", exc_info=True
            )
        return None

    @property
    def trading_org_inn(self):
        return

    @property
    def trading_org_contacts(self):
        return

    @property
    def msg_number(self):
        return

    @property
    def case_number(self):
        case = dedent_func(
            BeautifulSoup(
                self.response.xpath(TradeLocator.case_number_loc).get(), "lxml"
            ).get_text()
        )
        if case:
            return Contacts.check_case_number(case)
        return None

    @property
    def debitor_inn(self):
        inn = (
            self.response.xpath(TradeLocator.debtor_inn_loc).get()
            or self.response.xpath(TradeLocator.debtor_inn_loc2).get()
        )
        if not inn:
            return None
        trade_inn = dedent_func(inn)
        pattern = re.compile(r"\d{10,12}")
        return Contacts.check_inn("".join(pattern.findall(trade_inn)))

    @property
    def address(self):
        address = (
            self.response.xpath(TradeLocator.address_loc).get()
            or self.response.xpath(TradeLocator.address_loc2).get()
        )
        return BeautifulSoup(address, "lxml").get_text(strip=True)

    @property
    def arbit_manager(self):
        try:
            td_org = dedent_func(
                BeautifulSoup(
                    self.response.xpath(TradeLocator.arbit_manager_loc).get(), "lxml"
                ).get_text()
            )
            if td_org != "None":
                return "".join(re.sub(r"\s+", " ", td_org))
        except Exception as e:
            logger.warning(f"{self.response.url} :: INVALID DATA ARBITR NAME")
        return None

    @property
    def arbit_manager_inn(self):
        return

    @property
    def arbit_manager_org(self):
        try:
            td_company = dedent_func(
                BeautifulSoup(
                    self.response.xpath(TradeLocator.arbit_manager_org_loc).get(),
                    "lxml",
                ).get_text()
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
            logger.warning(f"{self.response.url} :: INVALID DATA ARBITR COMPANY")
        return None

    @property
    def lot_id(self):
        return

    @property
    def lot_link(self):
        return self.trading_link

    @property
    def lot_number(self):
        match = re.search(
            r"лота №(\d+) ",
            BeautifulSoup(
                self.response.xpath(TradeLocator.lot_number_loc).get(), "lxml"
            )
            .get_text()
            .strip()
            .lower(),
        )
        if match:
            return match.group(1)
        return "1"

    @property
    def lot_info(self):
        total_info = []
        for info in self.response.xpath(TradeLocator.lot_info_loc).getall():
            soup = BeautifulSoup(info, "lxml")
            total_info.append(soup.get_text())
        return dedent_func("\n".join(total_info))

    @property
    def property_information(self):
        return

    @property
    def start_date_requests(self):
        date = self.response.xpath(TradeLocator.start_date_requests_loc).get()
        if not date:
            return None
        return DateTimeHelper.smart_parse(date).astimezone(DateTimeHelper.moscow_tz)

    @property
    def end_date_requests(self):
        date = self.response.xpath(TradeLocator.end_date_requests_loc).get()
        if not date:
            return None
        dt = DateTimeHelper.smart_parse(date)
        if not dt:
            return None
        return dt.astimezone(DateTimeHelper.moscow_tz)

    def start_and_end_dates_trading(self):
        date_interval = (
            BeautifulSoup(
                self.response.xpath(TradeLocator.start_and_end_dates_trading_loc).get(),
                "lxml",
            )
            .get_text()
            .strip()
        )
        parts = date_interval.split("-")
        if len(parts) == 2:
            start_date, end_date = parts
        else:
            start_date, end_date = parts[0], None
        start_date_dt = DateTimeHelper.smart_parse(start_date)
        if start_date_dt:
            start_date = start_date_dt.astimezone(DateTimeHelper.moscow_tz)
        end_date_dt = DateTimeHelper.smart_parse(end_date)
        if end_date_dt:
            end_date = end_date_dt.astimezone(DateTimeHelper.moscow_tz)
        return start_date, end_date

    @property
    def start_date_trading(self):
        return self.start_and_end_dates_trading()[0]

    @property
    def end_date_trading(self):
        return self.start_and_end_dates_trading()[1]

    @property
    def start_price(self):
        try:
            p = self.response.xpath(TradeLocator.start_price_loc).get().strip()
            if p:
                p = re.sub(r"\s", "", dedent_func(p).replace(",", "."))
                p = "".join([x for x in p if x.isdigit() or x == "."])
                if len(p) > 0:
                    return round(float(p), 2)
        except Exception as e:
            logger.error(f"{self.response.url} :: INVALID START PRICE\n{e}")
        return None

    @property
    def step_price(self):
        return

    @property
    def periods(self):
        return

    def download_images(self):
        carousel = self.response.xpath(TradeLocator.images_carousel_loc).getall()
        images = []
        for i, image in enumerate(carousel):
            img = BeautifulSoup(image, "lxml").find("img")
            src = img.get("src")
            images.append(
                DownloadData(
                    url=src,
                    file_name=f"image_{i}.jpg",
                    referer=self.response.url,
                    cookies=self.response.request.headers["Cookie"].decode(),
                    is_image=True,
                    order=i,
                )
            )
        return images

    def download_general(self):
        files = list()
        for link in self.response.xpath(TradeLocator.general_files_loc).getall():
            a = BeautifulSoup(str(link), features="lxml").find("a")
            name = a.get_text().strip()
            link = a.get("href")
            files.append(
                DownloadData(
                    url=link,
                    file_name=name,
                    referer=self.response.url,
                    cookies=self.response.request.headers["Cookie"].decode(),
                )
            )
        return files + self.download_images()

    def download_lot(self):
        return []
