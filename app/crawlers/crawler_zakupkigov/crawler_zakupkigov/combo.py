import re

from bs4 import BeautifulSoup

from app.utils import logger, Contacts


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
        if not (org := (
                self.soup.find("span", text="Размещение осуществляет") or
                self.soup.find("span", text="Наименование организации")
        )):
            logger.warning(f"{self.response.url} | Could not find trading_org")
            return None
        return org

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
            logger.warning(f"{self.response.url} | Could not find trading_org_inn")
            return None
        return Contacts.check_inn(inn.find_next('div', class_='registry-entry__body-value').get_text(strip=True))

    @property
    def trading_org_contacts(self):
        if not (trading_org_block := self.get_trading_org_block()):
            logger.warning(f"{self.response.url} | Could not find trading_org_contacts")
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
        if not (trading_org_block := self.get_trading_org_block()):
            logger.warning(f"{self.response.url} | Could not find address")
            return None

        if address := trading_org_block.find('span', class_='section__title', text='Адрес'):
            return address.find_next('span', class_='section__info').get_text(strip=True)

    @property
    def status(self):
        ...
