import pathlib
import re

import pandas as pd
from itertools import takewhile
from bs4 import BeautifulSoup
from app.utils import (
    dedent_func,
    Contacts,
    contains,
    URL,
    DateTimeHelper,
    logger,
    make_float,
)
from app.db.models import DownloadData
from app.utils.config import image_formats


class Combo:
    def __init__(self, response):
        self.response = response
        self.soup = BeautifulSoup(self.response.text, "lxml")

    def get_lots(self, html: str):
        soup = BeautifulSoup(html, "lxml")
        lots = []
        for lot in soup.find_all("div", class_="ty-compact-list__item"):
            lot_number = lot.find("div", class_="lot-info-sku").text.strip()
            short_name = dedent_func(
                lot.find("div", class_="lot-info-name").text.strip()
            )
            status = self.parse_status(
                lot.find("div", class_="lot-info-status").text.strip()
            )
            link = lot.find("a", class_="product-title").get("href")
            lots.append([link, lot_number, short_name, status])
        return lots

    def next_page(self, html):
        soup = BeautifulSoup(html, "lxml")
        next_page = soup.find("a", class_="ty-pagination__next")
        return next_page

    def parse_status(self, status):
        d = {
            "active": [
                "подача заявок",
                "опубликована",
                "опубликован проект",
                "размещена в еис",
                "подача предложений",
                "идет прием заявок",
            ],
            "pending": [
                "рассмотрение заявок",
                "ожидает рассмотрения заявок",
                "ожидает начала подачи предложений",
                "подведение итогов",
            ],
            "ended": [
                "завершена",
                "рассмотрение предложений/подведение итогов",
                "отменена",
                "процедура отменена",
                "процедура по лоту проведена",
                "подведение итогов по окончании периода",
                "процедура не состоялась",
                "прием заявок завершен",
                "прием заявок приостановлен",
            ],
        }
        for key, value in d.items():
            if status.lower() in value:
                return key
        logger.error(f"{self.response.url} | Unknown status - {status}")
        return None

    def parse_price(self, price: str):
        return make_float(price)

    def download_general(self):
        files = list()
        for file in self.soup.find("div", id="content_documents").find_all(
                "div", class_="attachment__item"
        ):
            name = file.get_text(strip=True).split("\n")[0]
            link = file.find("a", class_="attachment__a cm-no-ajax")
            if not link:
                continue
            link = link.get("href")
            files.append(
                DownloadData(url=link, file_name=name, referer=self.response.url)
            )
        return files

    def download_lot(self):
        images = list()
        for i, image in enumerate(self.soup.find("div", class_="ty-product-block__img").find_all(
                "img"
        )):
            link = image.get("src")
            name = URL.clean_url(link).split("/")[-1]
            path = pathlib.Path(name)
            images.append(
                DownloadData(
                    url=link, file_name=name, referer=self.response.url,
                    is_image=path.suffix.lower() in image_formats,
                    order=i
                )
            )
        return images

    def get_main_info(self):
        return self.soup.find("div", class_="ty-product-block_product_main")

    def get_trading_type_value(self):
        return (
            self.get_main_info()
            .find("dt", text=contains("Вид процедуры"))
            .find_next("dd")
            .text.strip()
        )

    @property
    def trading_id(self):
        return (
            self.get_main_info()
            .find("dt", text=contains("Код процедуры"))
            .find_next("dd")
            .text.strip()
        )

    @property
    def trading_link(self):
        return self.response.url

    @property
    def trading_type(self):
        type_ = self.get_trading_type_value()
        d = {
            "auction": [
                "аукцион с открытой формой подачи предложений",
                "аукцион",
                "аукцион на повышение",
                "аукцион на понижение",
                "аукцион с закрытой формой подачи предложений",
            ],
            "offer": [
                "запрос предложений",
                "продажа посредством публичного предложения",
                "публичная оферта",
                "сбор предложений"
            ],
            "competition": [
                "конкурс",
                "конкурс с открытой формой подачи предложений",
                "конкурс с закрытой формой подачи предложений",
            ],
        }
        for key, value in d.items():
            if type_.lower() in value:
                return key
        logger.error(f"{self.response.url} | Unknown type - {type_}")
        return None

    @property
    def trading_form(self):
        type_ = self.get_trading_type_value()
        if "закрыт" in type_.lower():
            return "closed"
        return "open"

    def get_organizer(self):
        return self.soup.find("div", id="content_organizer")

    @property
    def trading_org(self):
        return dedent_func(
            self.get_organizer()
            .find(
                "label", class_="ty-control-group__label", text=contains("Наименование")
            )
            .find_next("span")
            .get_text(strip=True)
        )

    @property
    def trading_org_contacts(self):
        return {
            "email": Contacts.check_email(
                self.get_organizer()
                .find(
                    "label",
                    class_="ty-control-group__label",
                    text=contains("Электронная почта"),
                )
                .find_next("span")
                .get_text(strip=True)
            ),
            "phone": Contacts.check_phone(
                self.get_organizer()
                .find(
                    "label", class_="ty-control-group__label", text=contains("Телефон")
                )
                .find_next("span")
                .get_text(strip=True)
            ),
        }

    def get_debtor(self):
        return self.soup.find("div", id="content_debtor")

    @property
    def msg_number(self):
        debtor = self.get_debtor()
        if debtor and debtor.has_attr("data-ca-accordion-is-active-scroll-to-elm"):
            number = debtor.find(
                "td",
                class_="key",
                text=contains("Номер объявления о проведении торгов в ЕФРСБ"),
            )
            if number:
                return Contacts.check_msg_number(
                    number.find_next("td").get_text(strip=True)
                )
        return None

    @property
    def case_number(self):
        debtor = self.get_debtor()
        if debtor and debtor.has_attr("data-ca-accordion-is-active-scroll-to-elm"):
            return Contacts.check_case_number(
                debtor.find(
                    "td", class_="key", text=contains("Реквизиты судебного")
                )
                .find_next("td")
                .get_text(strip=True)
            )
        return None

    @property
    def debtor_inn(self):
        debtor = self.get_debtor()
        if debtor and debtor.has_attr("data-ca-accordion-is-active-scroll-to-elm"):
            return Contacts.check_inn(
                debtor.find("td", class_="key", text=contains("ИНН"))
                .find_next("td")
                .get_text(strip=True)
            )
        return None

    @property
    def address(self):
        debtor = self.get_debtor()
        if debtor and debtor.has_attr("data-ca-accordion-is-active-scroll-to-elm"):
            return Contacts.check_address(
                debtor.find("td", class_="key", text=contains("Почтовый адрес"))
                .find_next("td")
                .get_text(strip=True)
            )

        return Contacts.check_address(
            self.get_main_info()
            .find("dt", text=re.compile(r"Адрес|Регион"))
            .find_next("dd")
            .text.strip()
        )

    @property
    def sud(self):
        debtor = self.get_debtor()
        if debtor and debtor.has_attr("data-ca-accordion-is-active-scroll-to-elm"):
            return Contacts.check_address(
                debtor.find("td", class_="key", text=contains("Наименование суда"))
                .find_next("td")
                .get_text(strip=True)
            )
        return None

    @property
    def arbit_manager(self):
        debtor = self.get_debtor()
        if debtor and debtor.has_attr("data-ca-accordion-is-active-scroll-to-elm"):
            return " ".join(
                debtor.find(
                    "label",
                    class_="ty-control-group__label",
                    text=re.compile(r"Арбитражный управляющий|Конкурсный управляющий"),
                )
                .find_next("td", class_="key", text=contains("ФИО"))
                .find_next("td")
                .get_text(strip=True)
                .split()
            )
        if fio := self.get_organizer().find(
                "label",
                class_="ty-control-group__label",
                text=contains("Контактное лицо"),
        ):
            return fio.find_next("span").get_text(strip=True)
        return None

    @property
    def arbit_manager_inn(self):
        debtor = self.get_debtor()
        if debtor and debtor.has_attr("data-ca-accordion-is-active-scroll-to-elm"):
            return " ".join(
                debtor.find(
                    "label",
                    class_="ty-control-group__label",
                    text=re.compile(r"Арбитражный управляющий|Конкурсный управляющий"),
                )
                .find_next("td", class_="key", text=contains("ИНН"))
                .find_next("td")
                .get_text(strip=True)
                .split()
            )
        return None

    @property
    def arbit_manager_org(self):
        debtor = self.get_debtor()
        if debtor and debtor.has_attr("data-ca-accordion-is-active-scroll-to-elm"):
            if sro := debtor.find(
                    "label",
                    class_="ty-control-group__label",
                    text=re.compile("Арбитражный управляющий"),
            ):
                return " ".join(
                    sro.find_next("td", class_="key", text=contains("СРО"))
                    .find_next("td")
                    .get_text(strip=True)
                    .split()
                )
        return self.trading_org

    @property
    def lot_id(self):
        return self.trading_link.split("product_id=")[-1]

    @property
    def lot_link(self):
        return self.trading_link

    def get_lot_number(self, short_name):
        pattern = re.compile(
            r"^Лот.?\W\s?\d{1,}\:?|^Лот.?\W\d{1,}\.?", flags=re.IGNORECASE
        )
        if short_name:
            match = pattern.findall(str(short_name))
        else:
            match = None
        if match:
            lot_number = "".join(re.findall(r"\d+", "".join(match)))
        else:
            return "1"
        if len(lot_number) < 5:
            return lot_number
        return "1"

    @property
    def lot_info(self):
        return dedent_func(
            self.get_main_info()
            .find("div", class_="ty-product__full-description")
            .get_text(strip=True)
        )

    @property
    def property_information(self):
        if info := self.soup.find("div", class_="review_order"):
            return dedent_func(info.find("span").get_text(strip=True))
        return None

    def get_auction_info_body(self):
        return self.soup.find("div", class_="ty-product-block_auction_info__body")

    def get_auc_dates_link(self):
        return (
                "https://catalog.lot-online.ru/e-auction/auctionLotProperty.v.xhtml?" + URL.return_only_param(
            self.get_main_info()
            .find("span", text=contains("Код лота"))
            .find_next("dd")
            .find("a")
            .get("href")
            .strip()
        )
        )

    def get_date_requests(self):
        return (
            self.get_auction_info_body()
            .find("label", text=contains("Период приёма заявок"))
            .find_next("span", class_="ty-control-group__item")
            .find_all("span")
        )

    @property
    def start_date_requests_auc(self):
        if date := DateTimeHelper.smart_parse(self.get_date_requests()[0].text.strip()):
            return date.astimezone(DateTimeHelper.moscow_tz)
        return None

    @property
    def end_date_requests_auc(self):
        if date := DateTimeHelper.smart_parse(self.get_date_requests()[1].text.strip()):
            return date.astimezone(DateTimeHelper.moscow_tz)
        return None

    @property
    def start_price(self):
        if start_price := self.soup.find("div", class_="start_price"):
            return self.parse_price(
                start_price.find("span").get_text(strip=True).replace("&nbsp;", "")
            )
        return None

    @property
    def step_price(self):
        if step_price := self.get_auction_info_body().find(
                "label", text=contains("Шаг")
        ):
            return self.parse_price(step_price.find_next("span").text.strip())
        return None

    @property
    def periods(self):
        table = self.soup.find("div", class_="tab_rad_reduction")
        if not table:
            return None
        td_periods = pd.read_html(str(table.find("table")))[0]
        periods = []
        for p in range(len(td_periods)):
            start_requests = td_periods.iloc[p][0]
            end_requests = td_periods.iloc[p][1]
            end_trading = td_periods.iloc[p][2]
            price_ = td_periods.iloc[p][4]
            price = self.parse_price(
                "".join(takewhile(lambda x: x != "р" and x != "Р", price_))
            )
            try:
                period = {
                    "start_date_requests": DateTimeHelper.smart_parse(start_requests).astimezone(
                        DateTimeHelper.moscow_tz
                    ),
                    "end_date_requests": DateTimeHelper.smart_parse(end_requests).astimezone(DateTimeHelper.moscow_tz),
                    "end_date_trading": DateTimeHelper.smart_parse(end_trading).astimezone(DateTimeHelper.moscow_tz),
                    "current_price": price,
                }
                periods.append(period)
            except Exception as e:
                continue
        return periods
