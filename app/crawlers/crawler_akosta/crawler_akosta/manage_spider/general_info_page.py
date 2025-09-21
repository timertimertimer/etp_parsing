import re
import pathlib
from datetime import datetime

from app.utils.config import allowable_formats, image_formats
from app.db.models import DownloadData
from ..locators.trading_page_locator import GeneralInfoLocator
from ..utils.config import data_origin, debtor_link, lot_link, host
from ..utils.post_data import post_data_download
from app.utils import (
    dedent_func,
    replace_multiple,
    pattern_replace1,
    URL,
    logger, DateTimeHelper,
)
from bs4 import BeautifulSoup as BS


class MainTradingPage:
    def __init__(self, response, soup):
        self.response = response
        self.soup = soup
        self.main_url = re.sub(r"/$", "", data_origin)

    def get_link_redirect(self):
        try:
            url = self.soup.find("partial-response").find("redirect").get("url")
        except Exception:
            return None
        if url:
            return URL.url_join(self.main_url, url)
        else:
            logger.error(f"{self.response.url} :: NO VALUE LINK")
            with open("redirect_page.txt", "w") as f:
                f.write(self.response.text)
        return None

    def get_debtor_info_link(self, url):
        return debtor_link + f"?{URL.return_only_param(url)}"

    def get_lot_tab_link(self, url):
        return lot_link + f"?{URL.return_only_param(url)}"

    def get_trading_number(self):
        return self.response.xpath(GeneralInfoLocator.trading_number_loc).get()

    @property
    def get_string_trading_type(self):
        label_type_trade = self.response.xpath(
            GeneralInfoLocator.trading_type_loc
        ).get()
        text = BS(str(label_type_trade), features="lxml")
        text = dedent_func(text.get_text().split(".")[-1].strip())
        return text

    def get_trading_type(self):
        _type = self.get_string_trading_type
        offer_type = ("Продажа посредством публичного предложения",)
        auction_type = (
            "Открытый аукцион с открытой формой подачи предложений",
            "Открытый аукцион с закрытой формой подачи предложений",
        )
        competition_type = (
            "Открытый конкурс с открытой формой подачи предложений",
            "Открытый конкурс с закрытой формой подачи предложений",
        )
        if _type in offer_type:
            return "offer"
        elif _type in auction_type:
            return "auction"
        elif _type in competition_type:
            return "competition"
        logger.error(f"{self.response.url} :: INVALID DATA TRADING TYPE")
        return None

    @property
    def get_string_organizer_div(self):
        return self.response.xpath(GeneralInfoLocator.organizer_div_loc).get()

    def get_organizer(self):
        _div = self.get_string_organizer_div
        try:
            organizer = BS(str(_div), features="lxml").find("a").get_text()
            return dedent_func(organizer)
        except Exception:
            logger.error(f"{self.response.url} :: ERROR WHILE GETTING ORGANIZER NAME")
        return None

    def get_organizer_contacts(self) -> dict:
        """:return trading_org"""
        _div = self.get_string_organizer_div
        contacts = {"email": "", "phone": ""}
        email = ""
        phone = ""
        paragraf_tag = BS(_div, "lxml").find_all("p")
        if _div:
            for i in paragraf_tag:
                if "@" in i.get_text():
                    email = dedent_func(i.get_text().strip())
                text = replace_multiple(i.get_text(), pattern_replace1, "")
                no_space = re.sub(r"\s", "", text)
                match = re.search(r"\d{6,}", no_space)
                if match:
                    phone = "".join(
                        [
                            x
                            for x in i.get_text()
                            if x.isdigit() or x == "-" or x == "(" or x == ")"
                        ]
                    )
            contacts["email"] = email
            contacts["phone"] = phone
            return contacts
        logger.error(
            f"{self.response.url} :: ERROR WHILE GETTING ORGANIZER NAME",
            exc_info=True,
        )
        return contacts

    def get_trading_form(self):
        _form = self.get_string_trading_type
        _open = (
            "Продажа посредством публичного предложения",
            "Открытый аукцион с открытой формой подачи предложений",
            "Открытый аукцион с закрытой формой подачи предложений",
            "Открытый конкурс с открытой формой подачи предложений",
            "Открытый конкурс с закрытой формой подачи предложений",
        )
        if _form in _open:
            return "open"
        logger.error(f"{self.response.url} :: INVALID DATA STATUS")
        return None

    def get_status(self):
        try:
            active = (
                "Идет приём заявок",
                "Идет прием заявок",
            )
            pending = ("Торги объявлены",)
            ended = (
                "Заявки рассмотрены",
                "Идёт аукцион",
                "Подведение итогов",
                "Приём заявок завершен",
                "Рассмотрение заявок",
                "Торги аннулированы",
                "Торги не состоялись",
                "Торги отменены",
                "Торги приостановлены",
                "Торги проведены",
            )
            _status = self.response.xpath(GeneralInfoLocator.status_loc).get()
            if not _status:
                return None
            status = dedent_func(_status.strip())
            if not status or len(status) == 0:
                return None
            if status in active:
                return "active"
            elif status in pending:
                return "pending"
            elif status in ended:
                return "ended"
            logger.warning(f"{self.response.url} :: INVALID STATUS")
        except Exception as e:
            logger.warning(
                f"{self.response.url} :: INVALID DATA STATUS {e}", exc_info=True
            )
        return None

    def get_period_requests_auction(self):
        period_requests_auction = self.response.xpath(
            GeneralInfoLocator.date_request_period_auction
        ).get()
        period_requests_auction = BS(
            str(period_requests_auction), features="lxml"
        ).get_text()
        period_requests_auction = dedent_func(period_requests_auction.strip())
        pattern = re.compile(r"\d{1,2}.\d{1,2}.\d{2,4}\s\d{1,2}:\d{1,2}")
        periods = pattern.findall(period_requests_auction)
        check_if_second_eq_2 = DateTimeHelper.compare(
            periods[0], periods[1], self.response.url
        )
        if check_if_second_eq_2 == 2:
            return periods
        logger.error(
            f"{self.response.url} :: INVALID DATA GETTING LIST PERIODS START DATE REQUESTS AUCTION/COMPETITION"
        )
        return None

    @property
    def start_date_requests(self):
        if self.get_period_requests_auction():
            return DateTimeHelper.smart_parse(self.get_period_requests_auction()[0]).astimezone(DateTimeHelper.moscow_tz)
        logger.error(f"{self.response.url} :: INVALID START DATE REQUEST AUCTION")
        return None

    @property
    def end_date_requests(self):
        if self.get_period_requests_auction():
            return DateTimeHelper.smart_parse(self.get_period_requests_auction()[1]).astimezone(DateTimeHelper.moscow_tz)
        logger.error(f"{self.response.url} :: INVALID END DATE REQUEST AUCTION")
        return None


    @property
    def start_date_trading(self):
        _div = self.response.xpath(GeneralInfoLocator.start_date_trading_auc_loc).get()
        if not _div:
            return None
        _date = BS(str(_div), features="lxml").get_text()
        _date = dedent_func(_date.strip())
        pattern = re.compile(r"\d{1,2}.\d{1,2}.\d{2,4}\s\d{1,2}:\d{1,2}")
        _date = pattern.findall(_date)
        if len(_date) == 1:
            return DateTimeHelper.smart_parse(_date[0]).astimezone(DateTimeHelper.moscow_tz)
        return None

    @property
    def end_date_trading(self):
        _div = self.response.xpath(GeneralInfoLocator.end_date_trading_auc_loc).get()
        if not _div:
            return None
        _date = BS(str(_div), features="lxml").get_text()
        _date = dedent_func(_date.strip())
        pattern = re.compile(r"\d{1,2}.\d{1,2}.\d{2,4}\s\d{1,2}:\d{1,2}")
        _date = pattern.findall(_date)
        if len(_date) == 1:
            return DateTimeHelper.smart_parse(_date[0]).astimezone(DateTimeHelper.moscow_tz)
        return None

    def get_documents_table(self):
        try:
            lst_data = list()
            doc_table = self.soup.find("table", id="formMain:auctionDocs")
            if not doc_table:
                return None
            for tr in doc_table.find_all("tr"):
                _a = tr.find(
                    "a", id=re.compile(r"formMain:auctionDocs:\d+:typeDocName")
                ).get("id")
                _text = (
                    tr.find("td")
                    .find("span", class_="form-docum-note")
                    .get_text()
                    .replace("(", "")
                    .replace(",", "")
                    .strip()
                )
                lst_data.append((_a, _text))
            return lst_data
        except Exception as e:
            logger.error(f"{self.response.url} :: ERROR GETTING DOCUMENTS {e}")
            return list()

    def find_correct_form_number_1(self):
        lst = ["formMain:j_idt93_collapsed", "formMain:j_idt82_collapsed"]
        divs = self.soup.find_all("input", id=re.compile("formMain:j_idt\d+_collapsed"))
        for div in divs:
            div = div.get("id")
            if div in lst:
                return div
        return None

    def return_post_data(self, view_state, a_id) -> dict:
        _post = post_data_download.copy()
        _post["formMain:inputServerTime"] = DateTimeHelper.format_datetime(datetime.now(), "%H:%M:%S")
        _post["javax.faces.ViewState"] = view_state
        data_ = self.find_correct_form_number_1()
        _post[data_] = "false"
        _post[a_id] = a_id
        return _post

    def download_trade(self, url: str, cookies: str, view: str):
        files = list()
        for t in self.get_documents_table():
            form_data, name = t
            path = pathlib.PurePath(name)
            if path.suffix.lower() in allowable_formats:
                files.append(
                    DownloadData(
                        url=url,
                        file_name=name,
                        referer=self.response.url,
                        host=host,
                        cookies=cookies,
                        method="POST",
                        data=self.return_post_data(view_state=view, a_id=form_data),
                        verify=False,
                        is_image=path.suffix.lower() in image_formats
                    )
                )
        return files
