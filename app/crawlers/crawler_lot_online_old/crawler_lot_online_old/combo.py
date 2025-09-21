import pathlib
import re
from bs4 import BeautifulSoup

from app.utils import URL, contains, dedent_func, DateTimeHelper, logger, make_float
from app.db.models import DownloadData
from app.utils.config import image_formats


class Combo:
    addresses = dict()

    def __init__(self, response):
        self.response = response
        self.soup = BeautifulSoup(response.text, "lxml")

    def download_general(self):
        return []

    def download_lot(self, data_origin):
        files = list()
        for link in self.soup.find("div", id="lot_documents").find_all("a"):
            name = link.get_text().strip()
            link = link.get("href")
            path = pathlib.Path(name)
            files.append(
                DownloadData(
                    url=URL.url_join(data_origin, link),
                    file_name=name,
                    referer=self.response.url,
                    is_image=path.suffix.lower() in image_formats,
                )
            )

        images = []
        lot_images = (
            self.soup.find("div", id="lot_photos") or
            self.soup.find("div", id="img-container") or
            self.soup.find("div", class_="img-container")
        ).find_all("img")
        for i, image in enumerate(lot_images):
            relative_link = image.get('src')
            absolute_link = URL.url_join(data_origin, relative_link)
            name = relative_link.split("/")[-1]
            images.append(
                DownloadData(
                    url=absolute_link,
                    file_name=name,
                    referer=self.response.url,
                    is_image=True,
                    order=i
                )
            )
        files.extend(images)
        return files

    @property
    def trading_type(self):
        type_ = self.soup.find("strong", text=contains("Вид процедуры:"))
        if type_:
            type_ = type_.find_next("span").text.strip().lower()
            if any(
                    [
                        "аукцион" in type_,
                        "сессия" in type_,
                    ]
            ):
                return "auction"
            elif "конкурс" in type_:
                return "competition"
            elif "предложени" in type_:
                return "offer"
        return None

    @property
    def trading_org(self):
        org = self.soup.find("strong", text=contains("Организатор"))
        if org:
            org = org.find_next("span").text.strip()
            return dedent_func(org)
        return None

    @property
    def status(self):
        status = self.soup.find("p", id="lot_status")
        if status:
            status = status.text.strip().lower()
            if status in (
                    "подача заявок",
                    "опубликована",
                    "опубликован проект",
                    "размещена в еис",
                    "подача предложений",
            ):
                return "active"
            elif status in (
                    "рассмотрение заявок",
                    "ожидает рассмотрения заявок",
                    "ожидает начала подачи предложений",
            ):
                return "pending"
            elif status in (
                    "завершена",
                    "рассмотрение предложений/подведение итогов",
                    "отменена",
                    "приостановлено",
            ):
                return "ended"
        return None

    @property
    def category(self):
        category = self.soup.find("strong", text=contains("Категория"))
        if category:
            categories = category.find_next("span").text.strip().split("/")
            categories_ = []
            for category in categories:
                category = category.strip()
                if category == "Рубрикатор":
                    continue
                categories_.append(category)
            return categories_
        return None

    @property
    def address(self):
        country = self.soup.find("strong", text=contains("Страна"))
        if country:
            country = country.find_next("span").text.strip()
        address = self.soup.find("strong", text=contains("Адрес"))
        if address:
            address = address.find_next("span").text.strip()
            address = dedent_func(f"{country}, {address}")
            return address
        return None

    @property
    def lot_info(self):
        info = self.soup.find("strong", text=contains("Описание лота"))
        if info:
            info = info.find_next("span").text.strip()
            return dedent_func(info)
        return None

    @property
    def start_date_requests(self):
        return self.get_dates_from_interval("Прием заявок")[0]

    @property
    def end_date_requests(self):
        return self.get_dates_from_interval("Прием заявок")[1]

    @property
    def start_date_trading(self):
        return self.get_dates_from_interval("Подача предложений")[0]

    @property
    def end_date_trading(self):
        return self.get_dates_from_interval("Подача предложений")[1]

    def get_dates_from_interval(self, label):
        date_requests = self.soup.find("strong", text=contains("Прием заявок"))
        if date_requests:
            date_requests = (
                date_requests.find_next("span").text.strip().replace(" ", " ")
            )
            start, end = date_requests.split(" - ")
            format = "%d/%m/%Y %H:%M"
            cleaned_start = re.sub(r"\*?\s*\(.*\)", "", start)
            cleaned_end = re.sub(r"\*?\s*\(.*\)", "", end)
            return (
                DateTimeHelper.smart_parse(cleaned_start, format).astimezone(DateTimeHelper.moscow_tz),
                DateTimeHelper.smart_parse(cleaned_end, format).astimezone(DateTimeHelper.moscow_tz)
            )
        return None

    @property
    def start_price(self):
        p = self.get_acitvity_table().find("span", id="priceStart")
        if p:
            return make_float(p.get_text().strip())
        return None

    @property
    def step_price(self):
        p = self.get_acitvity_table().find("td", id="priceStepUp")
        if p:
            return make_float(p.get_text().strip())
        return None

    @property
    def min_price(self):
        p = self.get_acitvity_table().find("span", id="priceMin")
        if p:
            return make_float(p.get_text().strip())
        return None

    def get_acitvity_table(self):
        return self.soup.find("table", class_="tbl-activity")

    @property
    def deposit(self):
        try:
            p = self.soup.find("strong", text=contains("Сумма задатка"))
            if p:
                p = p.find_next("span").text.strip()
                p = re.sub(r"\s", "", dedent_func(p).replace(",", "."))
                p = "".join([x for x in p if x.isdigit() or x == "."])
                if len(p) > 0:
                    return round(float(p), 2)
        except ValueError as e:
            logger.error(f"{self.response.url} :: INVALID DEPOSIT PRICE\n{e}")
        return None

    @property
    def periods(self):
        return None
