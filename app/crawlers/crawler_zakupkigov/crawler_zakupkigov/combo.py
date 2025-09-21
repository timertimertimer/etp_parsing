import re

from bs4 import BeautifulSoup

from app.db.models import DownloadData
from app.utils import logger, Contacts, dedent_func, DateTimeHelper, make_float, URL


class Combo:
    def __init__(self, response):
        self.response = response
        self.soup = BeautifulSoup(response.text, "lxml")

    @property
    def trading_id(self):
        trading_id = self.soup.find(
            "span", class_="cardMainInfo__purchaseLink distancedText"
        ).get_text(strip=True)
        return "".join([char for char in trading_id if char.isdigit()])

    @property
    def trading_number(self):
        return self.trading_id

    @property
    def trading_type(self):
        if not (
            type_ := self.soup.find(
                "span", text=re.compile("Способ определения поставщика")
            )
        ):
            logger.warning(f"{self.response.url} | Could not parse trading_type")
            return None
        type_ = type_.find_next("span").get_text(strip=True)
        d = {"rfp": ["Запрос котировок в электронной форме"]}
        for k, v in d.items():
            if "аукцион" in type_.lower():
                return "auction"
            if "конкурс" in type_.lower():
                return "competition"
            if type_ in v:
                return k
        logger.warning(f"{self.response.url} | Could not parse trading_type='{type_}'")
        return "other"

    @property
    def trading_form(self):
        return "open"

    def get_trading_org_data(self):
        if org := (
            self.soup.find("span", text="Наименование организации")
            or self.soup.find("span", text="Размещение осуществляет")
        ):
            return org
        logger.warning(f"{self.response.url} | Could not find trading org data")
        return None

    def get_trading_org_block(self):
        if not (trading_org_data := self.get_trading_org_data()):
            return None
        return trading_org_data.find_parent("div", class_="row blockInfo")

    def get_trading_org_contacts_block(self):
        if block := self.soup.find(
            "h2", class_="blockInfo__title", text="Контактная информация"
        ):
            return block.parent
        return None

    @property
    def trading_org(self):
        if org := self.get_trading_org_data():
            return org.find_next("span").get_text(strip=True).lstrip("Заказчик")
        logger.warning(f"{self.response.url} | Could not find trading org data")
        return None

    @property
    def trading_org_inn(self):
        if inn := self.soup.find(
            "div", class_="registry-entry__body-title", text="ИНН"
        ):
            return Contacts.check_inn(
                inn.find_next("div", class_="registry-entry__body-value").get_text(
                    strip=True
                )
            )
        logger.warning(f"{self.response.url} | Could not find trading org inn={inn}")
        return None

    @property
    def trading_org_contacts(self):
        org_block = self.get_trading_org_block()
        contacts_block = self.get_trading_org_contacts_block()

        email_kwargs = dict(
            name="span", class_="section__title", text="Адрес электронной почты"
        )
        if email := (
            contacts_block.find(**email_kwargs)
            if contacts_block
            else org_block.find(**email_kwargs)
        ):
            email = email.find_next("span", class_="section__info").get_text(strip=True)

        phone_kwargs = dict(
            name="span", class_="section__title", text=re.compile("телефон")
        )
        if phone := (
            contacts_block.find(**phone_kwargs)
            if contacts_block
            else org_block.find(**phone_kwargs)
        ):
            phone = phone.find_next("span", class_="section__info").get_text(strip=True)
        return {
            "email": Contacts.check_email(email),
            "phone": Contacts.check_phone(phone),
        }

    @property
    def address(self):
        if trading_org_block := self.get_trading_org_block():
            if address := trading_org_block.find(
                "span", class_="section__title", text="Адрес"
            ):
                return address.find_next("span", class_="section__info").get_text(
                    strip=True
                )
            if trading_org_contacts_block := self.get_trading_org_contacts_block():
                if address := trading_org_contacts_block.find(
                    "span", class_="section__title", text="Место нахождения"
                ):
                    return address.find_next("span", class_="section__info").get_text(
                        strip=True
                    )
        return None

    def get_main_card(self):
        return self.soup.find("div", class_="cardMainInfo row")

    @property
    def status(self):
        d = dict(
            active=(
                "идет прием заявок",
                "идет приём заявок",
                "торги в стадии приема заявок",
                "подача заявок",
            ),
            pending=("торги объявлены", "объявленные торги", "работа комиссии"),
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
                "определение поставщика завершено",
            ),
        )

        if not (
            status := self.get_main_card().find("span", class_="cardMainInfo__state")
        ):
            logger.warning(f"{self.response.url} | Could not get status")
            return None
        status = status.get_text(strip=True)
        for k, v in d.items():
            if status.lower() in v:
                return k
        return None

    @property
    def categories(self):
        return None

    @property
    def lot_id(self):
        return None

    @property
    def lot_number(self):
        return "1"

    @property
    def lot_link(self):
        return None

    @property
    def short_name(self):
        return None

    @property
    def property_information(self):
        if info := self.get_main_card().find(
            "span", class_="cardMainInfo__title", text="Предмет электронного аукциона"
        ):
            return dedent_func(info.find_next("span").get_text(strip=True))
        return None

    @property
    def lot_info(self):
        if info := self.get_main_card().find(
            "span", class_="cardMainInfo__title", text="Объект закупки"
        ):
            return dedent_func(info.find_next("span").get_text(strip=True))
        return None

    def otbor_data(self):
        otbor = self.soup.find(
            "h2",
            class_="blockInfo__title",
            text="Информация о проведении предварительного отбора",
        ) or self.soup.find(
            "h2", class_="blockInfo__title", text="Информация о процедуре закупки"
        )
        if not otbor:
            return None
        return otbor.find_parent("div", class_="row blockInfo")

    def parse_date(self, date_block):
        date_block = date_block.find_next("span", class_="section__info")
        date = date_block.find(text=True, recursive=False).get_text(strip=True)
        tz = (
            date_block.find("span", class_="timeZoneName")
            .get_text(strip=True)
            .strip("()")
        )
        tz_offset = int(tz.split("МСК")[1]) if tz.split("МСК")[1] else 0
        return DateTimeHelper.smart_parse(date).astimezone(
            DateTimeHelper.get_timezone_with_offset_from_moscow(tz_offset)
        )

    @property
    def start_date_requests(self):
        def get_publication_date():
            return DateTimeHelper.smart_parse(
                self.get_main_card()
                .find("span", class_="cardMainInfo__title", text="Размещено")
                .find_next("span")
                .get_text(strip=True)
            ).astimezone(DateTimeHelper.moscow_tz)

        if not (otbor_data := self.otbor_data()):
            return get_publication_date()

        if date := otbor_data.find(
            "span",
            class_="section__title",
            text=re.compile("Дата и время начала срока подачи заявок"),
        ):
            return self.parse_date(date)
        return get_publication_date()

    @property
    def end_date_requests(self):
        if not (otbor_data := self.otbor_data()):
            return None

        if date := (
            otbor_data.find(
                "span",
                class_="section__title",
                text=re.compile("Дата окончания срока рассмотрения заявок"),
            )
            or otbor_data.find(
                "span",
                class_="section__title",
                text=re.compile("Дата и время окончания срока подачи заявок"),
            )
        ):
            return self.parse_date(date)
        return None

    @property
    def start_date_trading(self):
        return None
        # if not (otbor_data := self.otbor_data()):
        #     return None
        #
        # if date := otbor_data.find(
        #         'span',
        #         class_='section__title',
        #         text='Дата проведения электронного аукциона'
        # ):
        #     return self.parse_date(date)
        # return None

    @property
    def end_date_trading(self):
        return None

    @property
    def start_price(self):
        if not (main_card := self.get_main_card()):
            return None

        if price := main_card.find("div", class_="price"):
            return make_float(
                price.find("span", class_="cardMainInfo__content cost").get_text(
                    strip=True
                )
            )
        return None

    @property
    def step_price(self):
        return None

    @property
    def periods(self):
        return None

    def download_general(self):
        files = []
        for doc in self.soup.find_all("div", class_="attachment row"):
            a = doc.find("span", class_='section__value').find("a")
            link = a["href"]
            name = a['title']
            files.append(DownloadData(url=link, file_name=name))
        return files

    def download_lot(self):
        return None
