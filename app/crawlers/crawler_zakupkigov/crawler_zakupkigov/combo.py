import re

from bs4 import BeautifulSoup

from app.utils import logger


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

    @property
    def trading_org(self):
        if not (org := self.get_trading_org_data()):
            return None
        return org.find_next('span').get_text(strip=True)

