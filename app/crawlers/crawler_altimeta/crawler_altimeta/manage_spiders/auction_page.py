from app.utils import DateTimeHelper, get_lot_number, dedent_func, make_float, logger
from ..locators.locator_lot_page import LocatorLotPage
from ..locators.locators_trade_page import LocatorTradePage
from bs4 import BeautifulSoup as BS
import re


class AucPage:
    def __init__(self, response):
        self.response = response
        self.soup = BS(
            str(self.response.text).replace("&lt;", "<").replace("&gt;", ">"),
            features="lxml",
        )

    @property
    def start_date_requests(self):
        date = self.response.xpath(LocatorTradePage.start_date_request_loc).get()
        date = BS(str(date), features="lxml").get_text(strip=True)
        return DateTimeHelper.smart_parse(date).astimezone(DateTimeHelper.moscow_tz)

    @property
    def end_date_requests(self):
        date = self.response.xpath(LocatorTradePage.end_date_request_loc).get()
        date = BS(str(date), features="lxml").get_text(strip=True)
        return DateTimeHelper.smart_parse(date).astimezone(DateTimeHelper.moscow_tz)

    @property
    def start_date_trading(self):
        date = self.response.xpath(LocatorTradePage.start_date_trading_loc).get()
        if date is None:
            date = self.response.xpath(LocatorTradePage.end_date_trading_loc).get()
            date = BS(str(date), features="lxml").get_text(strip=True)
        date = BS(str(date), features="lxml").get_text(strip=True)
        return DateTimeHelper.smart_parse(date).astimezone(DateTimeHelper.moscow_tz)

    @property
    def end_date_trading(self):
        date = self.response.xpath(LocatorTradePage.end_date_trading_loc).get()
        date = BS(str(date), features="lxml").get_text(strip=True)
        return DateTimeHelper.smart_parse(date).astimezone(DateTimeHelper.moscow_tz)

    def get_all_lot_tables(self):
        tables_all = self.response.xpath(LocatorLotPage.get_all_table).getall()
        return tables_all

    def get_status(self, table_):
        table = BS(str(table_), features="lxml")
        status = table.find("tbody").find("td", string=re.compile("татус торгов"))
        if status is not None:
            status = dedent_func(
                status.findNext("td").get_text(strip=True).strip().lower()
            )
            active = (
                "идет прием заявок",
                "идет приём заявок",
                "идёт приём заявок",
                "идёт приём заявок (приостановлены)",
            )
            pending = ("объявлены", "объявлены (приостановлены)")
            ended = (
                "прием заявок завершен",
                "приём заявок завершен (приостановлены)",
                "в стадии проведения",
                "подводятся итоги",
                "подводятся итоги (приостановлены)",
                "торги отменены (приостановлены)",
                "торги завершены",
                "торги отменены",
                "приём заявок завершен",
                "торги завершены (приостановлены)",
            )
            if status in active:
                return "active"
            elif status in pending:
                return "pending"
            elif status in ended:
                return "ended"
            else:
                logger.warning(
                    f"{str(self.response.text)[:200]} :: !!!! ERROR !!!! STATUS !!!! ERROR WITH TEXT "
                    f"{self.response.url}"
                )
        else:
            logger.warning(
                f"{str(self.response.text)[:200]} :: !!!! ERROR !!!! STATUS !!!! {self.response.url}"
            )
        return None

    def get_th_of_table(self, table_):
        table = BS(str(table_), features="lxml")
        th = table.find("th").get_text(strip=True)
        try:
            return th
        except Exception as e:
            logger.warning(f"{self.response.url} :: ERROR LOT TITLE {e}", exc_info=True)
        return None

    @get_lot_number
    def get_lot_number(self, table_):
        return self.get_th_of_table(table_)

    def get_short_name(self, table_):
        table = BS(str(table_), features="lxml")
        short_name = table.find("tbody").find("td", string=re.compile("редмет торгов"))
        if short_name:
            return (
                short_name.findNext("td").get_text(strip=True).strip().replace("'", '"')
            )
        short_name = re.split(r":", self.get_th_of_table(table_), maxsplit=1)
        if len(short_name) == 2:
            return dedent_func(short_name[1].strip())
        return None

    @staticmethod
    def get_lot_info(table_):
        table = BS(str(table_), features="lxml")
        if lot_info := (
            table.find("tbody").find(
                "td",
                string=re.compile(r"ведения об имуществе \(предприятии\) должника"),
            )
        ):
            return (
                lot_info.findNext("td").get_text(strip=True).strip().replace("'", '"')
            )
        return None

    @staticmethod
    def get_property_info(table_):
        table = BS(str(table_), features="lxml")
        if property_info := (
            table.find("tbody").find(
                "td",
                string=re.compile(r"орядок ознакомления с имуществом \(предприятием\)"),
            )
        ):
            return (
                property_info.findNext("td")
                .get_text(strip=True)
                .strip()
                .replace("'", '"')
            )
        return None

    def get_start_price(self, table_):
        table = BS(str(table_), features="lxml")
        if start_price := table.find("tbody").find(
            "td", string=re.compile("ачальная цена продажи имущес")
        ):
            start_price = (
                start_price.findNext("td")
                .get_text(strip=True)
                .strip()
                .replace("'", '"')
            )
            if len(start_price) < 60 and re.match(r"^\d+", start_price):
                start_price = start_price
            else:
                start_price = self.response.xpath(
                    '//td[contains(., "руб, НДС не облагается")]'
                ).get()
                start_price = BS(str(start_price), features="lxml").get_text(strip=True)
            try:
                return make_float(start_price)
            except ValueError as e:
                logger.warning(
                    f"{self.response.url} ::: ERROR {e} ::: START PRICE", exc_info=True
                )
        return None

    def get_step_price(self, table_):
        table = BS(str(table_), features="lxml")
        if step_price := table.find("tbody").find(
            "td", string=re.compile("еличина повышения начальной це")
        ):
            step_price = step_price.findNext("td").get_text(strip=True).strip()
            step = re.split(r"\(", step_price, maxsplit=1)[0].replace(",", ".")
            step = "".join(re.findall(r"(^\d+)\.?", step))
            try:
                step = (
                    float(self.get_start_price(table_)) * float(step) / 100
                    if self.get_start_price(table_)
                    else None
                )
                return round(step, 2)
            except ValueError as e:
                logger.warning(
                    f"{self.response.url} ::: ERROR {e} ::: STEP PRICE", exc_info=True
                )
        return None

    def get_categories(self, table):
        table = BS(str(table), features="lxml")
        categories = table.find("tbody").find(
            "td", string=re.compile("Классификатор имущества")
        )
        if categories:
            return categories.findNext("td").get_text(strip=True).strip()
        return None
