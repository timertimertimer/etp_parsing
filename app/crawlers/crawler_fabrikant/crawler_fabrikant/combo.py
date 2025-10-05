import re
import pandas as pd
from bs4 import BeautifulSoup as BS

from app.db.models import DownloadData
from .locator import Locator
from app.utils import (
    URL,
    dedent_func,
    Contacts,
    contains,
    logger,
    DateTimeHelper,
    make_float,
)
from .config import data_origin_url


class Combo:
    def __init__(self, response):
        self.response = response
        self.soup = BS(response.text, features="lxml")

    def download_general(self):
        files = list()
        if not (table := self.soup.find("div", id="proc").find("table")):
            return files
        for file in table.find_all("tr")[1:]:
            if not (link := file.find("td", class_="action")):
                continue
            link = URL.url_join(
                data_origin_url, link.find("a", text=contains("Скачать")).get("href")
            )
            file_name = file.find("td", class_="procedure-document-file").find("b")
            if not file_name:
                continue
            name = file_name.get_text(strip=True)
            files.append(
                DownloadData(url=link, file_name=name, referer=self.trading_link)
            )
        return files

    def download_lot(self, lot_number: str):
        files = list()
        if not (table := self.soup.find("div", id=f"lot{lot_number}")):
            return files
        for file in table.find("table").find_all("tr")[1:]:
            if not (link := file.find("td", class_="action")):
                continue
            link = URL.url_join(
                data_origin_url, link.find("a", text=contains("Скачать")).get("href")
            )
            name = (
                file.find("td", class_="lot-document-file")
                .find("b")
                .get_text(strip=True)
            )
            files.append(
                DownloadData(url=link, file_name=name, referer=self.trading_link)
            )
        return files

    def count_lots(self):
        return self.response.xpath(Locator.div_info_lot_offer).getall()[1:]

    def link_doc_page(self, url):
        try:
            link_to_document = BS(
                self.response.css(Locator.doc_link_loc).get(), features="lxml"
            ).a["href"]
            if data_origin_url not in link_to_document:
                return URL.url_join(data_origin_url, link_to_document)
            else:
                return link_to_document
        except Exception as e:
            logger.error(f"{url}:: INVALID DATA REFERENCE TO DOC PAGE")
        return None

    @property
    def trading_id(self):
        return self.response.url.split("/")[-1]

    @property
    def trading_link(self):
        return self.response.url

    @property
    def trading_number(self):
        number = self.response.xpath(Locator.offer_trading_number_loc2).get()
        number1 = self.response.xpath(Locator.offer_trading_number_loc).get()
        if number is None:
            number = number1
        if number:
            number = BS(str(number), features="lxml").get_text()
            number = "".join(re.findall(r"\d+", number))
        return number

    def get_trading_type_text(self):
        check_type = self.soup.find(
            "div", text=re.compile("Способ проведения процедуры")
        ) or self.soup.find("div", text=re.compile("Название процедуры на ЭТП"))
        if check_type:
            check_type = check_type.find_next("div")
            if check_type:
                return check_type.get_text().strip()
        return None

    @property
    def trading_type(self):
        string = self.get_trading_type_text()
        d = {
            "offer": [
                "Публичное предложение продавца",
                "Процедура с поэтапным снижением цены",
            ],
            "auction": [
                "Открытый аукцион с открытой формой подачи ценовых предложений",
                "Открытый аукцион с закрытой формой подачи ценовых предложений",
                "Закрытый аукцион с открытой формой подачи ценовых предложений",
                "Закрытый аукцион с закрытой формой подачи ценовых предложений",
                "Аукцион продавца",
                "Аукцион",
                "Аукцион с закрытой формой подачи предложений о цене",
                "Аукцион с открытой формой подачи предложений о цене",
                "Публичное предложение (по типу голландского аукциона)",
                "Аукцион в электронной форме, участниками которого могут быть только субъекты малого и среднего предпринимательства",
            ],
            "competition": [
                "Открытый конкурс",
                "Закрытый конкурс",
                "Конкурс продавца",
                "Конкурс в электронной форме, участниками которого могут являться только субъекты малого и среднего предпринимательства",
                "Конкурс",
            ],
            "pdo": ["ПДО продавца (по типу продажи без объявления цены)", "МПДО"],
            "rfp": [
                "Запрос предложений",
                "Запрос предложений в электронной форме, участниками которого могут являться только субъекты малого и среднего предпринимательства"
                "Запрос цен",
                "Запрос котировок",
                "Запрос оферт",
                "Мониторинг цен",
                "Запрос цен",
                "Запрос котировок в электронной форме, участниками которого могут являться только субъекты малого и среднего предпринимательства",
            ],
            "tender": ["Тендер"],
            "reduction": ["Редукцион"],
        }
        for k, v in d.items():
            match = "".join(
                filter(
                    lambda x: re.findall(re.escape(x), string, flags=re.IGNORECASE), v
                )
            )
            if match:
                return k
        logger.warning(
            f"{self.response.url} | Could not parse trading_type. String: {string}"
        )
        return None

    @property
    def sme(self):
        string = self.get_trading_type_text()
        if "субъекты малого и среднего предпринимательства" in string:
            return True
        return False

    @property
    def trading_form(self):
        form_type = self.soup.find(
            "div", text=re.compile("Форма торгов по составу участников")
        )
        if form_type:
            form_type = form_type.find_next("div")
            if form_type:
                form_type = form_type.get_text().strip()
                if "открыт" in form_type.lower():
                    return "open"
                elif "закрыт" in form_type.lower():
                    return "closed"
                else:
                    raise Exception
        return "closed"

    @property
    def trading_org(self):
        try:
            first_loc = dedent_func(
                self.response.xpath(Locator.offer_org_name_loc1).get()
            )
            second_loc = dedent_func(
                BS(
                    str(self.response.xpath(Locator.offer_org_name_loc2).get()),
                    features="lxml",
                ).get_text()
            )
            if first_loc:
                return first_loc
            elif second_loc:
                return second_loc
            else:
                return None
        except Exception as e:
            logger.warning(f"{self.response.url} :: INVALID DATA TRADING ORG - OFFER ")
        return None

    @property
    def trading_org_inn(self):
        try:
            trade_inn = BS(
                self.response.xpath(Locator.offer_org_inn_loc).get(), features="lxml"
            ).get_text()
            pattern = re.compile(r"\d{10,12}")
            if pattern:
                return "".join(pattern.findall(trade_inn))
        except Exception as e:
            pass
        return None

    @property
    def trading_org_contacts(self):
        phone = ""
        phone_loc = self.response.xpath(Locator.offer_org_phone_loc).get()
        if phone_loc:
            phone = Contacts.check_phone(
                BS(phone_loc, features="lxml").get_text().strip()
            )
        email = ""
        email_loc = self.response.xpath(Locator.offer_org_email_loc).get()
        if email_loc:
            email = Contacts.check_email(
                BS(email_loc, features="lxml").get_text().strip()
            )
        return {"email": email, "phone": phone}

    @property
    def msg_number(self):
        td_msg = BS(self.response.text, features="lxml").find(
            "div", string=re.compile("сообщения .* ЕФРСБ", re.IGNORECASE)
        )
        if td_msg:
            td_msg = dedent_func(td_msg.find_next("div").get_text().strip())
        try:
            if td_msg:
                match = re.findall(r"\d{7,9}", td_msg)
                return Contacts.check_msg_number(" ".join(match))
        except Exception as e:
            logger.error(
                f"{self.response.url} :: INVALID DATA MSG_NUMBER OFFER", exc_info=True
            )
        return None

    @property
    def case_number(self):
        case_ = self.response.xpath(Locator.offer_case_number).get()
        try:
            case_ = (
                "".join(BS(str(case_), features="lxml").get_text())
                .replace("№", "")
                .replace("\\", "/")
                .replace(" ", "")
                .strip()
            )
            if len(case_) < 42:
                return Contacts.check_case_number(case_)
        except Exception as e:
            logger.warning(f"{self.response.url} :: INVALID CASE_NUMBER  OFFER")
        return None

    @property
    def debtor_inn(self):
        inn = self.response.xpath(Locator.deb_inn_loc).get()
        if inn:
            inn = BS(inn, features="lxml").get_text()
            pattern = re.compile(r"\d{10,12}")
            if pattern:
                return "".join(pattern.findall(inn))
        return None

    @property
    def address(self):
        debtor_address = self.response.xpath(Locator.address_loc).get()
        if not debtor_address:
            debtor_address = sud_address = self.response.xpath(Locator.sud_loc).get()
        if debtor_address:
            return " ".join(
                BS(debtor_address, features="lxml").get_text(strip=True).split()
            )
        return None

    @property
    def arbit_manager(self):
        try:
            last_name = dedent_func(
                BS(
                    str(self.response.xpath(Locator.arbitr_last_name).get()),
                    features="lxml",
                ).get_text()
            )
            name = dedent_func(
                BS(
                    str(self.response.xpath(Locator.arbitr_name).get()), features="lxml"
                ).get_text()
            )
            middle_name = dedent_func(
                BS(
                    str(self.response.xpath(Locator.arbitr_mid_name).get()),
                    features="lxml",
                ).get_text()
            )
            return " ".join(
                list(filter(lambda x: x != "None", [last_name, name, middle_name]))
            )
        except Exception as e:
            pass

    @property
    def arbit_manager_inn(self):
        inn = self.response.xpath(Locator.arbitr_inn).get()
        if inn:
            arb_inn = BS(inn, features="lxml").get_text()
            pattern = re.compile(r"\d{10,12}")
            if pattern:
                return "".join(pattern.findall(dedent_func(arb_inn)))
        return None

    @property
    def arbit_manager_org(self):
        amo = self.response.xpath(Locator.arbitr_org).get()
        if amo:
            td_company = BS(amo, features="lxml").get_text()
            if "(" in td_company:
                td_company = "".join(
                    [
                        x if len(td_company) > 0 else None
                        for x in re.split(r"\(", td_company, maxsplit=1)[0]
                    ]
                )
            return "".join(dedent_func(td_company))
        return None

    def create_soup(self, lot):
        return BS(lot, features="lxml")

    def get_status(self, lot):
        try:
            status = (
                self.create_soup(lot)
                .find("span", class_="kim-state-label")
                .get_text(strip=True)
            )
        except Exception as e:
            return None
        active = ("Этап приема заявок", "Проводятся торги", "Прием заявок")
        pending = (
            "Ожидание этапа приема заявок",
            "Ожидается начало нового этапа",
            "Ожидается начало приема заявок",
        )
        if status in active:
            return "active"
        elif status in pending:
            return "pending"
        else:
            return "ended"

    def get_lot_id(self, lot):
        return self.get_lot_link(lot).split("/")[-1]

    def get_lot_link(self, lot):
        return URL.url_join(
            data_origin_url,
            self.create_soup(lot).find("a", text="Просмотр").get("href").strip(),
        )

    def get_lot_number(self, lot):
        short_name = self.get_short_name(lot)
        pattern = re.compile(
            r"Лот.?\W\s?\d{1,}\:?|Лот.?\W\d{1,}\.?", flags=re.IGNORECASE
        )
        match = pattern.findall(str(short_name))
        lot_number = "".join(re.findall(r"\d+", min(match)))
        return lot_number

    def get_short_name(self, lot):
        return dedent_func(
            self.create_soup(lot)
            .find("div", class_="panel-heading clearfix")
            .find(text=True, recursive=False)
            .get_text(strip=True)
            .removesuffix("-")
            .strip()
        )

    def get_lot_info(self, lot):
        lot_soup = self.create_soup(lot)
        lot_info = (
                lot_soup.find("div", text=re.compile("Предмет договора", re.IGNORECASE))
                or lot_soup.find(
            "div", text=re.compile("Наименование предмета торгов", re.IGNORECASE)
        )
                or lot_soup.find(
            "div", text=re.compile("Наименование предмета аренды", re.IGNORECASE)
        )
        )
        if not lot_info:
            return None
        return dedent_func(lot_info.find_next("div").get_text(strip=True))

    def get_property_information(self, lot):
        info = self.create_soup(lot).find(
            "div",
            text=re.compile("Порядок ознакомления с имуществом", re.IGNORECASE),
        )
        if not info:
            return None
        return dedent_func(info.find_next("div").get_text(strip=True))

    def get_start_date_requests(self, lot):
        publication_date = self.soup.find(
            "div", text=re.compile("Дата публикации", re.IGNORECASE)
        )
        lot_date = self.create_soup(lot).find(
            "div",
            text=re.compile("Дата и время начала приема заявок", re.IGNORECASE),
        )
        dt = DateTimeHelper.smart_parse(
            (lot_date or publication_date).find_next("div").get_text(strip=True)
        )
        if not dt:
            return None
        return dt.astimezone(DateTimeHelper.moscow_tz)

    def get_end_date_requests(self, lot):
        procedure_date = self.soup.find(
            "div",
            text=re.compile("Дата окончания приема заявок", re.IGNORECASE),
        ) or self.soup.find(
            "div", text=re.compile("Дата и время окончания приема заявок", re.IGNORECASE),

        )
        lot_soup = self.create_soup(lot)
        lot_date = lot_soup.find(
            "div",
            text=re.compile("Дата и время окончания приема заявок", re.IGNORECASE),
        ) or lot_soup.find(
            "div",
            text=re.compile("Дата окончания приема заявок", re.IGNORECASE),
        )

        if date := (lot_date or procedure_date):
            return DateTimeHelper.smart_parse(
                date.find_next("div").get_text(strip=True)
            ).astimezone(DateTimeHelper.moscow_tz)
        return None

    def get_categories(self, lot):
        lot_soup = self.create_soup(lot)
        categories = (
                lot_soup.find(
                    "div",
                    text=re.compile("Классификатор имущества для ЕФРСБ", re.IGNORECASE),
                )
                or lot_soup.find(
            "div", text=re.compile("Категория имущества", re.IGNORECASE)
        )
                or lot_soup.find("div", text=re.compile("Коды ОКПД", re.IGNORECASE))
                or lot_soup.find(
            "div", text=re.compile("Категория для рассылки по ОКПД2", re.IGNORECASE)
        )
        )
        if not categories:
            return None
        return " ".join(categories.find_next("div").get_text(strip=True).split())

    def get_start_date_trading(self, lot):
        soup = self.create_soup(lot)
        date = (
                soup.find(
                    "div",
                    text=re.compile("Дата и время начала аукциона", re.IGNORECASE),
                )
                or soup.find(
            "div",
            text=re.compile(
                "Дата и время начала подачи предложений о цене",
                re.IGNORECASE,
            ),
        )
                or soup.find(
            "div",
            text=re.compile(
                "Дата начала редукциона",
                re.IGNORECASE,
            ),
        )
        )
        if not date:
            return None
        return DateTimeHelper.smart_parse(
            date.find_next("div").get_text(strip=True)
        ).astimezone(DateTimeHelper.moscow_tz)

    def get_end_date_trading(self, lot):
        date = self.create_soup(lot).find(
            "div",
            text=re.compile("Дата и время подведения итогов", re.IGNORECASE),
        )
        if not date:
            return None

        return DateTimeHelper.smart_parse(
            date.find_next("div").get_text(strip=True)
        ).astimezone(DateTimeHelper.moscow_tz)

    def get_start_price(self, lot):
        if not (
                start_price := self.create_soup(lot).find(
                    "div", class_="panel-group panel-group-element-lot_price"
                )
        ):
            return None
        start_price = start_price.find_next("div").get_text(strip=True)
        return make_float(start_price)

    def get_step_price(self, lot):
        _div_step = self.create_soup(lot).find(
            "div", text=re.compile("Шаг аукциона", re.IGNORECASE)
        )
        if _div_step:
            _div_step = _div_step.find_next("div").get_text(strip=True)
            step = "".join(
                re.findall(r"^\d*\,?\d+", _div_step.replace("\xa0", ""))
            ).replace(",", ".")
            start_price = self.get_start_price(lot)
            try:
                step = float(step)
                return round(start_price * step / 100, 2)
            except (ValueError, TypeError) as e:
                pass
        return None

    def get_periods(self, lot):
        lot_soup = self.create_soup(lot)
        if not (
                tables := (
                        lot_soup.find("div", text=re.compile("Этап понижения", re.IGNORECASE))
                        or lot_soup.find(
                    "div", text=re.compile("Этапы приема заявок", re.IGNORECASE)
                )
                )
        ):
            return None

        tables = tables.find_next("div")
        periods = []
        check_value = 10 ** 22
        for table in tables.find_all("table"):
            _table = pd.read_html(str(table))
            df = _table[0][1]
            start = df.iloc[1]
            end = df.iloc[2]
            price_ = df.iloc[3]
            price_ = "".join(filter(lambda x: x.isdigit() or x == ",", price_)).replace(
                ",", "."
            )
            try:
                if isinstance(price_, str):
                    price = "".join(re.sub(r"\s", "", price_)).replace(",", ".")
                price = round(float(price), 2)
                if check_value < price:
                    logger.critical(
                        f"{self.response.url} :: INVALID PRICE ON PERIOD - CURRENT PRICE HIGHER THAN PREVIUOS"
                    )
                else:
                    check_value = price
            except Exception as e:
                logger.error(
                    f"{self.response.url} Period Price - {price_} typeof - {type(price_)}"
                )
                return None
            try:
                period = {
                    "start_date_requests": DateTimeHelper.smart_parse(start).astimezone(DateTimeHelper.moscow_tz),
                    "end_date_requests": DateTimeHelper.smart_parse(end).astimezone(DateTimeHelper.moscow_tz),
                    "end_date_trading": DateTimeHelper.smart_parse(end).astimezone(DateTimeHelper.moscow_tz),
                    "current_price": price,
                }
                periods.append(period)
            except Exception as e:
                continue
        return periods
