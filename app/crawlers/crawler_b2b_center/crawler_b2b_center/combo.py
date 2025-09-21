import re

from bs4 import BeautifulSoup

from app.utils import Contacts, dedent_func, DateTimeHelper, make_float


class Combo:
    def __init__(self, response):
        self.response = response
        self.soup = BeautifulSoup(response.text, "lxml")

    def download_general(self):
        return []

    def download_lot(self):
        return []

    @property
    def trading_id(self):
        return self.response.url.split("?id=")[1]

    @property
    def trading_link(self):
        return self.response.url

    @property
    def trading_number(self):
        return self.trading_id

    @property
    def trading_type(self):
        return "rfp"

    @property
    def trading_form(self):
        return "open"

    def get_trading_org_td(self):
        try:
            return self.soup.find("tr", id="trade-info-organizer-name").find_all("td")[
                1
            ]
        except Exception as e:
            return None

    @property
    def trading_org(self):
        return self.get_trading_org_td().get_text(strip=True)

    @property
    def trading_org_contacts(self):
        email = Contacts.check_email(
            self.soup.find("tr", id="trade-info-organizer-email")
            .find_all("td")[1]
            .get_text(strip=True)
        )
        phone = Contacts.check_phone(
            self.soup.find("tr", id="trade-info-organizer-phone")
            .find_all("td")[1]
            .get_text(strip=True)
        )
        return {"email": email, "phone": phone}

    @property
    def address(self):
        return (
            self.soup.find("tr", id="trade-info-organizer-fact-address")
            .find_all("td")[1]
            .get_text(strip=True)
        )

    @property
    def short_name(self):
        if headline := self.soup.find(
            "h1", class_="h3", attrs={"itemprop": "headline"}
        ):
            return dedent_func(headline.find("div", class_="s2").get_text(strip=True))
        return None

    @property
    def lot_info(self):
        return None

    @property
    def categories(self):
        categories = []
        if okpd2 := self.soup.find("tr", id="trade-info-okpd2"):
            category = re.sub(r"\s+", " ", okpd2.find_all("td")[1].get_text()).strip()
            categories.append(category)
        if okved2 := self.soup.find("tr", id="trade-info-okved2"):
            category = re.sub(r"\s+", " ", okved2.find_all("td")[1].get_text()).strip()
            categories.append(category)
        return categories

    @property
    def property_information(self):
        if text := self.soup.find(
            "td", text="Порядок предоставления документации по закупке:"
        ):
            return dedent_func(text.find_next("td").get_text(strip=True))
        return None

    @property
    def start_date_requests(self):
        if date := (self.soup.find("td", text="Дата публикации:")):
            return DateTimeHelper.smart_parse(
                date.find_next("td").get_text(strip=True)
            ).astimezone(DateTimeHelper.moscow_tz)
        return None

    @property
    def end_date_requests(self):
        if date := (
            self.soup.find("td", text="Дата окончания подачи заявок:")
            or self.soup.find(
                "td", text="Дата окончания подачи заявок основного этапа:"
            )
        ):
            return DateTimeHelper.smart_parse(
                date.find_next("td").get_text(strip=True)
            ).astimezone(DateTimeHelper.moscow_tz)
        return None

    @property
    def start_date_trading(self):
        return None

    @property
    def end_date_trading(self):
        return None

    @property
    def start_price(self):
        if price := (
            self.soup.find("td", text="Цена за единицу продукции:")
            or self.soup.find("td", text="Общая стоимость закупки:")
        ):
            return make_float(price.find_next("td").get_text(strip=True))
        return None

    @property
    def step_price(self):
        return None

    @property
    def periods(self):
        return None

    @property
    def trading_org_inn(self):
        if inn := self.soup.find("td", text="ИНН"):
            return Contacts.check_inn(inn.find_next('td').get_text(strip=True))
        return None
