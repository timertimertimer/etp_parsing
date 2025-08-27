import re
from xmlrpc.client import DateTime

from bs4 import BeautifulSoup

from app.utils import logger, Contacts, dedent_func, DateTimeHelper, make_float


class Combo:
    def __init__(self, response):
        self.response = response
        self.soup = BeautifulSoup(response.text, "lxml")

    @property
    def trading_id(self):
        trading_id = self.soup.find('span', class_="cardMainInfo__purchaseLink distancedText").get_text(strip=True)
        return "".join([char for char in trading_id if char.isdigit()])

    @property
    def trading_number(self):
        return self.trading_id

    @property
    def trading_type(self):
        if not (type_ := self.soup.find('span', text=re.compile("Способ определения поставщика"))):
            logger.warning(f"{self.response.url} | Could not parse trading_type")
            return None
        type_ = type_.find_next('span').get_text(strip=True)
        d = {
            "auction": ['Электронный аукцион', 'Электронный аукцион (ПП РФ 615)']
        }
        for k, v in d.items():
            if type_ in v:
                return k
        logger.warning(f"{self.response.url} | Could not parse trading_type={type_}")
        return None

    @property
    def trading_form(self):
        return 'open'

    def get_trading_org_data(self):
        if org := (
                self.soup.find("span", text="Размещение осуществляет") or
                self.soup.find("span", text="Наименование организации")
        ):
            return org
        logger.warning(f"{self.response.url} | Could not find trading org data")
        return None

    def get_trading_org_block(self):
        if not (trading_org_data := self.get_trading_org_data()):
            return None
        return trading_org_data.find_parent('div', class_='row blockInfo')

    @property
    def trading_org(self):
        if not (org := self.get_trading_org_data()):
            return None
        return org.find_next('span').get_text(strip=True)

    @property
    def trading_org_inn(self):
        if not (inn := self.soup.find('div', class_='registry-entry__body-title', text='ИНН')):
            return None
        return Contacts.check_inn(inn.find_next('div', class_='registry-entry__body-value').get_text(strip=True))

    @property
    def trading_org_contacts(self):
        if not (trading_org_block := self.get_trading_org_block()):
            return None

        if email := trading_org_block.find('span', class_='section__title', text='Адрес электронной почты'):
            email = email.find_next('span', class_='section__info').get_text(strip=True)

        if phone := trading_org_block.find('span', class_='section__title', text='Номер телефона'):
            phone = phone.find_next('span', class_='section__info').get_text(strip=True)
        return {
            'email': Contacts.check_email(email),
            'phone': Contacts.check_phone(phone),
        }

    @property
    def address(self):
        if trading_org_block := self.get_trading_org_block():
            if address := trading_org_block.find('span', class_='section__title', text='Адрес'):
                return address.find_next('span', class_='section__info').get_text(strip=True)
        return None

    def get_main_card(self):
        return self.soup.find('div', class_='cardMainInfo row')

    @property
    def status(self):
        d = dict(
            active=(
                "идет прием заявок",
                "идет приём заявок",
                "торги в стадии приема заявок",
                "подача заявок"
            ),
            pending=("торги объявлены", "объявленные торги"),
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
            ),
        )

        status = self.get_main_card().find('span', class_='cardMainInfo__state')
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
        return '1'

    @property
    def lot_link(self):
        return None

    @property
    def short_name(self):
        return None

    @property
    def property_information(self):
        if info := self.get_main_card().find(
                'span', class_='cardMainInfo__title',
                text='Предмет электронного аукциона'
        ):
            return dedent_func(info.find_next('span').get_text(strip=True))
        return None

    @property
    def lot_info(self):
        if info := self.get_main_card().find(
                'span', class_='cardMainInfo__title',
                text='Объект закупки'
        ):
            return dedent_func(info.find_next('span').get_text(strip=True))
        return None

    def otbor_data(self):
        return (
            self.soup.find('h2', class_='blockInfo__title', text='Информация о проведении предварительного отбора')
            .find_parent('div', class_='row blockInfo')
        )

    @property
    def start_date_requests(self):
        if not (otbor_data := self.otbor_data()):
            return None

        if date := otbor_data.find(
                'span',
                class_='section__title',
                text='Дата и время начала срока подачи заявок на участие в предварительном отборе'
        ):
            return DateTimeHelper.smart_parse(
                date.find_next('span', class_='section__info')
            ).astimezone(DateTimeHelper.moscow_tz)

        logger.warning(f'{self.response.url} | Could not parse start_date_requests')
        return None

    @property
    def end_date_requests(self):
        if not (otbor_data := self.otbor_data()):
            return None

        if date := otbor_data.find(
            'span',
            class_='section__title',
            text='Дата окончания срока рассмотрения заявок на участие в электронном аукционе'
        ):
            return DateTimeHelper.smart_parse(
                date.find_next('span', class_='section__info')
            ).astimezone(DateTimeHelper.moscow_tz)

        logger.warning(f'{self.response.url} | Could not parse end_date_requests')
        return None

    @property
    def start_date_trading(self):
        if not (otbor_data := self.otbor_data()):
            return None

        if date := otbor_data.find(
            'span',
            class_='section__title',
            text='Дата проведения электронного аукциона'
        ):
            return DateTimeHelper.smart_parse(
                date.find_next('span', class_='section__info')
            ).astimezone(DateTimeHelper.moscow_tz)

        logger.warning(f'{self.response.url} | Could not parse start_date_trading')
        return None

    @property
    def end_date_trading(self):
        return None

    @property
    def start_price(self):
        if not (main_card := self.get_main_card()):
            return None

        if price := main_card.find('div', class_='price'):
            return make_float(price.find('span', class_='cardMainInfo__content cost').get_text(strip=True))

        logger.warning(f'{self.response.url} | Could not parse start_price')
        return None

