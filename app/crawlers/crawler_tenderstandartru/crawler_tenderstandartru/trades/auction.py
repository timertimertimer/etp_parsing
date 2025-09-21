from app.utils import delete_extra_symbols, cut_lot_number, contains
from .libraries import *


class AuctionParse:
    addresses = dict()

    def __init__(self, response_):
        self.response = response_
        self.soup = soup(self.response)

    @property
    def trading_org(self):
        label = self.soup.find(
            "label", string=re.compile(r"Организатор торгов", re.IGNORECASE)
        )
        if label:
            div_inn = label.findNext("div", class_="auction_table").find(
                "div", string=re.compile(r"Сокращенное наименование:", re.IGNORECASE)
            )
            if div_inn:
                div_inn = div_inn.findNextSibling("div")
                return div_inn.get_text()
        return None

    @property
    def trading_org_inn(self):
        label = self.soup.find(
            "label", string=re.compile(r"Организатор торгов", re.IGNORECASE)
        )
        if label:
            div_inn = label.findNext("div", class_="auction_table").find(
                "div", string=re.compile(r"ИНН:", re.IGNORECASE)
            )
            if div_inn:
                div_inn = div_inn.findNextSibling("div")
                inn = div_inn.get_text()
                return Contacts.check_inn(inn)
        return None

    @property
    def email(self):
        label = self.soup.find(
            "label",
            string=re.compile(r"Контактное лицо организатора торгов", re.IGNORECASE),
        )
        if label:
            div_email = label.findNext("div", class_="auction_table").find(
                "div", string=re.compile(r"E-mail:", re.IGNORECASE)
            )
            if div_email:
                div_email = div_email.findNextSibling("div")
                email = div_email.get_text()
                return Contacts.check_email(email)
        return None

    @property
    def phone(self):
        label = self.soup.find(
            "label",
            string=re.compile(r"Контактное лицо организатора торгов", re.IGNORECASE),
        )
        if label:
            div_phone = label.findNext("div", class_="auction_table").find(
                "div", string=re.compile(r"Телефон:", re.IGNORECASE)
            )
            if div_phone:
                div_phone = div_phone.findNextSibling("div")
                phone = div_phone.get_text()
                return Contacts.check_phone(phone)
        return None

    @property
    def trading_org_contacts(self):
        return {"email": self.email, "phone": self.phone}

    @property
    def case_number(self):
        label = self.soup.find(
            "label", string=re.compile(r"Сведения о банкротстве", re.IGNORECASE)
        )
        if label:
            div_bankrot_info = label.findNext("div", class_="auction_table").find(
                "div", string=re.compile(r"Номер дела о банкротстве:", re.IGNORECASE)
            )
            if div_bankrot_info:
                div_bankrot_info = div_bankrot_info.findNextSibling("div")
                case_number = div_bankrot_info.get_text()
                return Contacts.check_case_number(case_number)
        return None

    @property
    def arbit_manager(self):
        label = self.soup.find(
            "label", string=re.compile(r"Арбитражный управляющий", re.IGNORECASE)
        )
        if label:
            div_arbitr_name = label.findNext("div", class_="auction_table").find(
                "div", string=re.compile(r"ФИО:", re.IGNORECASE)
            )
            if div_arbitr_name:
                div_arbitr_name = div_arbitr_name.findNextSibling("div")
                arbitr_name = div_arbitr_name.get_text()
                return dedent_func(arbitr_name)
        return None

    @property
    def arbit_manager_org(self):
        label = self.soup.find(
            "label", string=re.compile(r"Арбитражный управляющий", re.IGNORECASE)
        )
        if label:
            div_arbitr_company = label.findNext("div", class_="auction_table").find(
                "div",
                string=re.compile(
                    r"Наименование организации арбитражных управляющих:", re.IGNORECASE
                ),
            )
            if div_arbitr_company:
                div_arbitr_company = div_arbitr_company.findNextSibling("div")
                arbitr_company = div_arbitr_company.get_text()
                return dedent_func(arbitr_company)
            return None
        return None

    @property
    def debtor_inn(self):
        label = self.soup.find(
            "label", string=re.compile(r"Сведения о должнике", re.IGNORECASE)
        )
        if label:
            div_inn = label.findNext("div", class_="auction_table").find(
                "div", string=re.compile(r"ИНН:", re.IGNORECASE)
            )
            if div_inn:
                div_inn = div_inn.findNextSibling("div")
                inn = div_inn.get_text()
                return Contacts.check_inn(inn)
            return None
        return None

    @property
    def address(self):
        label = self.soup.find(
            "label", string=re.compile(r"Сведения о банкротстве", re.IGNORECASE)
        )
        if label:
            div_bankrot_info = label.findNext("div", class_="auction_table").find(
                "div",
                string=re.compile(r"Наименование арбитражного суда:", re.IGNORECASE),
            )
            if div_bankrot_info:
                div_bankrot_info = div_bankrot_info.findNextSibling("div")
                return div_bankrot_info.get_text().strip()
            return None
        return None

    @property
    def property_information(self):
        _div = self.soup.find(
            "div",
            string=re.compile(r"Порядок ознакомления с имуществом:", re.IGNORECASE),
        )
        if _div:
            prop_info = _div.findNext("div").get_text().strip().lower()
            return dedent_func(prop_info)

        logger.warning(
            f"{self.response.url} | ERROR function self.property_information"
        )
        return None

    # LOT PAGE
    def get_trading_form(self, trading_form_text):
        _open = "открытая"
        _closed = "закрытая"
        if trading_form_text in _open:
            return "open"
        elif trading_form_text in _closed:
            return "closed"
        else:
            logger.warning(
                f"{self.response.url} | ERROR function {self.get_trading_form.__name__}"
            )
            return None

    @property
    def trading_form(self):
        _div = self.soup.find(
            "div",
            string=re.compile(r"Форма торга по составу участника:", re.IGNORECASE),
        )
        if _div:
            form_ = _div.findNext("div").get_text().strip().lower()
            return self.get_trading_form(form_)
        logger.warning(f"{self.response.url} | ERROR function self.trading_form")
        return None

    @property
    @delete_extra_symbols
    @cut_lot_number
    def short_name(self):
        previous_div = self.soup.find(
            "div", string=re.compile(r"Номер №\s?\d+", re.IGNORECASE)
        )
        if previous_div:
            _div = previous_div.findNext(
                "div", string=re.compile(r"Наименование:", re.IGNORECASE)
            )
            if _div:
                short_name = _div.findNext("div").get_text().strip().lower()
                return dedent_func(short_name)
        logger.warning(f"{self.response.url} | ERROR function self.short_name")
        return None

    @property
    def lot_info(self):
        _div = self.soup.find(
            "div",
            string=re.compile(
                r"Сведения об имуществе, его составе, характеристиках, описание, порядок ознакомления:",
                re.IGNORECASE,
            ),
        )
        if _div:
            lot_info = _div.findNext("div").get_text().strip().lower()
            return dedent_func(lot_info)
        logger.warning(f"{self.response.url} | ERROR function self.lot_info")
        return None

    @property
    def start_date_requests(self):
        _div = self.soup.find(
            "div",
            string=re.compile(
                r"Дата начала представления заявок на участие:", re.IGNORECASE
            ),
        )
        if _div:
            data_requests = _div.findNext("div").get_text().strip().lower()
            return DateTimeHelper.smart_parse(data_requests).astimezone(
                DateTimeHelper.moscow_tz
            )
        logger.warning(f"{self.response.url} | ERROR function self.start_date_requests")
        return None

    @property
    def end_date_requests(self):
        _div = self.response.xpath(
            '//div[contains(text(), "Дата окончания")]/following-sibling::div[1]/text()'
        ).get()
        if _div:
            end_date_req = _div.strip().lower()
            return DateTimeHelper.smart_parse(end_date_req).astimezone(
                DateTimeHelper.moscow_tz
            )
        logger.warning(f"{self.response.url} | ERROR function end_date_requests")
        return None

    @property
    def start_date_trading(self):
        _div = self.soup.find(
            "div", string=re.compile(r"Дата проведения", re.IGNORECASE)
        ) or self.soup.find(
            "div", string=re.compile(r"Подведение результатов торгов:", re.IGNORECASE)
        )
        if _div:
            end_date_req = _div.findNext("div").get_text().strip().lower()
            return DateTimeHelper.smart_parse(end_date_req).astimezone(
                DateTimeHelper.moscow_tz
            )
        logger.warning(f"{self.response.url} | ERROR function self.start_date_trading")
        return None

    @property
    def start_price(self):
        start_price = self.soup.find(
            "div", string=re.compile(r"^Начальная цена", re.IGNORECASE)
        )
        if start_price:
            start_price = start_price.findNext("div").get_text().strip()
            if start_price:
                return make_float(start_price)
            return None
        return None

    @property
    def msg_number(self):
        _div = self.soup.find(
            "div", string=re.compile(r"Номер сообщения в ЕФРСБ:", re.IGNORECASE)
        )
        if _div:
            msg = _div.findNext("div").get_text().strip().lower()
            return " ".join(re.findall(r"\d{7,8}", msg))
        logger.warning(f"{self.response.url} | ERROR function self.msg_number")
        return None

    def get_step_price(self, start_price):
        try:
            _div = self.soup.find(
                "div", string=re.compile(r"Шаг, руб.:", re.IGNORECASE)
            )
            if _div:
                step_price = _div.findNext("div").get_text().strip()
                return make_float(step_price)
            elif _div is None:
                _div = self.soup.find(
                    "div",
                    string=re.compile(r"Шаг, % от начальной цены:", re.IGNORECASE),
                )
                if _div:
                    step_price = _div.findNext("div").get_text().strip()

                    return make_float(start_price * int(step_price) / 100)
            logger.debug(
                f"{self.response.url} | DEBUG function {self.get_step_price.__name__}"
            )
        except Exception as e:
            logger.warning(
                f"{self.response.url} | ERROR function {self.get_step_price.__name__} - {e}"
            )
        return None
