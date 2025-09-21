import pathlib
import re
import pandas as pd
from bs4 import BeautifulSoup as BS

from app.utils import (
    dedent_func,
    Contacts,
    normalize_string,
    DateTimeHelper,
    URL,
    logger,
)
from app.db.models import DownloadData
from ..locators.trade_locator import TradeLocator
from ..config import data_origin_url


class OfferParse:
    def __init__(self, response):
        self.response = response
        self.soup = BS(response.text, "lxml")

    @property
    def data_origin(self):
        return data_origin_url

    @property
    def trading_id(self):
        _id = re.findall(r"\d+", str(self.trading_link))
        return _id[0]

    @property
    def trading_link(self):
        return "-".join(self.response.url.split("-")[:-1])

    @property
    def trading_number(self):
        div = self.response.xpath(TradeLocator.trading_number_loc).get()
        div = BS(str(div), features="lxml").get_text()
        match = "".join(re.findall(r"\d+\-\w+", str(div)))
        if len(match) < 0:
            logger.warning(f"{self.response.url} | Couldn't parse trading_number")
        return match

    @property
    def trading_type(self):
        div = self.response.xpath(TradeLocator.trading_type_loc).get()
        div = BS(str(div), features="lxml").get_text().strip()
        return div

    @property
    def trading_org(self):
        try:
            td_org = self.response.xpath(TradeLocator.trading_organ_loc).get()
            td_org = dedent_func(BS(str(td_org), features="lxml").get_text()).strip()
            return "".join(re.sub(r"\s+", " ", td_org))
        except Exception as e:
            logger.warning(
                f"{self.response.url} | Couldn't parse trading_org. Error: {e}",
                exc_info=True,
            )
        return None

    @property
    def trading_org_inn(self):
        return (
            BS(
                str(self.response.xpath(TradeLocator.trading_org_inn_loc).get()),
                features="lxml",
            )
            .get_text()
            .strip()
        )

    def get_phone_number(self):
        try:
            phone = self.response.xpath(TradeLocator.phone_organ_loc).get()
            phone = (
                dedent_func(BS(str(phone), features="lxml").get_text())
                .replace(";", "")
                .strip()
            )
            return Contacts.check_phone(phone)
        except Exception as e:
            pass
        return None

    def get_email(self):
        try:
            email = self.response.xpath(TradeLocator.email_organ_loc).get()
            email = (
                dedent_func(BS(str(email), features="lxml").get_text())
                .replace(";", "")
                .strip()
            )
            return Contacts.check_email(email)
        except Exception as e:
            pass
        return None

    @property
    def trading_org_contacts(self):
        if self.get_phone_number():
            phone = self.get_phone_number()
        else:
            phone = None
        if self.get_email():
            email = self.get_email()
        else:
            email = None
        return {"email": email, "phone": phone}

    @property
    def msg_number(self):
        td_msg = self.response.xpath(TradeLocator.msg_number_loc).get()
        try:
            if not td_msg:
                return None
            td_msg = (
                "".join(BS(str(td_msg), features="lxml").get_text())
                .replace(",", " ")
                .replace("№", "")
                .replace(";", "")
                .replace(":", "")
                .strip()
            )
            match = "".join(re.findall(r"\d{1,2}\.\d{1,2}\.\d{2,4}", td_msg))
            if match:
                return (
                    "".join(td_msg)
                    .replace(match, "")
                    .replace("от", "")
                    .replace("-", "")
                    .replace("и", "")
                    .strip()
                )
            else:
                msg = dedent_func(re.sub(r"\s+", " ", td_msg))
                msg = " ".join(re.findall(r"(\d{8})", msg))
                msg = " ".join(
                    [n if int(n) or n == " " else "" for n in (re.split(r"\s", msg))]
                )
                return msg
        except Exception as e:
            logger.warning(
                f"{self.response.url} | Couldn't parse msg_number. Error: {e}"
            )
        return None

    @property
    def case_number(self):
        case_ = self.response.xpath(TradeLocator.case_number_loc).get()
        try:
            case_ = (
                "".join(BS(str(case_), features="lxml").get_text())
                .replace("№", "")
                .replace("\\", "/")
                .replace(" ", "")
                .strip()
            )
            if len(case_) < 42:
                return dedent_func(case_)
        except Exception as e:
            logger.warning(
                f"{self.response.url} | Couldn't parse case_number. Error: {e}"
            )
        return None

    @property
    def debitor_inn(self):
        try:
            trade_inn = dedent_func(
                BS(
                    self.response.xpath(TradeLocator.debitor_inn_loc).get(),
                    features="lxml",
                ).get_text()
            )
            pattern = re.compile(r"\d{10,12}")
            if pattern:
                return "".join(pattern.findall(trade_inn))
        except Exception as e:
            pass
        return None

    @property
    def arbitr_manager_org(self):
        try:
            td_org = self.response.xpath(TradeLocator.arbitr_manag_loc).get()
            if td_org is None:
                td_org = self.response.xpath(TradeLocator.finance_manag_loc).get()
            td_org = dedent_func(BS(str(td_org), features="lxml").get_text()).strip()
            if td_org != "None":
                return "".join(re.sub(r"\s+", " ", td_org))
        except Exception as e:
            logger.warning(f"{self.response.url} | INVALID DATA ARBITR NAME")
        return None

    @property
    def arbitr_inn(self):
        try:
            arbitr_inn = self.response.xpath(TradeLocator.arbitr_inn_loc).get()
            if arbitr_inn is None:
                arbitr_inn = self.response.xpath(TradeLocator.finance_inn_loc).get()
            arbitr_inn = dedent_func(BS(str(arbitr_inn), features="lxml").get_text())
            pattern = re.compile(r"\d{10,12}")
            if pattern:
                return "".join(pattern.findall(arbitr_inn))
        except Exception as e:
            pass
        return None

    @property
    def arbitr_org(self):
        try:
            td_company = self.response.xpath(TradeLocator.arbitr_org_loc).get()
            if td_company is None:
                td_company = self.response.xpath(TradeLocator.finance_org_loc).get()
            td_company = dedent_func(BS(str(td_company), features="lxml").get_text())
            if td_company != "None":
                if "(" in td_company:
                    td_company = "".join(
                        [
                            x if len(td_company) > 0 else None
                            for x in re.split(r"\(", td_company, maxsplit=1)[0]
                        ]
                    )
                return "".join(dedent_func(td_company))
        except Exception as e:
            logger.warning(f"{self.response.url} | INVALID DATA ARBITR COMPANY")
        return None

    @property
    def count_lots(self):
        return self.response.xpath(TradeLocator.count_lots_loc).getall()

    @property
    def lot_title(self):
        return dedent_func(self.response.xpath(TradeLocator.lot_title).get())

    @property
    def status(self):
        d = dict(
            active=(
                "идет прием заявок",
                "идет приём заявок",
                "торги в стадии приема заявок",
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

        status = self.response.xpath(TradeLocator.status_loc).get()
        if not status:
            return None
        status = status.strip().lower()
        for k, v in d.items():
            if status in v:
                return k
        return None

    def get_lot_id(self, lot):
        id_ = BS(lot, features="lxml").find("div", class_="lot-regnumber")
        if not id_:
            return None
        return id_.get_text(strip=True).removeprefix("Идентификационный номер: ")

    def get_lot_link(self, lot_num):
        return f"{self.trading_link}-{lot_num}"

    def get_lot_number(self, lot):
        return self.get_lot_id(lot).split("-")[-1]

    def get_short_name(self, lot_num: str):
        short_name = self.response.xpath(
            TradeLocator.short_name_loc.format(lot_num)
        ).get()
        if not short_name:
            return None
        return dedent_func(BS(str(short_name), features="lxml").get_text())

    def get_lot_info(self, lot_num: str):
        lot_info = self.response.xpath(TradeLocator.lot_info_loc.format(lot_num)).get()
        if not lot_info:
            return None
        return dedent_func(BS(str(lot_info), features="lxml").get_text())

    @property
    def address(self):
        address = self.response.xpath(TradeLocator.region_loc).get()
        if not address:
            address = self.response.xpath(TradeLocator.sud_loc).get()
        address = BS(str(address), features="lxml").get_text(strip=True)
        if address:
            return address
        return None

    @property
    def property_info(self):
        property_info = self.response.xpath(TradeLocator.property_info_loc).get()
        if not property_info:
            return None
        return dedent_func(BS(str(property_info), features="lxml").get_text())

    def get_start_price(self, lot_num: str):
        start_price = self.response.xpath(
            TradeLocator.start_price_loc.format(lot_num)
        ).get()
        try:
            start_price = dedent_func(BS(str(start_price), features="lxml").get_text())
            start_price = normalize_string(start_price)
            pattern = r"^\d+\.\d{1,2}"
            clean_price = "".join(
                filter(lambda x: x.isdigit() or x == ",", start_price)
            ).replace(",", ".")
            match = "".join(re.findall(pattern, clean_price))
            if match:
                return round(float(match), 2)
            else:
                logger.warning(
                    f"{self.response.url} | INVALID DATA START PRICE - LOT {lot_num}"
                )
        except Exception as e:
            logger.warning(
                f"{self.response.url} | LOT {lot_num} INVALID DATA - START PRICE - LOT {lot_num}"
            )
        return None

    def get_period_table(self, lot_num: str):
        try:
            table = self.response.xpath(
                TradeLocator.period_table_loc.format(lot_num)
            ).getall()
            soup = BS(str(table[0]), features="lxml")
            class_shortdate = soup.find_all("span", class_="shortdate")
            if len(class_shortdate) > 0:
                for span in class_shortdate:
                    span.decompose()
            return pd.read_html(str(soup).replace(",", "."), header=None)[0]
        except Exception as e:
            logger.warning(
                f"{self.response.url} | INVALID DATA PERIOD TABLE - LOT {lot_num}"
            )
        return None

    def get_periods(self, lot_num):
        periods = list()
        table = self.get_period_table(lot_num)
        for p in range(len(table)):
            try:
                start = table.iloc[p][1]
                end = table.iloc[p][2]
                price = table.iloc[p][3]
                if isinstance(price, str):
                    price = normalize_string(price)
                    price = round(float(price.replace(" ", "")), 2)
                period = {
                    "start_date_requests": DateTimeHelper.smart_parse(start).astimezone(
                        DateTimeHelper.moscow_tz
                    ),
                    "end_date_requests": DateTimeHelper.smart_parse(end).astimezone(
                        DateTimeHelper.moscow_tz
                    ),
                    "end_date_trading": DateTimeHelper.smart_parse(end).astimezone(
                        DateTimeHelper.moscow_tz
                    ),
                    "current_price": price,
                }
                periods.append(period)
            except Exception as e:
                logger.warning(f"{self.response.url}", exc_info=True)
                continue
        return periods

    def get_start_date_requests(self, lot_num):
        try:
            table = self.get_period_table(lot_num)
            return DateTimeHelper.smart_parse(table.iloc[0][1]).astimezone(
                DateTimeHelper.moscow_tz
            )
        except Exception as e:
            logger.warning(
                f"{self.response.url} | INVALID DATA START DATE REQUEST LOT {lot_num}"
            )
        return None

    def get_end_date_requests(self, lot_num):
        try:
            table = self.get_period_table(lot_num)
            return DateTimeHelper.smart_parse(table.iloc[-1][2]).astimezone(
                DateTimeHelper.moscow_tz
            )
        except Exception as e:
            logger.warning(
                f"{self.response.url} | INVALID DATA END DATE REQUEST LOT {lot_num}"
            )
        return None

    def download(self):
        files = list()
        for file in self.response.xpath(TradeLocator.general_files_loc).getall():
            link = BS(str(file), features="lxml").find("a").get("href")
            name = BS(str(file), features="lxml").find("a").get_text()
            parse_link = URL.parse_url(URL.url_join(data_origin_url, link))
            if any(
                [
                    (len(name) < 3),
                    (len(name) == 0),
                    not name,
                    name == "None",
                    "%20" in name,
                    "%25" in name,
                ]
            ):
                try:
                    _div = BS(str(file), features="lxml").find("a").find("div")
                    url_text = (
                        "".join(re.findall(r"url.\W(download/\d+.+)\?", str(_div)))
                        .replace("(", "")
                        .replace(")", "")
                        .replace(" ", "_")
                    )
                    name = dedent_func(pathlib.Path(str(url_text)).name)
                except Exception as e:
                    logger.warning(f"{e}")
                    extra_name = "".join(dedent_func(pathlib.Path(str(link)).name))[0:6]
                    name = extra_name + dedent_func(pathlib.Path(str(link)).suffix)
            else:
                name = re.sub(r". $", "_.", name)
            files.append(
                DownloadData(url=parse_link, file_name=name, referer=self.response.url)
            )

        gallery = self.soup.find("div", class_="gallery-container")
        if not gallery:
            return files
        for i, image in enumerate(gallery.find_all('img')):
            link = image.get('src')
            name = link.split('/')[-1]
            if 'static-maps.yandex.ru' in name:
                name = f'map_{i}.png'
            files.append(
                DownloadData(url=URL.url_join(data_origin_url, link), file_name=name, referer=self.response.url, is_image=True, order=i)
            )
        return files
