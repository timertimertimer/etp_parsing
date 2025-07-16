import re
from collections import deque

from bs4 import BeautifulSoup

from app.utils import dedent_func, Contacts, logger


class SerpParse:
    def __init__(self, response):
        self.response = response
        self.soup = BeautifulSoup(self.response.text, "lxml")

    def get_current_page(self):
        try:
            pag_ul = self.soup.find("ul", class_="pagination")
            if pag_ul:
                active_page = pag_ul.find("li", class_="active").get_text()
                if re.match(r"\d+", active_page):
                    return int(active_page)
                else:
                    logger.warning(f"{self.response.url} | ACTIVE PAGE NOT AN INTEGER")
                    return 0
            else:
                logger.warning(f"{self.response.url} | PAGINATION TAG NOT FOUND")
                return 0
        except Exception as e:
            logger.warning(f"{self.response.url} | INVALID DATA CURRENT PAGE {e}")
            return 1

    def get_next_page(self):
        try:
            pag_ul = self.soup.find("ul", class_="pagination")
            if pag_ul:
                active_page = pag_ul.find("li", class_="active")
                next_page = active_page.findNext("li")
                if next_page:
                    next_page = next_page.get_text()
                    if re.match(r"\d+", next_page):
                        return int(next_page)
                    else:
                        return 0
            else:
                return 0
        except Exception as e:
            logger.warning(f"{self.response.url} | INVALID DATA NEXT PAGE {e}")
        return None

    def links_to_trade(self, table_class: str = "data") -> list:
        set_links = set()
        try:
            tbody = self.soup.find("table", class_=table_class).find("tbody")
            tr_list = tbody.find_all("tr")
            if tr_list:
                for tr in tr_list:
                    td = tr.find_all("td")[0].get_text()
                    link = re.findall(r"/trade_view.php\?trade_nid=\d+", str(tr))
                    if link:
                        set_links.add((link[0].lstrip("/"), td))
                return list(set_links)
        except Exception as e:
            logger.warning(
                f"{self.response.url} | INVALID DATA DURING GETTING LINKS TO TRADE {e}"
            )
        return list()

    def get_table_with_lots(self):
        table = self.soup.find("table", class_="views-table")
        if table is None:
            table = self.soup.find(
                "th", string=re.compile("Предмет торгов")
            ).find_parent("table")
        if table:
            tag_thead = table.thead
            tag_thead.decompose()
            return table
        return None

    def get_lots_data(self):
        if table := self.get_table_with_lots():
            short_lot_data = list()
            for tr in table.find_all("tr"):
                trade_link = tr.find_all("td")[0].find("a").get("href")
                trading_type = dedent_func(tr.find_all("td")[0].get_text())
                lot_link = tr.find_all("td")[1].find("a").get("href")
                organizer = dedent_func(tr.find_all("td")[2].get_text())
                status = dedent_func(tr.find_all("td")[6].get_text())
                short_lot_data.append(
                    (trade_link, lot_link, organizer, trading_type, status)
                )
            return deque(short_lot_data)
        return list()

    def get_trading_type_and_form(self, trading_type_text):
        offer = ["ОТПП", "ЗТПП"]
        auction = ["ОАОФ", "ОАЗФ", "ЗАОФ", "ЗАОЗ"]
        competition = ["ОКОФ", "ОКЗФ", "ЗКОФ", "ЗКОЗ"]
        open_form = ["ОТПП", "ОАОФ", "ОАЗФ", "ОКОФ", "ОКЗФ"]
        close_form = ["ЗТПП", "ЗАОФ", "ЗАОЗ", "ЗКОФ", "ЗКОЗ"]
        trading_type = re.findall(r"\d{4,}.?-.?\D{4}", trading_type_text)
        if len(trading_type) == 1:
            trading_type = re.findall(
                r"\D{4}", trading_type[0].replace("-", "").strip()
            )
            trading_type = trading_type[0].strip()
            if trading_type in offer and trading_type in open_form:
                return "offer", "open"
            if trading_type in offer and trading_type in close_form:
                return "offer", "closed"
            if trading_type in auction and trading_type in open_form:
                return "auction", "open"
            if trading_type in auction and trading_type in close_form:
                return "auction", "closed"
            if trading_type in competition and trading_type in open_form:
                return "competition", "open"
            if trading_type in competition and trading_type in close_form:
                return "competition", "closed"
        logger.warning(
            f"{self.response.url} | ERROR function {self.get_trading_type_and_form.__name__}"
        )
        return None

    def get_trading_number(self, trading_type_text):
        tradin_number = re.findall(r"\d{4,}.?-\D{4}", trading_type_text)
        if len(tradin_number) == 1:
            return dedent_func("".join(tradin_number))
        logger.warning(
            f"{self.response.url} | ERROR function {self.get_trading_number.__name__}"
        )
        return None

    def get_status_of_trade(self, status_text, trading_page):
        status = dedent_func(status_text)
        active = ("Прием заявок",)
        pending = ("Торги объявлены", "Ожидает публикации")
        ended = (
            "Прием заявок завершен",
            "Идут торги",
            "Подведение результатов торгов",
            "Подведение итогов",
            "Торги отменены",
            "Торги завершены",
            "Торги не состоялись",
            "Торги приостановлены",
        )

        if status in active:
            return "active"
        elif status in pending:
            return "pending"
        elif status in ended:
            return "ended"
        logger.warning(
            f"{self.response.url} | ERROR STATUS OF TRADE on page {trading_page}"
        )
        return None

    def get_trading_id(self):
        _id = "".join(re.findall(r"\d+$", self.response.url))
        return _id

    def get_curent_page(self):
        current = self.soup.find("ul", class_="pagination").find("li", class_="active")
        if current:
            current = dedent_func(current.get_text())
            if re.match(r"\d{1,3}", current):
                return int(current)
        logger.warning(f"{self.response.url} | ERROR GETTING CURRENT PAGE")
        return -1

    # TRADING PAGE

    def table_trading_page_trade_info(self):
        table = self.soup.find(
            "th", string=re.compile("Информация о проведении торгов", re.IGNORECASE)
        ).find_parent("table")
        if table:
            return table
        logger.warning(
            f"{self.response.url} | ERROR function {self.table_trading_page_trade_info.__name__}"
        )
        return None

    def table_organizer_info(self):
        table = self.soup.find(
            "th", string=re.compile("Информация об организаторе", re.IGNORECASE)
        ).find_parent("table")
        if table:
            return table
        logger.warning(
            f"{self.response.url} | ERROR function {self.table_organizer_info.__name__}"
        )
        return None

    def get_organizer_inn(self):
        try:
            if table := self.table_organizer_info():
                text = "ИНН"
                org_inn = table.find("td", string=re.compile(text, re.IGNORECASE))
                if len(org_inn.get_text().strip()) > 3:
                    text = "^ИНН$"
                    org_inn = table.find("td", string=re.compile(text, re.IGNORECASE))
                org_inn = org_inn.findNextSibling("td").get_text()
                return Contacts.check_inn(dedent_func(org_inn))
        except Exception as e:
            logger.warning(f"{self.response.url} | ERROR INN")
        return None

    def get_organizer_email(self):
        if table := self.table_organizer_info():
            text = "Адрес электронной почты"
            org_email = table.find("td", string=re.compile(text, re.IGNORECASE))
            if org_email:
                org_email = org_email.findNextSibling("td").get_text()
                return Contacts.check_email(dedent_func(org_email))
        return None

    def get_organizer_phone(self):
        if table := self.table_organizer_info():
            text = "Телефон"
            org_phone = table.find("td", string=re.compile(text, re.IGNORECASE))
            if org_phone:
                org_phone = org_phone.findNextSibling("td").get_text()
                return Contacts.check_phone(dedent_func(org_phone))
        return None

    def get_organizer_contacts(self):
        return {
            "email": self.get_organizer_email(),
            "phone": self.get_organizer_phone(),
        }

    def get_msg_number(self):
        if table := self.table_trading_page_trade_info():
            text = "Номер объявления о проведении торгов"
            td_msg = table.find("td", string=re.compile(text, re.IGNORECASE))
            if td_msg:
                msg = re.findall(r"\d{6,8}", td_msg.findNextSibling("td").get_text())
                return " ".join(msg)
        return None

    def table_trading_page_bankrot_info(self):
        table = self.soup.find(
            "th", string=re.compile("Сведения о банротстве", re.IGNORECASE)
        ).find_parent("table")
        if table:
            return table
        logger.warning(
            f"{self.response.url} | ERROR function {self.table_trading_page_bankrot_info.__name__}"
        )
        return None

    def get_case_number(self):
        if table := self.table_debtor_info():
            text = "Номер дела о банкротстве"
            td_case_number = (
                table.find("td", string=re.compile(text, re.IGNORECASE))
                .findNextSibling("td")
                .get_text()
            )
            return Contacts.check_case_number(dedent_func(td_case_number))
        return None

    def table_debtor_info(self):
        table = self.soup.find(
            "th", string=re.compile("Информация о должнике", re.IGNORECASE)
        ).find_parent("table")
        if table:
            return table
        logger.warning(
            f"{self.response.url} | ERROR function {self.table_debtor_info.__name__}"
        )
        return None

    def get_debtor_inn(self):
        if table := self.table_debtor_info():
            text = "ИНН"
            org_inn = (
                table.find("td", string=re.compile(text, re.IGNORECASE))
                .findNextSibling("td")
                .get_text()
            )
            return Contacts.check_inn(dedent_func(org_inn))
        return None

    @property
    def address(self):
        try:
            if table := self.table_debtor_info():
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
        except Exception as e:
            logger.warning(f"{self.response.url} | Error: {e}")
        return None

    def table_arbitrator_info(self):
        table = self.soup.find(
            "th",
            string=re.compile("Информация об арбитражном управляющем", re.IGNORECASE),
        ).find_parent("table")
        if table:
            return table
        logger.warning(
            f"{self.response.url} | ERROR function {self.table_arbitrator_info.__name__}"
        )
        return None

    def get_arbitrator_name(self):
        if table := self.table_arbitrator_info():
            arb_last_name = (
                table.find("td", string=re.compile("Фамилия", re.IGNORECASE))
                .findNextSibling("td")
                .get_text(strip=True)
            )
            arb_first_name = (
                table.find("td", string=re.compile("Имя", re.IGNORECASE))
                .findNextSibling("td")
                .get_text(strip=True)
            )
            arb_dad_name = (
                table.find("td", string=re.compile("Отчество", re.IGNORECASE))
                .findNextSibling("td")
                .get_text(strip=True)
            )
            return " ".join([arb_last_name, arb_first_name, arb_dad_name])
        return None

    def get_arbitr_inn(self):
        if table := self.table_arbitrator_info():
            text = "ИНН"
            arb_inn = (
                table.find("td", string=re.compile(text, re.IGNORECASE))
                .findNextSibling("td")
                .get_text()
            )
            return Contacts.check_inn(dedent_func(arb_inn))
        return None

    def get_arbitr_company(self):
        if table := self.table_arbitrator_info():
            text = "Наименование СРО"
            arb_company = (
                table.find("td", string=re.compile(text, re.IGNORECASE))
                .findNextSibling("td")
                .get_text()
            )
            return dedent_func(arb_company)
        return None
