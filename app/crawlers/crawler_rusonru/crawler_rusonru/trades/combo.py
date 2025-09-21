import re

import pandas as pd
from numpy import float64

from app.utils import dedent_func, Contacts, make_float, DateTimeHelper, logger
from .serp import SerpParse
from .files import DocumentGeneral, DocumentLot
from bs4 import BeautifulSoup as BS

from ..locator import Locator


class Combo:
    def __init__(self, response):
        self.response = response
        self.soup = BS(self.response.text, "lxml")
        self.serp = SerpParse(response=self.response)
        self.gen = DocumentGeneral(self.response)
        self.lot = DocumentLot(self.response)

    @property
    def trading_id(self):
        try:
            _id = re.findall(r"\d+$", str(self.response.url))
            return "".join(_id)
        except Exception as ex:
            logger.warning(f"{self.response.url} | INVALID DATA Trading ID {ex}")
        return None

    @property
    def trading_link(self):
        return self.response.url

    @property
    def trading_number(self):
        try:
            _number = self.response.xpath(Locator.trading_number).get()
            return dedent_func(_number)
        except Exception as ex:
            logger.warning(f"{self.response.url} | INVALID DATA Trading Number {ex}")
        return None

    @property
    def trading_type(self):
        try:
            offer = ("публичное предложение", "закрытое публичное предложение")
            auction = (
                "аукцион с открытой формой представления цены",
                "аукцион с закрытой формой представления цены",
                "закрытый аукцион с открытой формой представления цены",
                "закрытый аукцион с закрытой формой представления цены",
            )
            competition = (
                "конкурс с открытой формой представления цены",
                "конкурс с закрытой формой представления цены",
                "закрытый конкурс с открытой формой представления цены",
                "закрытый конкурс с закрытой формой представления цены",
            )
            _type_text = self.response.xpath(Locator.trading_type).get()
            _type_text1 = BS(str(_type_text), features="lxml").get_text().lower()
            text = dedent_func(_type_text1)
            if text in offer:
                return "offer"
            elif text in auction:
                return "auction"
            elif text in competition:
                return "competition"
        except Exception as e:
            logger.warning(f"{self.response.url} | INVALID DATA TRADING TYPE {e}")
        return None

    @property
    def trading_form(self):
        _open = (
            "публичное предложение",
            "аукцион с открытой формой представления цены",
            "аукцион с закрытой формой представления цены",
            "конкурс с открытой формой представления цены",
            "конкурс с закрытой формой представления цены",
        )
        closed = (
            "закрытое публичное предложение",
            "закрытый аукцион с открытой формой представления цены",
            "закрытый аукцион с закрытой формой представления цены",
            "закрытый конкурс с открытой формой представления цены",
            "закрытый конкурс с закрытой формой представления цены",
        )
        _type_text = self.response.xpath(Locator.trading_type).get()
        _type_text1 = BS(str(_type_text), features="lxml").get_text().lower()
        text = dedent_func(_type_text1)
        if text in _open:
            return "open"
        elif text in closed:
            return "closed"
        return None

    def get_block_org(self):
        try:
            org_block = self.response.xpath(Locator.trading_org).get()
            if not org_block:
                org_block = self.response.xpath(Locator.trading_org2).get()
            org_block = BS(str(org_block), features="lxml")
            return org_block
        except Exception as ex:
            logger.warning(f"{self.response.url} | INVALID DATA TRADING ORG {ex}")
        return None

    @property
    def trading_org(self):
        try:
            block = self.get_block_org()
            name = block.find(
                "td", string=re.compile("аименование", re.IGNORECASE)
            ) or block.find("td", string=re.compile("ФИО", re.IGNORECASE))
            if name:
                return dedent_func(name.findNext("td").get_text(strip=True))
        except Exception as ex:
            logger.warning(f"{self.response.url} | INVALID DATA get_org_name {ex}")
        return None

    @property
    def trading_org_inn(self):
        try:
            block = self.get_block_org()
            _inn = block.find("td", string=re.compile("ИНН", re.IGNORECASE))
            if _inn:
                _inn = dedent_func(_inn.findNext("td").get_text().strip())
                return Contacts.check_inn(_inn)
        except Exception as ex:
            logger.warning(f"{self.response.url} | INVALID DATA ORG INN {ex}")
        return None

    @property
    def trading_org_contacts(self):
        email = self.get_email()
        phone = self.get_phone()
        return {"email": email, "phone": phone}

    def get_email(self):
        try:
            block = self.get_block_org()
            email = block.find(
                "td", string=re.compile("E-mail", re.IGNORECASE)
            ).findNext("td")
            if email:
                email = dedent_func(email.get_text().strip())
                return Contacts.check_email(email)
        except Exception as ex:
            logger.warning(f"{self.response.url} | INVALID DATA EMAIL ORG {ex}")
        return None

    def get_phone(self):
        try:
            block = self.get_block_org()
            phone = block.find(
                "td", string=re.compile("Телефон", re.IGNORECASE)
            ).findNext("td")
            if phone:
                phone = dedent_func(phone.get_text().strip())
                return Contacts.check_phone(phone)
        except Exception as ex:
            logger.warning(f"{self.response.url} | INVALID DATA PHONE ORG {ex}")
        return None

    @property
    def msg_number(self):
        block = self.get_block_trade_info()
        block = BS(str(block), features="lxml")
        msg = block.find(
            "td",
            string=re.compile("о проведении торгов на fedresurs.ru", re.IGNORECASE),
        ).findNext("td")
        if msg:
            msg = re.findall(r"\d{6,8}", msg.get_text())
            if len(msg) > 0:
                return " ".join(msg)
        return None

    def get_block_trade_info(self):
        try:
            info_block = self.response.xpath(Locator.trade_info).get()
            info_block = BS(str(info_block), features="lxml")
            return info_block
        except Exception as ex:
            logger.warning(
                f"{self.response.url} | INVALID DATA get_block_trade_info {ex}"
            )
        return None

    @property
    def case_number(self):
        block = self.get_block_debtor_info()
        if block:
            case = block.find(
                "td", string=re.compile("Номер дела о банкротстве", re.IGNORECASE)
            ).findNext("td")
            if case:
                case = dedent_func(case.get_text().strip())
                return Contacts.check_case_number(case)
        return None

    def get_block_debtor_info(self):
        try:
            debtor_block = self.response.xpath(Locator.debtor_info).get()
            debtor_block = BS(str(debtor_block), features="lxml")
            return debtor_block
        except Exception as ex:
            logger.warning(f"{self.response.url} | INVALID DATA DEBTOR INFO {ex}")
        return None

    @property
    def debtor_inn(self):
        try:
            block = self.get_block_debtor_info()
            _inn = block.find("td", string=re.compile("ИНН", re.IGNORECASE)).findNext(
                "td"
            )
            if _inn:
                _inn = dedent_func(_inn.get_text().strip())
                if re.match(r"\d{9,13}", _inn):
                    inn = _inn
                else:
                    inn = self.response.xpath(Locator.extra_loc_debtor).get()
                return Contacts.check_inn(inn)
        except Exception as ex:
            logger.warning(f"{self.response.url} | INVALID DATA DEBTOR INN {ex}")
        return None

    @property
    def address(self):
        try:
            if table := self.get_block_debtor_info():
                address = table.find("td", string="Адрес")
                if address:
                    address = address.findNextSibling("td").get_text(strip=True)
                sud = table.find("td", string="Наименование суда")
                if sud:
                    sud = sud.findNextSibling("td").get_text(strip=True)
                region = table.find("td", string="Регион")
                if region:
                    region = region.findNextSibling("td").get_text(strip=True)
                if not any([address, sud]):
                    return region
                if not address:
                    address = sud
                return address
        except Exception:
            logger.warning(
                f"{self.response.url} | ERROR function {self.address.__name__}"
            )
        return None

    def get_arbitr_block(self):
        """:return block with arbitr info"""
        try:
            block_arbitr = self.response.xpath(Locator.arbitr_info).get()
            arb = BS(str(block_arbitr), features="lxml")
            return arb
        except Exception as ex:
            logger.warning(f"{self.response.url} | {ex}")
        return None

    @property
    def arbit_manager(self):
        try:
            block = self.get_arbitr_block()
            if block:
                last_name = block.find(
                    "td", string=re.compile("Фамилия", re.IGNORECASE)
                )
                if last_name:
                    last_name = dedent_func(last_name.findNext("td").get_text().strip())
                else:
                    last_name = ""
                first_name = block.find("td", string=re.compile("Имя", re.IGNORECASE))
                if first_name:
                    first_name = dedent_func(
                        first_name.findNext("td").get_text().strip()
                    )
                else:
                    first_name = ""
                middle_name = block.find(
                    "td", string=re.compile("Отчество", re.IGNORECASE)
                )
                if middle_name:
                    middle_name = dedent_func(
                        middle_name.findNext("td").get_text().strip()
                    )
                else:
                    middle_name = ""
                return " ".join([last_name, first_name, middle_name])
        except Exception as e:
            logger.warning(f"{self.response.url} | INVALID DATA ARBITR NAME {e}")
        return None

    @property
    def arbit_manager_inn(self):
        try:
            block = self.get_arbitr_block()
            _inn = block.find("td", string=re.compile("ИНН", re.IGNORECASE)).findNext(
                "td"
            )
            if _inn:
                _inn = dedent_func(_inn.get_text().strip())
                return Contacts.check_inn(_inn)
        except Exception as ex:
            logger.warning(f"{self.response.url} | INVALID DATA ARBITR INN {ex}")
        return None

    @property
    def arbit_manager_org(self):
        try:
            block = self.get_arbitr_block()
            company = block.find(
                "td", string=re.compile("аименование СРО", re.IGNORECASE)
            ).findNext("td")
            if company:
                company = dedent_func(company.get_text().strip())
                if "(" in company:
                    company = re.split(r"\(", company, maxsplit=1)[0]
                if "," in company:
                    company = re.split(r",", company, maxsplit=1)[0]
                return company
        except Exception as ex:
            logger.warning(f"{self.response.url} | INVALID DATA ARBITR company {ex}")
        return None

    def date_block_auction(self):
        try:
            block = self.response.xpath(Locator.dates_trading).get()
            date_ = BS(str(block), features="lxml")
            return date_
        except Exception as ex:
            logger.warning(f"{self.response.url} | {ex}")
        return None

    def count_lots(self) -> list:
        lot = self.soup.find_all("table", id=re.compile("table_lot", re.IGNORECASE))
        if len(lot) > 0:
            return lot
        return None

    def get_lot_block(self, table: str):
        try:
            if table and len(table) > 0:
                table_html = BS(str(table), features="lxml")
                return table_html
        except Exception as ex:
            logger.warning(
                f"{self.response.url} | ERROR TABLE LOT INFO {ex}", exc_info=True
            )
        return None

    def get_status(self, table: str):
        active = ("прием заявок", "приём заявок")
        pending = ("торги объявлены", "торги обьявлены")
        ended = (
            "прием заявок завершен",
            "идут торги",
            "подведение итогов",
            "торги завершены",
            "торги не состоялись",
            "торги приостановлены",
            "торги отменены",
            "приём заявок завершен",
        )
        try:
            block = self.get_lot_block(table=table)
            status = (
                block.find("td", string=re.compile("Статус торгов", re.IGNORECASE))
                .findNext("td")
                .get_text()
                .lower()
            )
            status = dedent_func(status.strip())
            if status in active:
                return "active"
            elif status in pending:
                return "pending"
            elif status in ended:
                return "ended"
        except Exception as ex:
            logger.warning(f"{self.response.url} | Invalid data get_lot_status {ex}")
        return None

    def get_lot_number(self, table: str):
        try:
            block = self.get_lot_block(table)
            if block:
                lot_number = (
                    block.find("td", string=re.compile("Номер лота", re.IGNORECASE))
                    .findNext("td")
                    .get_text()
                )
                num = dedent_func(lot_number.strip())
                if re.match(r"^\d+$", num):
                    return num
                else:
                    logger.warning(f"{self.response.url} | INVALID DATA LOT NUMBER")
        except Exception as ex:
            logger.warning(f"{self.response.url} | ERROR LOT NUMBER {ex}")
        return None

    def get_short_name(self, table: str):
        try:
            block = self.get_lot_block(table=table)
            if block:
                short = block.find(
                    "td", string=re.compile("Наименование имущества", re.IGNORECASE)
                )
                if short:
                    short = dedent_func(short.findNext("td").get_text().strip())
                    return short
        except Exception as ex:
            logger.warning(f"{self.response.url} | INVALID DATA SHORT NAME {ex}")
        return None

    def get_lot_info(self, table: str):
        try:
            block = self.get_lot_block(table=table)
            if block:
                lot_info = block.find(
                    "td",
                    string=re.compile(
                        "Cведения об имуществе \(предприятии\) должника", re.IGNORECASE
                    ),
                )
                if lot_info:
                    lot_info = dedent_func(lot_info.findNext("td").get_text().strip())
                    return lot_info
        except Exception as ex:
            logger.warning(f"{self.response.url} | INVALID DATA LOT INFO {ex}")
        return None

    @property
    def property_information(self):
        block = self.get_block_trade_info()
        block = BS(str(block), features="lxml")
        info = block.find(
            "td", string=re.compile("Порядок ознакомления с имуществом", re.IGNORECASE)
        )
        if info:
            return dedent_func(info.findNext("td").get_text(strip=True))
        return None

    @property
    def start_date_requests_auc(self):
        try:
            block = self.date_block_auction()
            if block:
                start = block.find(
                    "td",
                    string=re.compile(
                        "ата начала представления заявок на участи", re.IGNORECASE
                    ),
                ).findNext("td")
                if start:
                    start = DateTimeHelper.smart_parse(
                        dedent_func(start.get_text().strip())
                    ).astimezone(DateTimeHelper.moscow_tz)
                    return start
        except Exception as ex:
            logger.warning(
                f"{self.response.url} | ERROR start date request auction {ex}"
            )
        return None

    @property
    def end_date_requests_auc(self):
        try:
            block = self.date_block_auction()
            if block:
                end = block.find(
                    "td",
                    string=re.compile(
                        "ата окончания представления заявок на", re.IGNORECASE
                    ),
                )
                if end:
                    end = DateTimeHelper.smart_parse(
                        dedent_func(end.findNext("td").get_text().strip())
                    ).astimezone(DateTimeHelper.moscow_tz)
                    return end
        except Exception as ex:
            logger.warning(
                f"{self.response.url} | ERROR start date request auction {ex}"
            )
        return None

    @property
    def start_date_trading_auc(self):
        try:
            block = self.date_block_auction()
            if block:
                start = block.find(
                    "td", string=re.compile("ата проведени", re.IGNORECASE)
                )
                if start:
                    start = DateTimeHelper.smart_parse(
                        dedent_func(start.findNext("td").get_text().strip())
                    ).astimezone(DateTimeHelper.moscow_tz)
                    return start
        except Exception as ex:
            logger.warning(
                f"{self.response.url} | ERROR start date request auction {ex}"
            )
        return None

    def get_period_table(self, table: str):
        try:
            block = self.get_lot_block(table=table)
            if block:
                table_1 = block.find("table", class_="views-table inner discount_int")
                if table_1:
                    table_1 = table_1
                else:
                    table_1 = block.find(
                        "th",
                        string=re.compile("ата начала приема заявок", re.IGNORECASE),
                    )
                    if table_1:
                        table_1 = table_1.find_parent("table")
                if table_1:
                    _table = pd.read_html(str(table_1))
                    df = _table[0]
                    return df
                else:
                    logger.warning(f"{self.response.url} | TABLE PERIODS NOT FOUND")
        except Exception as ex:
            logger.warning(f"{self.response.url} | INVALID DATA PERIODS OFFER {ex}")
        return None

    def get_start_date_requests_offer(self, table: str):
        try:
            table_period = self.get_period_table(table)
            start_date = table_period.iloc[0][0]
            return DateTimeHelper.smart_parse(start_date).astimezone(
                DateTimeHelper.moscow_tz
            )
        except Exception as ex:
            logger.warning(
                f"{self.response.url} | INVALID DATA START DATE TRADING OFFER {ex}"
            )
        return None

    def get_end_date_requests_offer(self, table: str):
        try:
            table_period = self.get_period_table(table)
            end_date = table_period.iloc[-1][1]
            return DateTimeHelper.smart_parse(end_date).astimezone(
                DateTimeHelper.moscow_tz
            )
        except Exception as ex:
            logger.warning(f"{self.response.url} | INVALID DATA END DATE TRADING {ex}")
        return None

    def get_start_date_trading_offer(self, table: str):
        return self.get_start_date_requests_offer(table)

    def get_end_date_trading_offer(self, table: str):
        return self.get_end_date_requests_offer(table)

    def clean_price(self, price):
        pattern = r"^\d+\.\d{1,2}"
        if "руб" in price:
            price = "".join(re.split(r"руб", price, maxsplit=1)[0])
        clean_price = "".join(filter(lambda x: x.isdigit() or x == ",", price)).replace(
            ",", "."
        )
        match = "".join(re.findall(pattern, clean_price))
        if match:
            return round(float(match), 2)
        return None

    def get_start_price_auc(self, table: str):
        try:
            block = self.get_lot_block(table=table)
            if block:
                price = block.find_all(
                    "td", string=re.compile("Начальная цена", re.IGNORECASE)
                )
                if len(price) == 1:
                    price = price[0]
                    price = dedent_func(price.findNext("td").get_text().strip())
                    return make_float(price)
                elif len(price) >= 2:
                    for p in price:
                        if len(p.get_text().strip()) < 15:
                            price = p.findNext("td").get_text()
                            return make_float(price)
                else:
                    logger.warning(f"{self.response.url} | INVALID DATA START PRICE")
        except Exception as ex:
            logger.warning(f"{self.response.url} | ERROR start price auction {ex}")
        return None

    def get_start_price_offer(self, table_):
        try:
            table_period = self.get_period_table(table_)
            current_price = table_period.iloc[0][2]
            if isinstance(current_price, str):
                current_price_ = make_float(current_price)
            elif isinstance(current_price, float64):
                current_price_ = round(float(current_price), 2)
            else:
                logger.warning(f"{self.response.url} | INVALID TYPE CURRENT PRICE")
                current_price_ = None
            return current_price_
        except Exception as ex:
            logger.warning(f"{self.response.url} | INVALID DATA END DATE TRADING {ex}")
        return None

    def get_step_price(self, table: str):
        try:
            # bs4 object
            block = self.get_lot_block(table=table)
            if block:
                step = block.find_all("td", string=re.compile("Шаг", re.IGNORECASE))
                if len(step) == 1:
                    step = step[0]
                    step = dedent_func(step.findNext("td").get_text().strip())
                    return make_float(step)
                elif len(step) >= 2:
                    for p in step:
                        if len(p.get_text().strip()) < 15:
                            price = p.findNext("td").get_text()
                            return make_float(price)
        except Exception as ex:
            logger.warning(f"{self.response.url} | ERROR step price {ex}")
        return None

    def get_periods(self, table):
        check_value = int(10**22)
        periods = list()
        df = self.get_period_table(table)
        try:
            for t in range(len(df)):
                start_date_request = df.iloc[t][0]
                end_date_request = df.iloc[t][1]
                end_date_trading = df.iloc[t][1]
                current_price = df.iloc[t][2]
                if not re.match(r"nan", str(current_price), re.IGNORECASE):
                    if isinstance(current_price, str):
                        current_price_ = make_float(current_price)
                    elif isinstance(current_price, float64):
                        current_price_ = round(float(current_price), 2)
                    else:
                        logger.warning(
                            f"{self.response.url} | INVALID TYPE CURRENT PRICE"
                        )
                        current_price_ = None
                    period = {
                        "start_date_requests": DateTimeHelper.smart_parse(
                            start_date_request
                        ).astimezone(DateTimeHelper.moscow_tz),
                        "end_date_requests": DateTimeHelper.smart_parse(
                            end_date_request
                        ).astimezone(DateTimeHelper.moscow_tz),
                        "end_date_trading": DateTimeHelper.smart_parse(
                            end_date_trading
                        ).astimezone(DateTimeHelper.moscow_tz),
                        "current_price": current_price_,
                    }
                    periods.append(period)
                    if check_value < current_price_:
                        logger.warning(
                            f"{self.response.url} | INVALID PRICE ON PERIOD - CURRENT PRICE HIGHER THAN PREVIUOS",
                            df,
                        )
                    check_value = current_price_
            return periods
        except Exception as e:
            logger.warning(
                f"{self.response.url} | PERIODS ERROR {e}\n{df}", exc_info=True
            )
        return None
