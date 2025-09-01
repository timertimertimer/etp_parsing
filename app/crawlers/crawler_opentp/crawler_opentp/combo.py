import re
import pandas as pd
from bs4 import BeautifulSoup

from .config import data_origin_url
from app.utils import URL, dedent_func, Contacts, DateTimeHelper, logger
from app.db.models import DownloadData


class Combo:
    def __init__(self, response):
        self.response = response
        self.soup = BeautifulSoup(self.response.text, "lxml")

    def get_trading_links(self):
        links = self.response.xpath(
            '//div[@id="tenders-box-on-index"]//table//td[1]/a/@href'
        ).getall()
        if links:
            return [URL.url_join(data_origin_url, link) for link in links]
        logger.warning(f"{self.response.url} :: NO TRADING LINKS")
        return []

    def get_next_page(self):
        pager_select = self.response.xpath('//span[@class="pager_select"]').get()
        try:
            next_link = BeautifulSoup(pager_select, "lxml").find("a")
            if next_link:
                return URL.url_join(data_origin_url, next_link.get("href"))
        except Exception as e:
            logger.error(
                f"{self.response.url} :: SOMETHING WENT WRONG WITH NEXT PAGE\n{e}",
                exc_info=True,
            )

    def download(self, docs):
        files = list()
        if not docs:
            return files
        for file in docs.find_all("tr")[1:]:
            link_ = file.find("a", target="_blank")
            link = link_.get("href")
            name = link_.get_text()
            files.append(
                DownloadData(
                    url=URL.url_join(data_origin_url, link),
                    file_name=name,
                    referer=self.response.url,
                )
            )
        return files

    def download_lot(self):
        return self.download(self.get_lot_table().find("table", class_="docs-table"))

    def download_general(self):
        return self.download(self.get_trade_table().find("table", class_="docs-table"))

    def get_trade_table(self):
        return self.soup.find("table", id="tender-info-table")

    def get_lot_table(self):
        return self.soup.find("table", id="lot-info-table")

    def get_lots(self):
        main_table = self.get_trade_table()
        try:
            lots = []
            lots_table = main_table.find("table", class_="lots-table")
            links = lots_table.find_all("a")
            pd_table = pd.read_html(str(lots_table))[0]
            for link, row in zip(links, list(pd_table.iterrows())[1:]):
                data = row[1]
                lot_number = data[0]
                short_name = dedent_func(data[1])
                status = self.get_status(data[2])
                address = (
                    data[3].strip() if isinstance(data[3], str) else None
                ) or self.get_sud_address()
                start_price = self.get_start_price(data[4])
                lots.append(
                    [
                        URL.url_join(data_origin_url, link.get("href")),
                        lot_number,
                        short_name,
                        status,
                        address,
                        start_price,
                    ]
                )
            return lots
        except Exception as e:
            logger.error(
                f"{self.response.url} :: SOMETHING WENT WRONG WITH LOTS\n{e}",
                exc_info=True,
            )
            return []

    def get_status(self, status):
        d = dict(
            active=("идет прием заявок", "идет приём заявок", "прием заявок"),
            pending=(
                "торги объявлены",
                "объявленные торги",
                "ожидание подведения итогов",
                "определение участников торгов",
                "извещение опубликовано",
            ),
            ended=(
                "заявки рассмотрены",
                "идёт аукцион",
                "подведение итогов",
                "приём заявок завершен",
                "рассмотрение заявок",
                "торги аннулированы",
                "торги не состоялись",
                "торги отменены",
                "торги приостановлены",
                "торги проведены",
                "торги завершены",
                "прием заявок завершен",
                "приостановленные торги",
            ),
        )
        for k, v in d.items():
            if status.lower() in v:
                return k
        return None

    def get_start_price(self, price):
        try:
            p = re.sub(r"\s", "", dedent_func(price).replace(",", "."))
            p = "".join([x for x in p if x.isdigit() or x == "."])
            if len(p) > 0:
                return round(float(p), 2)
        except Exception as e:
            logger.error(f"{self.response.url} :: INVALID DATA START PRICE\n{e}")

    @property
    def trading_id(self):
        _id = re.search(r"tender\/(\d+)\/", str(self.response.url)).group(1)
        return _id

    def get_main_info(self):
        table = self.get_trade_table()
        main_info = table.find("div", text=re.compile("Основная информация")).get_text()
        trading_number, trading_type_and_form = re.search(
            r"(\d+)-(\D+)$", main_info
        ).groups()
        if trading_type_and_form[1] == "А":
            trading_type = "auction"
        else:
            trading_type = "offer"
        return trading_number, trading_type

    @property
    def trading_form(self):
        d = {"Открытая": "open", "Закрытая": "closed"}
        form = self.get_trade_table().find(
            "b", text=re.compile("Форма представления предложений о цене")
        )
        if form:
            form = form.next_sibling.get_text()
            return d.get(form, None)
        return "closed"

    def get_org(self):
        table = self.get_trade_table()
        return table.find("div", text="Информация об организаторе").find_next("tr")

    @property
    def trading_org(self):
        try:
            org = self.get_org().find(
                "div", text=re.compile(r"Арбитражный управляющий")
            )
            if org:
                return dedent_func(
                    re.search(r"Арбитражный управляющий \/ (.+)", org.get_text()).group(
                        1
                    )
                )
            org = (
                self.get_org()
                .find("b", text=re.compile("Полное наименование"))
                .next_sibling.get_text()
            )
            return dedent_func(org)
        except Exception as e:
            logger.error(
                f"{self.response.url} :: SOMETHING WENT WRONG WITH ORGANIZER\n{e}",
                exc_info=True,
            )

    @property
    def trading_org_inn(self):
        try:
            inn = (
                self.get_org().find("b", text=re.compile("ИНН")).next_sibling.get_text()
            )
            return Contacts.check_inn(inn)
        except Exception as e:
            logger.error(
                f"{self.response.url} :: SOMETHING WENT WRONG WITH ORGANIZER INN\n{e}",
                exc_info=True,
            )

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
                self.get_org()
                .find("b", text=re.compile("Телефон"))
                .next_sibling.get_text()
            )
            phone = dedent_func(phone)
            return Contacts.check_phone(phone)
        except Exception as e:
            logger.error(
                f"{self.response.url} :: SOMETHING WENT WRONG WITH PHONE NUMBER\n{e}",
                exc_info=True,
            )

    def get_email(self):
        try:
            email = (
                self.get_org()
                .find("b", text=re.compile("Адрес электронной почты"))
                .next_sibling.get_text()
            )
            email = dedent_func(email)
            return Contacts.check_email(email)
        except Exception as e:
            logger.error(
                f"{self.response.url} :: SOMETHING WENT WRONG WITH EMAIL\n{e}",
                exc_info=True,
            )

    @property
    def msg_number(self):
        return None

    def get_debtor(self):
        table = self.get_trade_table()
        return table.find("div", text=re.compile("Информация о продавце")).find_next(
            "tr"
        )

    @property
    def case_number(self):
        try:
            case_number = (
                self.get_debtor()
                .find("b", text=re.compile("Номер дела"))
                .next_sibling.get_text()
            )
            return dedent_func(case_number)
        except Exception as e:
            logger.error(
                f"{self.response.url} :: SOMETHING WENT WRONG WITH EMAIL\n{e}",
                exc_info=True,
            )

    @property
    def debitor_inn(self):
        try:
            inn = (
                self.get_debtor()
                .find("b", text=re.compile("ИНН"))
                .next_sibling.get_text()
            )
            return Contacts.check_inn(inn)
        except Exception as e:
            logger.error(
                f"{self.response.url} :: SOMETHING WENT WRONG WITH DEBITOR INN\n{e}",
                exc_info=True,
            )

    def get_sud_address(self):
        try:
            address = (
                self.get_debtor()
                .find("b", text=re.compile("Наименование арбитражного суда"))
                .next_sibling.get_text()
            )
            return dedent_func(address)
        except Exception as e:
            logger.error(
                f"{self.response.url} :: SOMETHING WENT WRONG WITH SUD ADDRESS\n{e}",
                exc_info=True,
            )

    @property
    def arbitr_manager(self):
        return self.trading_org

    @property
    def arbitr_manager_inn(self):
        return self.trading_org_inn

    @property
    def arbitr_manager_org(self):
        try:
            org = (
                self.get_debtor()
                .find(
                    "b",
                    text=re.compile("Наименование организации арбитражных управляющих"),
                )
                .next_sibling.get_text()
            )
            return dedent_func(org)
        except Exception as e:
            logger.error(
                f"{self.response.url} :: SOMETHING WENT WRONG WITH ARBITR MANAGER ORG\n{e}",
                exc_info=True,
            )

    @property
    def start_date_requests(self):
        try:
            date = (
                self.get_trade_table()
                .find(
                    "b",
                    text=re.compile(
                        "Дата и время начала представления заявок на участие"
                    ),
                )
                .next_sibling.get_text()
            )
            return DateTimeHelper.smart_parse(date).astimezone(DateTimeHelper.moscow_tz)
        except Exception as e:
            logger.error(
                f"{self.response.url} :: SOMETHING WENT WRONG WITH START DATE REQUESTS\n{e}",
                exc_info=True,
            )

    @property
    def end_date_requests(self):
        try:
            date = (
                self.get_trade_table()
                .find(
                    "b",
                    text=re.compile(
                        "Дата и время окончания представления заявок на участие"
                    ),
                )
                .next_sibling.get_text()
            )
            return DateTimeHelper.smart_parse(date).astimezone(DateTimeHelper.moscow_tz)
        except Exception as e:
            logger.error(
                f"{self.response.url} :: SOMETHING WENT WRONG WITH END DATE REQUESTS\n{e}",
                exc_info=True,
            )

    @property
    def property_information(self):
        try:
            return dedent_func(
                self.get_trade_table()
                .find("b", text=re.compile("Порядок ознакомления с имуществом"))
                .next_sibling.get_text()
            )
        except Exception as e:
            logger.error(
                f"{self.response.url} :: SOMETHING WENT WRONG WITH PROPERTY INFORMATION\n{e}",
                exc_info=True,
            )

    @property
    def lot_id(self):
        _id = re.search(r"tender\/\d+\/lot\/(\d+)", str(self.response.url)).group(1)
        return _id

    @property
    def lot_info(self):
        try:
            return dedent_func(
                self.get_lot_table()
                .find("b", text=re.compile("Наименование лота"))
                .next_sibling.get_text()
            )
        except Exception as e:
            logger.error(
                f"{self.response.url} :: SOMETHING WENT WRONG WITH LOT INFO\n{e}",
                exc_info=True,
            )

    @property
    def step_price(self):
        try:
            p = self.get_lot_table().find("b", text=re.compile("Шаг аукциона, руб."))
            if p:
                p = p.next_sibling.get_text()
                p = re.sub(r"\s", "", dedent_func(p.strip()).replace(",", "."))
                p = "".join([x for x in p if x.isdigit() or x == "."])
                if len(p) > 0:
                    return round(float(p), 2)
        except ValueError as e:
            logger.error(f"{self.response.url} :: INVALID DATA STEP PRICE\n{e}")

    @property
    def start_date_trading(self):
        return self.start_date_requests

    @property
    def end_date_trading(self):
        try:
            date = (
                self.get_trade_table()
                .find("b", text=re.compile("Дата и время подведения итогов торгов"))
                .next_sibling.get_text()
            )
            return DateTimeHelper.smart_parse(date).astimezone(DateTimeHelper.moscow_tz)
        except Exception as e:
            logger.error(
                f"{self.response.url} :: SOMETHING WENT WRONG WITH END DATE TRADING\n{e}",
                exc_info=True,
            )
