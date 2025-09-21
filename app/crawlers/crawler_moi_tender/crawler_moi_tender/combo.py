import re
from bs4 import BeautifulSoup, NavigableString

from .config import data_origin_url
from app.utils import (
    dedent_func,
    make_float,
    contains,
    URL,
    Contacts,
    DateTimeHelper,
)
from app.db.models import DownloadData


class Combo:
    def __init__(self, response):
        self.response = response
        self.soup = BeautifulSoup(response.text, "lxml")

    def get_lots(self):
        lots = self.soup.find_all("div", class_="tender")
        lots_data = []
        for lot in lots:
            status = dedent_func(lot.find("div", class_="status").get_text(strip=True))
            if "закрыт" in status.lower():  # Доступ по паролю
                trading_form = "closed"
                status = "ended"
            else:
                trading_form = "open"
                status = "active"
            short_desc = lot.find("div", class_="short-desc")
            trading_link = short_desc.find("a")["href"]
            short_name = dedent_func(short_desc.find("a").get_text(strip=True))
            region_city = lot.find("div", class_="region-city")
            span = region_city.find("span")
            address = dedent_func(span.find("b").get_text())
            trading_id = trading_number = dedent_func(
                lot.find("div", class_="num").get_text(strip=True).replace("№", "")
            )
            start_price = lot.find("div", class_="price")
            if start_price:
                start_price = start_price.findNext("div").get_text().strip()
                if start_price:
                    return make_float(start_price)
            category = dedent_func(
                lot.find("div", class_="tender-cat").find("b").get_text(strip=True)
            )
            company = lot.find("div", class_="company").find("a")
            org = dedent_func(company.get_text(strip=True))
            org_link = dedent_func(company["href"])
            lots_data.append(
                {
                    "trading_id": trading_id,
                    "trading_link": trading_link,
                    "trading_number": trading_number,
                    "trading_form": trading_form,
                    "start_price": start_price,
                    "category": category,
                    "org": org,
                    "org_link": org_link,
                    "status": status,
                    "short_name": short_name,
                    "address": address,
                }
            )
        return lots_data

    def download_trade(self):
        files = list()
        links = self.soup.find("div", class_="title", text=contains("Документация"))
        if not links:
            return files
        for link in links.parent.find_all("div", class_="isfile") or []:
            a = link.find("a")
            name = a.get_text().strip()
            link = URL.url_join(data_origin_url, a.get("href"))
            files.append(
                DownloadData(file_name=name, url=link, referer=self.response.url)
            )
        return files

    def download_lot(self):
        return []

    @property
    def trading_org_contacts(self):
        phone = None
        profile_page = self.get_profile_page()
        email = profile_page.find("a", href=re.compile("mailto:"))
        if email:
            email_ = Contacts.check_email(
                dedent_func(email.get("href").removeprefix("mailto:"))
            )
            phone = email.find_next("div", class_="value")
            if phone:
                phone = Contacts.check_phone(phone.get_text())
            email = email_
        return {"email": email, "phone": phone}

    @property
    def trading_org_inn(self):
        profile_page = self.get_profile_page()
        inn = profile_page.find("div", class_="value", text=contains("ИНН"))
        if inn:
            inn = inn.get_text(strip=True).split()[-1]
            return dedent_func(Contacts.check_inn(inn))
        return None

    def get_profile_page(self):
        return self.soup.find("div", class_="profile-page")

    @property
    def lot_number(self):
        return "1"

    @property
    def lot_info(self):
        info = self.soup.find("div", class_="description")
        if info:
            return dedent_func(info.get_text())
        return None

    @property
    def property_information(self):
        return

    @property
    def start_date_requests(self):
        start = (
            self.soup.find(
                "div", class_="label", text=contains("Дата публикации извещения")
            )
            .find_next("div")
            .get_text(strip=True)
        )
        return DateTimeHelper.smart_parse(start).astimezone(DateTimeHelper.moscow_tz)

    @property
    def end_date_requests(self):
        div = self.soup.find(
            "div", class_="label", text=contains("Дата окончания приема заявок")
        ).find_next("div")
        return DateTimeHelper.smart_parse(
            "".join(
                child for child in div.contents if isinstance(child, NavigableString)
            )
            .strip()
            .replace("/ ", "")
        ).astimezone(DateTimeHelper.moscow_tz)

    @property
    def start_date_trading(self):
        return

    @property
    def end_date_trading(self):
        return

    @property
    def step_price(self):
        return

    @property
    def periods(self):
        return
