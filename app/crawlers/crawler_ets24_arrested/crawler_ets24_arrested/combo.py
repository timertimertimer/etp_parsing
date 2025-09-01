from bs4 import BeautifulSoup

from app.crawlers.crawler_ets24_arrested.crawler_ets24_arrested.config import base_url
from app.db.models import DownloadData
from app.utils import URL, dedent_func, Contacts, DateTimeHelper, make_float


class Combo:
    def __init__(self, response):
        self.response = response
        self.soup = BeautifulSoup(response.text, "lxml")

    def get_lots(self) -> list[str]:
        lots = []
        for tr in self.soup.find("table", id="auction-table").find_all("tr")[1:]:
            href = tr.find("a").get("href")
            lots.append(URL.url_join(base_url, href))
        return lots

    @property
    def trading_id(self):
        return self.response.url.split("OID=")[-1]

    @property
    def trading_number(self):
        return self.trading_id

    def get_trade_table(self):
        return self.soup.find(
            "h3", text="Общие сведения о проведении торгов"
        ).find_next("table")

    @property
    def trading_type(self):
        return {
            "Аукцион": "auction",
            "Публичное предложение": "offer",
            "Конкурс": "competition",
            "Специализированный аукцион": "auction",
        }.get(
            self.get_trade_table()
            .find("td", text="Форма представления торгов")
            .find_next("td")
            .text.strip()
        )

    @property
    def trading_form(self):
        return {"Открытая": "open", "Закрытая": "closed"}.get(
            self.get_trade_table()
            .find("td", text="Форма представления предложений о цене")
            .find_next("td")
            .text.strip()
        )

    def get_org_table(self):
        return self.soup.find("h3", text="Сведения об организаторе торгов").find_next(
            "table"
        )

    @property
    def trading_org(self):
        return dedent_func(
            self.get_org_table()
            .find("td", text="Полное наименование")
            .find_next("td")
            .text.strip()
        )

    @property
    def trading_org_contacts(self):
        org_table = self.get_org_table()
        return {
            "phone": Contacts.check_phone(
                org_table.find("td", text="Телефон контактного лица организатора")
                .find_next("td")
                .text.strip()
            ),
            "email": Contacts.check_email(
                org_table.find("td", text="E-mail контактного лица организатора")
                .find_next("td")
                .text.strip()
            ),
        }

    @property
    def case_number(self):
        return None

    def get_debtor_table(self):
        return self.soup.find(
            "h3", text="Сведения о должнике и его имуществе"
        ).find_next("table")

    @property
    def debtor_inn(self):
        return None

    @property
    def address(self):
        return dedent_func(
            self.get_debtor_table()
            .find("td", text="Местонахождение предмета торгов (адрес)")
            .find_next("td")
            .text.strip()
        )

    @property
    def arbit_manager(self):
        return None

    @property
    def arbit_manager_inn(self):
        return None

    @property
    def arbit_manager_org(self):
        return None

    @property
    def status(self):
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
        return dedent_func(
            self.soup.find("div", class_="page-header-content").text.strip()
        )

    @property
    def lot_info(self):
        return dedent_func(
            self.get_debtor_table()
            .find(
                "td",
                text="Сведения об имуществе (предприятии) должника, выставляемом на торги, его составе, характеристиках, описание",
            )
            .find_next("td")
            .text.strip()
        )

    @property
    def property_information(self):
        return None

    def get_requests_table(self):
        return self.soup.find(
            "h3",
            text="Порядок представления заявок на участие в торгах (предложений о цене)",
        ).find_next("table")

    @property
    def start_date_requests(self):
        return DateTimeHelper.smart_parse(
            self.get_requests_table()
            .find("td", text="Дата и время начала подачи заявок")
            .find_next("td")
            .text.strip()
        ).astimezone(DateTimeHelper.moscow_tz)

    @property
    def end_date_requests(self):
        return DateTimeHelper.smart_parse(
            self.get_requests_table()
            .find("td", text="Дата и время окончания подачи заявок")
            .find_next("td")
            .text.strip()
        ).astimezone(DateTimeHelper.moscow_tz)

    @property
    def start_date_trading(self):
        return DateTimeHelper.smart_parse(
            self.get_trade_table()
            .find("td", text="Дата и время начала торгов")
            .find_next("td")
            .text.strip()
        ).astimezone(DateTimeHelper.moscow_tz)

    @property
    def end_date_trading(self):
        date = self.get_trade_table().find("td", text="Дата и время окончания торгов")
        if date:
            date = DateTimeHelper.smart_parse(date.find_next("td").text.strip()).astimezone(DateTimeHelper.moscow_tz)
        return date

    @property
    def start_price(self):
        return make_float(
            self.get_trade_table()
            .find("td", text="Начальная цена (НДС не облагается), руб.")
            .find_next("td")
            .text.strip()
        )

    @property
    def step_price(self):
        price = self.get_trade_table().find("td", text="Шаг аукциона, руб.")
        if price:
            price = make_float(
                price
                .find_next("td")
                .text.strip()
            )
        return price

    @property
    def periods(self):
        return None

    def download_general(self):
        files = []
        for a in self.soup.find("h3", text="Документы").find_parent("td").find_all("a"):
            link = a["href"]
            name = a.text.strip()
            files.append(
                DownloadData(url=URL.url_join(base_url, link), file_name=name, referer=self.response.url)
            )
        return files

    def download_lot(self):
        return []