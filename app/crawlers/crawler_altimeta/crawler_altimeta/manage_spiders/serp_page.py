import re
from bs4 import BeautifulSoup as BS

from app.utils import Contacts, DateTimeHelper, dedent_func, logger
from ..locators.locators_serp import LocatorSerp
from ..locators.locators_trade_page import LocatorTradePage


class SerpPage:
    addresses = dict()

    def __init__(self, response_):
        self.response = response_
        self.soup = BS(
            str(self.response.text).replace("&lt;", "<").replace("&gt;", ">"),
            features="lxml",
        )
        self.loc_serp = LocatorSerp
        self.loc_trade = LocatorTradePage

    def retur_page_html(self):
        return self.soup

    def return_current_start_date(self):
        _date = self.response.xpath(self.loc_trade.check_date).get()
        if _date:
            _date = BS(str(_date), features="lxml").get_text().strip()
            if re.match(r"\d{1,2}\.\d{1,2}\.\d{2,4}.*?\d{1,2}\:\d{1,2}", _date):
                return DateTimeHelper.smart_parse(_date).astimezone(DateTimeHelper.moscow_tz)
            else:
                logger.error(
                    f"{self.response.url} :: INVALID DATE !!!!!!!!!!!!@@@@@@@@@@@@@############# THE LOT SHOULD LOST"
                )
        else:
            logger.error(
                f"{self.response.url} :2: INVALID DATE !!!!!!!!!!!!@@@@@@@@@@@@@############# THE LOT SHOULD LOST"
            )
        return None

    def get_one_next_link(self):
        next_page = self.response.xpath(self.loc_serp.links_to_the_next_page).get()
        return next_page

    def get_links_to_trade(self):
        tr_with_links = self.response.xpath(self.loc_serp.links_to_trade_page).getall()
        pattern = re.compile(
            r"window.location.+(\/trade\/view\/purchase\/general\.html\?id=\d+).+"
        )
        links_to_trade = ["".join(pattern.findall(x)) for x in tr_with_links]
        if len(links_to_trade) > 0:
            return links_to_trade
        else:
            return None

    def get_original_text_type(self):
        try:
            _form = self.response.xpath(self.loc_trade.trading_type_loc).get()
            _form = BS(str(_form), features="lxml").get_text().strip()
            return dedent_func(_form.lower())
        except Exception as e:
            logger.error(
                f"{self.response.url} :: ERROR WHILE GETTING TRADING TYPE \n{e}",
                exc_info=True,
            )
            return None

    @property
    def trading_type(self):
        auction = (
            "открытый аукцион с открытой формой представления предложений о цене",
            "открытый аукцион с открытой формой представления предложений о цене (банкротство)",
            "открытый аукцион с закрытой формой представления предложений о цене",
            "открытый аукцион с закрытой формой представления предложений о цене (банкротство)",
            "закрытый аукцион с открытой формой представления предложений о цене",
            "закрытый аукцион с открытой формой представления предложений о цене (банкротство)",
            "закрытый аукцион с закрытой формой представления предложений о цене",
            "закрытый аукцион с закрытой формой представления предложений о цене (банкротство)",
        )
        offer = (
            "открытые торги посредством публичного предложения",
            "открытые торги посредством публичного предложения (банкротство)",
            "закрытые торги посредством публичного предложения",
            "закрытые торги посредством публичного предложения (банкротство)",
        )

        competition = (
            "открытый конкурс с открытой формой представления предложений о цене",
            "открытый конкурс с открытой формой представления предложений о цене (банкротство)",
            "открытый конкурс с закрытой формой представления предложений о цене",
            "открытый конкурс с закрытой формой представления предложений о цене (банкротство)",
            "закрытый конкурс с открытой формой представления предложений о цене",
            "закрытый конкурс с открытой формой представления предложений о цене (банкротство)",
            "закрытый конкурс с закрытой формой представления предложений о цене",
            "закрытый конкурс с закрытой формой представления предложений о цене (банкротство)",
        )
        _type = self.get_original_text_type()
        if _type in auction:
            return "auction"
        if _type in offer:
            return "offer"
        if _type in competition:
            return "competition"
        return None

    @property
    def trading_form(self):
        _open = (
            "открытый аукцион с открытой формой представления предложений о цене",
            "открытый аукцион с открытой формой представления предложений о цене (банкротство)",
            "открытые торги посредством публичного предложения (банкротство)",
            "открытые торги посредством публичного предложения",
            "открытый конкурс с открытой формой представления предложений о цене",
            "открытый конкурс с открытой формой представления предложений о цене (банкротство)",
            "открытый аукцион с закрытой формой представления предложений о цене",
            "открытый аукцион с закрытой формой представления предложений о цене (банкротство)",
            "открытый конкурс с закрытой формой представления предложений о цене",
            "открытый конкурс с закрытой формой представления предложений о цене (банкротство)",
        )

        _closed = (
            "закрытый аукцион с открытой формой представления предложений о цене",
            "закрытый аукцион с открытой формой представления предложений о цене (банкротство)",
            "закрытый конкурс с открытой формой представления предложений о цене",
            "закрытый конкурс с открытой формой представления предложений о цене (банкротство)",
            "закрытый аукцион с закрытой формой представления предложений о цене",
            "закрытый аукцион с закрытой формой представления предложений о цене (банкротство)",
            "закрытый конкурс с закрытой формой представления предложений о цене",
            "закрытый конкурс с закрытой формой представления предложений о цене (банкротство)",
            "закрытые торги посредством публичного предложения",
            "закрытые торги посредством публичного предложения (банкротство)",
        )
        _form = self.get_original_text_type()
        if _form in _open:
            return "open"
        elif _form in _closed:
            return "closed"
        elif "ГК РФ" in _form:
            return None
        elif "гк рф" in _form:
            return None
        logger.warning(f"{self.response.url} :: ERROR FORM, {_form}")
        return None

    @property
    def trading_id(self):
        match = re.findall(r"\d{4,}$", str(self.response.url).strip())
        return "".join(match)

    def get_trading_number_from_serp_page(self):
        tr_with_links = self.response.xpath(self.loc_serp.links_to_trade_page).getall()
        pattern = re.compile(
            r"window.location.+(\/trade\/view\/purchase\/general\.html\?id=\d+).+"
        )
        links = []
        for link in tr_with_links:
            soup = BS(str(link), features="lxml")
            links.append(
                ["".join(pattern.findall(link)), soup.find("td").get_text(strip=True)]
            )
        return links

    @property
    def trading_number(self) -> str or None:
        _h1 = self.soup.h1.get_text()
        pattern = re.compile(r"идентификационный номер: (\d+-\D{4})\)")
        match = pattern.findall(_h1)
        if match and len(match) == 1:
            return "".join(match)
        else:
            logger.error(f"{self.response.url} :: ERROR TRADING NUMBER")
            return None

    @property
    def trading_org(self):
        org_name = self.response.xpath(self.loc_trade.trading_org_name_loc).get()
        org_name = BS(str(org_name), features="lxml").get_text().strip()
        return dedent_func(org_name)

    @property
    def email(self):
        org_email = self.response.xpath(self.loc_trade.trading_org_email_loc).get()
        org_email = BS(str(org_email), features="lxml").get_text().strip()
        return Contacts.check_email(org_email)

    @property
    def phone(self):
        org_phone = self.response.xpath(self.loc_trade.trading_org_phone_loc).get()
        phone = BS(str(org_phone), features="lxml").get_text()
        return Contacts.check_phone(phone)

    @property
    def trading_org_contacts(self):
        return {"email": self.email, "phone": self.phone}

    @property
    def arbit_manager(self):
        arb_name = self.response.xpath(self.loc_trade.arbitr_name_loc).get()
        if arb_name:
            arb_name = BS(str(arb_name), features="lxml").get_text().strip()
            return dedent_func(arb_name)
        else:
            comp_man = self.response.xpath(self.loc_trade.competiton_man).get()
            if comp_man:
                comp_man = BS(str(comp_man), features="lxml").get_text().strip()
                return dedent_func(comp_man)
        return None

    @property
    def arbit_manager_org(self):
        company = self.response.xpath(self.loc_trade.arbitr_org_loc).get()
        if company:
            company = BS(str(company), features="lxml").get_text().strip()
            return dedent_func(company)
        return None

    @property
    def msg_number(self):
        msg = self.response.xpath(self.loc_trade.msg_number_loc).get()
        return Contacts.check_msg_number(
            BS(str(msg), features="lxml").get_text().strip()
        )

    @property
    def case_number(self):
        case = self.response.xpath(self.loc_trade.case_number_loc).get()
        case = BS(str(case), features="lxml").get_text().strip()
        return Contacts.check_case_number(case)

    @property
    def debtor_inn(self):
        _inn = self.response.xpath(self.loc_trade.debtor_inn_loc).get()
        _inn = BS(str(_inn), features="lxml").get_text().strip()
        return Contacts.check_inn(_inn)

    @property
    def address(self):
        address = self.response.xpath(self.loc_trade.address_loc).get()
        return BS(str(address), features="lxml").get_text().strip()
