import pandas as pd
from bs4 import BeautifulSoup

from app.db.models import DownloadData
from app.utils import (
    dedent_func,
    contains,
    DateTimeHelper,
    make_float,
    URL
)


class Combo:
    def __init__(self, response):
        self.response = response
        self.soup = BeautifulSoup(response.text, "lxml")

    def get_lots(self, data_origin: str):
        return [
            URL.url_join(data_origin, el.get("href"))
            for el in self.soup.find("h3", text=contains("Лоты"))
            .find("table")
            .find_all("a")
        ]

    @property
    def trading_id(self):
        return self.soup.find("span", class_="identifier").text

    @property
    def trading_link(self):
        return self.response.url

    @property
    def trading_number(self):
        return self.trading_id

    @property
    def trading_type(self):
        type_ = (
            self.soup.find("td", text="Способ проведения процедуры")
            .find_next("td")
            .text
        )
        if "аукцион" in type_.lower():
            return "auction"
        else:
            return None  # TODO

    @property
    def trading_form(self):
        return "open"

    @property
    def trading_org(self):
        return dedent_func(
            self.soup.find("td", text="Организатор").find_next("td").text
        )

    @property
    def trading_org_inn(self):
        return None

    @property
    def trading_org_contacts(self):
        return {"email": None, "phone": None}

    @property
    def msg_number(self):
        return None

    @property
    def case_number(self):
        return None

    @property
    def debtor_inn(self):
        return None

    @property
    def address(self): ...  # TODO

    @property
    def arbit_manager(self):
        return None

    @property
    def arbit_manager_org(self):
        return None

    @property
    def arbit_manager_inn(self):
        return None

    @property
    def status(self):
        mapping = {"Завершена процедура": "ended"}  # TODO
        return mapping.get(self.soup.find("div", class_=contains("rangeStage")).text)

    @property
    def lot_id(self):
        return self.soup.find("span", class_="identifier").text

    @property
    def lot_link(self):
        return self.response.url

    @property
    def lot_number(self):
        return self.soup.find("td", text="Номер лота").text

    @property
    def short_name(self):
        return dedent_func(self.soup.find("div", class_=contains("etpp-small")).text)

    @property
    def property_information(self):
        return None  # TODO

    @property
    def lot_info(self):
        return dedent_func(self.soup.find("td", text="предмет торгов").text)

    def parse_date(self, date):
        months = {
            "янв": "01",
            "фев": "02",
            "мар": "03",
            "апр": "04",
            "май": "05",
            "июн": "06",
            "июл": "07",
            "авг": "08",
            "сен": "09",
            "окт": "10",
            "ноя": "11",
            "дек": "12",
        }
        parts = date.split()
        day = parts[0]
        month = months[parts[1]]
        year = parts[2]
        time = parts[3]

        formatted = f"{day}.{month}.{year} {time}"
        return DateTimeHelper.smart_parse(formatted).astimezone(DateTimeHelper.moscow_tz)

    @property
    def start_date_requests(self):
        date = self.soup.find(
            "span", text=contains("Начало срока подачи заявок")
        ) or self.soup.find("span", text=contains("Начало подачи заявок"))
        if not date:
            return None

        return self.parse_date(
            date.find_next("td").text.strip().replace("\xa0", " ").replace(" МСК", ""),
        )

    @property
    def end_date_requests(self):
        date = self.soup.find(
            "span", text=contains("Окончание срока подачи заявок")
        ) or self.soup.find("span", text=contains("Окончание подачи заявок"))
        if not date:
            return None
        return self.parse_date(
            date.find_next("td").text.strip().replace("\xa0", " ").replace(" МСК", ""),
        )

    @property
    def start_date_trading(self):
        date = self.soup.find("span", text=contains("Начало проведение торгов"))
        if not date:
            return None
        return self.parse_date(
            date.find_next("td").text.strip().replace("\xa0", " ").replace(" МСК", ""),
        )

    @property
    def end_date_trading(self):
        date = self.soup.find("span", text=contains("Окончание проведения торгов"))
        if not date:
            return None

        return DateTimeHelper.smart_parse(
            date.find_next("td").text.strip().replace("\xa0", " ").replace(" МСК", ""),
        ).astimezone(DateTimeHelper.moscow_tz)

    @property
    def start_price(self):
        return make_float(
            (
                self.soup.find("td", text=contains("Начальная (минимальная) цена"))
                or self.soup.find("td", text=contains("Начальная цена договора"))
            )
            .find_next("td")
            .text.strip()
            .replace("\xa0", " ")
        )

    @property
    def step_price(self):
        price = self.soup.find("td", text="Шаг торгов")
        if not price:
            return None

        return make_float(price.find_next("td").text.strip().replace("\xa0", " "))

    @property
    def periods(self):
        periods = []
        table = self.soup.find("table", id="tablewrapper_0")
        table = pd.read_html(str(table))
        df = table[0]
        for el in list(df.iterrows()):
            s = el[1]
            start = s.iloc[1]
            end = s.iloc[2]
            price = s.iloc[3]
            period = {
                "start_date_requests": self.parse_date(start),
                "end_date_requests": self.parse_date(end),
                "end_date_trading": self.parse_date(end),
                "current_price": make_float(price),
            }
            periods.append(period)
        return periods

    def download_files(self):
        download_data = []
        links = self.soup.find("h3", text=contains("Сообщения"))
        if not links:
            return None
        links = links.find_next('table').find_all("a")
        for link in links:
            url = link.get("href")
            name = link.get('value')
            download_data.append(DownloadData(file_name=name, url=url))
        return download_data
