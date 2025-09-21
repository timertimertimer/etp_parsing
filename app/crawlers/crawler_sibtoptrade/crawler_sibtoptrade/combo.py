import re

from bs4 import BeautifulSoup as BS

from app.db.models import DownloadData
from app.utils import dedent_func, Contacts, make_float, logger, DateTimeHelper
from .locator import Locator


def replaceMultiple(mainString, toBeReplaces, newString):
    # Iterate over the sings to be replaced
    for elem in toBeReplaces:
        # Check if string is in the main string
        if elem in mainString:
            # Replace the string
            mainString = mainString.replace(elem, newString)

    return mainString


pattern_replace = [
    "(",
    ")",
    "-",
    "+",
    "- ",
    " ",
]
pattern_replace1 = ["(", ")", "+", "- ", "null", "\n", "&nbsp;"]


class Combo:
    def __init__(self, response):
        self.response = response

    def check_name(self, string_: str):
        try:
            if string_ is not None and 3 < len(string_) < 256:
                return string_.strip()
            else:
                return None
        except Exception as e:
            logger.warning(e)

    def download_general(self):
        files = list()
        soup = BS(self.response.text, "lxml")
        for a in soup.select(".doclist a"):
            link_etp = "".join(a.get("href"))
            name = "".join(a.get_text()).strip()
            files.append(DownloadData(url=link_etp, file_name=name))
        return files

    def download_lot(self):
        return []

    @property
    def trading_id(self):
        return "".join(re.findall(r"\d+", str(self.trading_link)))

    @property
    def trading_link(self):
        return self.response.url

    @property
    def trading_type(self):
        string_ = self.response.xpath(
            '//td[contains(.,"Вид торгов")]/following::td[1]/text()'
        ).getall()
        string_ = ("".join(string_)).strip()
        if "аукцион" in string_.lower():
            return "auction"
        elif "предложение" in string_.lower():
            return "offer"
        elif "конкурс" in string_.lower():
            return "competition"
        return None

    @property
    def trading_form(self):
        string_ = self.response.xpath(Locator.trade_form_loc).get()
        open_form = [
            "Открытый аукцион",
            "Конкурс",
            "Публичное предложение",
            "Открытая форма предложения о цене",
        ]
        close_form = [
            "Закрытый аукцион",
            "Закрытая форма предложения о цене",
            "Закрытый конкурс",
        ]
        string_ = ("".join(string_)).strip()
        if string_ in open_form:
            return "open"
        elif string_ in close_form:
            return "close"
        return None

    @property
    def trading_org(self):
        return self.check_name(self.response.xpath(Locator.org_name_loc).get())

    @property
    def trading_org_inn(self):
        return Contacts.check_inn(self.response.xpath(Locator.inn_org).get())

    @property
    def trading_org_contacts(self):
        return {
            "email": Contacts.check_email(
                "".join(self.response.xpath(Locator.email_org_loc).get())
            ),
            "phone": Contacts.check_phone(
                "".join(self.response.xpath(Locator.phone_org_loc).get())
            ),
        }

    @property
    def msg_number(self):
        return Contacts.check_msg_number(self.response.xpath(Locator.msg_num_loc).get())

    @property
    def case_number(self):
        return Contacts.check_case_number(
            self.response.xpath(Locator.case_num_loc).get()
        )

    @property
    def debtor_inn(self):
        return Contacts.check_inn(self.response.xpath(Locator.debitor_inn).get())

    @property
    def address(self):
        try:
            address = (
                self.response.xpath(Locator.debitor_address).get()
                or self.response.xpath(Locator.seller_address).get()
            )
            if address:
                return BS(str(address), features="lxml").get_text(strip=True)
        except Exception as e:
            logger.error(f"{self.response.url} | ERROR ADDRESS DEBTOR\n{e}")
        return None

    @property
    def arbit_manager(self):
        return self.check_name(self.response.xpath(Locator.arbitr_name_loc).get())

    @property
    def arbit_manager_inn(self):
        return Contacts.check_inn(self.response.xpath(Locator.arbitr_inn_loc).get())

    @property
    def arbit_manager_org(self):
        return dedent_func(
            self.check_name(self.response.xpath(Locator.arbitr_org_loc).get())
        )

    @property
    def lot_number(self):
        return self.response.xpath(Locator.lot_number_loc).get()

    @property
    def short_name(self):
        return dedent_func(self.response.xpath(Locator.short_name).get())

    @property
    def property_information(self):
        return dedent_func(self.response.xpath(Locator.property_information_loc).get())

    @property
    def start_date_requests(self):
        date = self.response.xpath(Locator.start_date_request_loc).get()
        if not date:
            return None
        return DateTimeHelper.smart_parse(date).astimezone(DateTimeHelper.moscow_tz)

    @property
    def end_date_requests(self):
        date = self.response.xpath(Locator.end_date_request_loc).get()
        if not date:
            return None
        return DateTimeHelper.smart_parse(date).astimezone(DateTimeHelper.moscow_tz)

    @property
    def start_date_trading(self):
        date = self.response.xpath(Locator.start_trading_loc).get()
        if not date:
            return None
        return DateTimeHelper.smart_parse(date).astimezone(DateTimeHelper.moscow_tz)

    @property
    def end_date_trading(self):
        date = self.response.xpath(Locator.end_trading_loc).get()
        if not date:
            return None
        return DateTimeHelper.smart_parse(date).astimezone(DateTimeHelper.moscow_tz)

    @property
    def start_price(self):
        start_price = self.response.xpath(Locator.start_price_loc).get()
        if "Начальная цена" in start_price:
            start_price = self.response.xpath(Locator.start_price_loc).extract()
            start_price = start_price[1]
        if "Информация о снижении цены" in start_price:
            start_price = self.response.xpath(Locator.start_price_loc).extract()
            if len(start_price) == 2:
                start_price = start_price[1]
            if len(start_price) == 3:
                start_price = start_price[2]
        if start_price:
            return make_float(start_price)
        return None

    @property
    def step_price(self):
        step_price = self.response.xpath(Locator.step_price_loc).get()
        if "Начальная цена" in step_price:
            step_price = self.response.xpath(Locator.step_if_bug).extract()
            step_price = step_price[0]
        if step_price and (
            self.trading_type == "auction" or self.trading_type == "competition"
        ):
            try:
                return make_float("".join(step_price))
            except Exception as e:
                logger.error(f"{self.response.url}:: STEP PRICE is INVALID")
        return None

    @property
    def periods(self):
        table_periods = self.response.xpath(Locator.table_period_1)
        if not table_periods:
            return None
        full_period = []
        for tr in table_periods:
            try:
                start = tr.xpath("td[1]//text()").get()
                end = tr.xpath("td[2]//text()").get()
                price = tr.xpath("td[3]//text()").get()
                start_date_requests = replaceMultiple(
                    start.strip(), pattern_replace1, " "
                )
                end_date_requests = replaceMultiple(end.strip(), pattern_replace1, " ")
                period = {
                    "start_date_requests": DateTimeHelper.smart_parse(
                        start_date_requests
                    ).astimezone(DateTimeHelper.moscow_tz),
                    "end_date_requests": DateTimeHelper.smart_parse(
                        end_date_requests
                    ).astimezone(DateTimeHelper.moscow_tz),
                    "end_date_trading": DateTimeHelper.smart_parse(
                        end_date_requests
                    ).astimezone(DateTimeHelper.moscow_tz),
                    "current_price": make_float(price),
                }
            except:
                continue
            full_period.append(period)
        return full_period
