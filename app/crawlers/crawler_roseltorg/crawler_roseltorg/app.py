import logging
import re

from bs4 import BeautifulSoup

from general_utils import (
    contains,
    CheckIfCorrectContactInfo,
    return_parse_date,
    make_float,
)
from general_utils.models import DownloadData
from .config import search_link

logger = logging.getLogger(__name__)


class Combo:
    def __init__(self, response):
        self.response = response
        self.soup = BeautifulSoup(response.text, "lxml")

    def get_trading_cards(self):
        return self.soup.find_all("div", class_="search-item")

    def parse_link(self, link):
        match = re.search(r"https:\/\/www\.roseltorg\.ru\/procedure\/[\w\d]+", link)
        if match:
            return match.group(0)
        logger.error(f"{self.response.url} :: Trading link not found")

    def get_next_page_link(self):
        if next_link := self.soup.find("button", class_="pagination__btn--next"):
            return search_link + next_link.get("data-href")

    def download_general(self):
        files = list()
        docs = self.soup.find_all("a", class_="documents__link")
        for doc in docs:
            link = doc.get("href")
            name: str = doc.get("title")
            file_format = link.split(".")[-1]
            if not name.endswith(file_format):
                name = f"{name}.{file_format}"
            files.append(
                DownloadData(url=link, file_name=name, referer=self.response.url)
            )
        return files

    def download_lot(self, lot: BeautifulSoup):
        return []

    def trading_id(self, trading_card: BeautifulSoup):
        if id_ := trading_card.find("a", class_="search-item__lot"):
            return id_.get_text(strip=True).split()[0]
        logger.error(f"{self.response.url} :: Trading id not found")

    def trading_link(self, trading_card: BeautifulSoup):
        if trading_link := trading_card.find(
            "a", class_="search-item__subject-link"
        ).get("href"):
            return trading_link
        logger.error(f"{self.response.url} :: Trading link not found")

    def trading_number(self, trading_card: BeautifulSoup):
        return self.trading_id(trading_card)

    @property
    def trading_type(self):
        type_ = self.soup.find("span", text=contains("Способ проведения"))
        if not type_:
            logger.error(f"{self.response.url} :: Trading type not found")
            return
        type_ = type_.find_next("p").get_text(strip=True)
        for name, trading_type in {
            "аукцион": "auction",
            "предложен": "offer",
            "конкурс": "competition",
        }.items():
            if name in type_.lower():
                return trading_type
        logger.warning(f"{self.response.url} :: Unknown type - {type_}")

    @property
    def trading_form(self):
        return "open"

    @property
    def msg_number(self):
        return

    @property
    def case_number(self):
        return

    @property
    def trading_org(self):
        text = contains("Организатор торгов")
        if org := self.soup.find("span", text=text) or self.soup.find("dt", text=text):
            return org.find_next("p").get_text(strip=True)
        logger.error(f"{self.response.url} :: Trading org not found")

    @property
    def trading_org_inn(self):
        match = re.search(r"\bИНН (\d{10,12})\b", self.trading_org)
        if match:
            inn = match.group(1)
            return CheckIfCorrectContactInfo.check_inn(inn)
        logger.warning(f"{self.response.url} :: Trading org inn not found")

    @property
    def trading_org_contacts(self):
        if phone := self.soup.find("td", text=contains("Телефон")):
            phone = phone.find_next("p").get_text(strip=True)
        else:
            phone = None
        if email := self.soup.find("td", text=contains("E-mail")):
            email = email.find_next("p").get_text(strip=True)
        else:
            email = None
        return {"phone": phone, "email": email}

    @property
    def arbit_manager(self):
        return

    @property
    def arbit_manager_inn(self):
        return

    @property
    def arbit_manager_org(self):
        return

    @property
    def debtor_inn(self):
        return

    def get_lots(self):
        return self.soup.find_all("div", class_="lot-item")

    def address(self, lot: BeautifulSoup):
        if address := lot.find("div", class_="lot-item__region"):
            return address.get_text(strip=True)
        logger.warning(f"{self.response.url} :: Address not found")

    @property
    def status(self):
        return

    def categories(self, lot: BeautifulSoup):
        if categories := lot.find("td", text=contains("Категория")):
            return categories.find_next("p").get_text(strip=True)
        logger.warning(f"{self.response.url} :: Categories not found")

    @property
    def lot_id(self):
        return

    @property
    def lot_link(self):
        return

    @property
    def short_name(self):
        if short_name := self.soup.find("div", class_="lot-item__subject"):
            return short_name.get_text(strip=True)
        logger.warning(f"{self.response.url} :: Short name not found")

    @property
    def lot_info(self):
        return

    @property
    def property_information(self):
        return

    def start_date_requests(self, lot: BeautifulSoup):
        if date := (
            lot.find("td", text=contains("Начало приёма заявок"))
            or lot.find("td", text=contains("Публикация извещения"))
        ):
            return return_parse_date(
                date.find_next("p").get_text(strip=True), "%d.%m.%y %H:%M:%S (МСК)"
            )
        logger.warning(f"{self.response.url} :: Start date requests not found")

    def end_date_requests(self, lot: BeautifulSoup):
        if date := lot.find("td", text=contains("Окончание приёма заявок")):
            format = "%d.%m.%y %H:%M:%S (МСК)"
        elif date := (
            lot.find("td", text=contains("Дата и время окончания приёма заявок"))
            or lot.find("td", text=contains("Приём заявок"))
        ):
            format = "до %d.%m.%y %H:%M:%S (МСК)"
        else:
            logger.warning(f"{self.response.url} :: End date requests not found")
            return
        return return_parse_date(date.find_next("p").get_text(strip=True), format)

    def start_date_trading(self, lot: BeautifulSoup):
        if date := lot.find("td", text=contains("Проведение торгов")):
            return return_parse_date(
                date.find_next("p").get_text(strip=True), "%d.%m.%y %H:%M:%S (МСК)"
            )
        logger.warning(f"{self.response.url} :: Start date trading not found")

    @property
    def end_date_trading(self):
        return

    def start_price(self, lot: BeautifulSoup):
        if price := lot.find("div", class_="lot-item__sum"):
            price = price.get_text(strip=True)
            if price == "НМЦ не указано":
                return
            return make_float(price)
        logger.warning(f"{self.response.url} :: Start price not found")

    def step_price(self, lot: BeautifulSoup):
        return
        # if price := lot.find('p', text=contains('Обеспечение заявки:')):
        #     price = price.find_next('span').get_text(strip=True)
        #     if price in ['не предусмотрено', 'в соответствии с лотовой документацией']:
        #         return
        #     return make_float(price)
        # logger.warning(f'{self.response.url} :: Step price not found')

    @property
    def periods(self):
        return
