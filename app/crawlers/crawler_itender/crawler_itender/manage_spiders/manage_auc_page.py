import re

from bs4 import BeautifulSoup as BS

from app.utils import dedent_func, Contacts, URL, DateTimeHelper, logger, make_float
from ..locators.serp_locator import LocatorSerp
from ..locators.auction_locator import AuctionLocator


class AuctionPage:
    def __init__(self, response):
        self.response = response
        self.loc = LocatorSerp
        self.loc_auc = AuctionLocator
        self.soup = BS(
            str(self.response.body.decode("utf-8"))
            .replace("&lt;", "<")
            .replace("&gt;", ">"),
            features="lxml",
        )

    @property
    def pagination(self):
        p = self.response.xpath(self.loc_auc.pagination_on_page).getall()
        try:
            if len(p) > 0 and len(p[0]) > 0:
                return p
            else:
                p[0] = 0
                return p
        except Exception:
            logger.warning(f"{self.response.url} :: INVALID DATA PAGINATION ON PAGE")
            return 0

    @property
    def extra_pagination(self):
        p1 = self.response.xpath(self.loc_auc.pagination_reverse_loc).get()
        try:
            if len(p1) > 0 and len(p1[0]) > 0:
                return p1
            else:
                p1[0] = 0
                return p1
        except Exception:
            logger.warning(f"{self.response.url} :: INVALID DATA PAGINATION ON PAGE")
            return 0

    @property
    def trading_number(self):
        legend = None
        try:
            legend = self.response.xpath(self.loc.trading_num_loc).get()
            if legend:
                legend = BS(str(legend), features="lxml").get_text()
                legend = "".join(re.findall(r"\d+", legend))
        except Exception as e:
            logger.warning(
                f"{self.response.url} :: ERROR TRADING NUMBER\n{e}", exc_info=True
            )
        return legend

    @property
    def trading_form(self):
        try:
            form = (
                self.response.xpath(self.loc.trading_form_loc).get()
                or self.response.xpath(self.loc.trading_form_loc_2).get()
            )
            if form:
                form = BS(str(form), features="lxml").get_text().lower()
                if "открытая" == form:
                    return "open"
                elif "закрытая" == form:
                    return "closed"
                else:
                    logger.warning(f"{self.response.url} :: ERROR TRADING FORM")
        except Exception as e:
            logger.warning(f"{self.response.url} :: TRADING TYPE ERROR\n{e}")
        return None

    @property
    def trading_org(self):
        try:
            org = self.response.xpath(self.loc_auc.oranizer_name_loc).get()
            if org:
                org = BS(str(org), features="lxml").get_text()
                return dedent_func(org)
        except Exception as e:
            logger.warning(f"{self.response.url} :: ERROR ORGANIZER NAME\n{e}")
        return None

    @property
    def trading_org_inn(self):
        try:
            _inn = self.response.xpath(self.loc_auc.organizer_inn_loc).get()
            if _inn:
                _inn = BS(str(_inn), features="lxml").get_text()
                return Contacts.check_inn(dedent_func(_inn))
        except Exception as e:
            logger.warning(f"{self.response.url} ::: ERROR INN ORG")
        return None

    @property
    def phone(self):
        phone = None
        try:
            phone = self.response.xpath(self.loc_auc.organizer_phone_loc).get()
            if phone:
                phone = BS(str(phone), features="lxml").get_text()
                phone = Contacts.check_phone(dedent_func(phone))
        except Exception:
            logger.warning(f"{self.response.url} ::: ERROR INN ORG")
        return phone

    @property
    def email(self):
        email = None
        try:
            email = self.response.xpath(self.loc_auc.organizer_email_loc).get()
            if email:
                email = BS(str(email), features="lxml").get_text()
                email = Contacts.check_email(dedent_func(email))
        except Exception as e:
            logger.warning(f"{self.response.url} ::: ERROR INN ORG\n{e}")
        return email

    @property
    def trading_org_contacts(self):
        return {"email": self.email, "phone": self.phone}

    @property
    def msg_number(self):
        msg = self.response.xpath(self.loc_auc.msg_number_loc).get()
        if msg:
            msg = BS(str(msg), features="lxml").get_text()
            msg = " ".join(re.findall(r"\d{6,8}", dedent_func(msg)))
        return msg

    @property
    def case_number(self):
        number = self.response.xpath(self.loc_auc.case_number_loc).get()
        if number:
            number = BS(str(number), features="lxml").get_text()
            if len(number) > 4:
                return Contacts.check_case_number(number)
        return None

    @property
    def debtor_inn(self):
        try:
            _inn = self.response.xpath(self.loc_auc.debtor_inn_loc).get()
            if _inn:
                _inn = BS(str(_inn), features="lxml").get_text()
                return Contacts.check_inn(dedent_func(_inn))
        except Exception as e:
            logger.warning(f"{self.response.url} ::: ERROR INN DEBTOR\n{e}")
        return None

    @property
    def address(self):
        try:
            address = self.response.xpath(self.loc_auc.address_loc).get()
            if address:
                address = BS(str(address), features="lxml").get_text()
                if address.lower() == "не определен":
                    address = BS(
                        str(self.response.xpath(self.loc_auc.sud_loc).get()), "lxml"
                    ).get_text()
                return address
        except Exception as e:
            logger.warning(f"{self.response.url} ::: ERROR ADDRESS DEBTOR\n{e}")
        return None

    @property
    def arbit_manager(self):
        try:
            arbitr = self.response.xpath(self.loc_auc.arbitr_name_loc).get()
            if arbitr:
                arbitr = BS(str(arbitr), features="lxml").get_text()
                return dedent_func(" ".join(arbitr.split()))
        except Exception as e:
            logger.warning(f"{self.response.url} :: ERROR ARBITR NAME\n{e}")
        return None

    @property
    def arbit_manager_org(self):
        try:
            company = self.response.xpath(self.loc_auc.arbitr_org_loc).get()
            if company:
                company = BS(str(company), features="lxml").get_text()
                company = dedent_func(company)
                if "(" in company:
                    return "".join(re.split(r"\(", company, maxsplit=1)[0])
                else:
                    return company
        except Exception as e:
            logger.warning(f"{self.response.url} :: ERROR company NAME\n{e}")
        return None

    @property
    def arbit_manager_inn(self):
        if self.arbit_manager == self.trading_org:
            return self.trading_org_inn
        return None

    # lot
    @property
    def status(self):
        try:
            active = ("Прием заявок", "Приём заявок")
            pending = ("Извещение опубликовано",)
            ended = (
                "Прием заявок на интервале не активен",
                "Определение участников торгов",
                "Идут торги",
                "Подведение результатов", "Подведение итогов",
                "Окончен", "Оконченный",
                "Не состоялся",
                "Отменен организатором",
                "Отменён организатором",
                "Приостановлен",
                "Приём заявок на интервале неактивен",
                "Контракт заключён"
            )
            status = self.response.xpath(self.loc_auc.status_loc).get()
            if status:
                status = dedent_func(
                    BS(str(status), features="lxml").get_text().strip()
                )
                if status and len(status) > 0:
                    if status in active:
                        return "active"
                    elif status in pending:
                        return "pending"
                    elif status in ended:
                        return "ended"
                    elif status2 := self.response.xpath(self.loc_auc.status2_loc).get():
                        status2 = dedent_func(
                            BS(str(status2), features="lxml").get_text().strip()
                        )
                        if status2 in active:
                            return "active"
                        elif status2 in pending:
                            return "pending"
                        elif status2 in ended:
                            return "ended"
                        else:
                            logger.warning(f"{self.response.url} :: INVALID STATUS")
                            return None
                    else:
                        logger.warning(f"{self.response.url} :: INVALID STATUS")
                        return None
        except Exception as e:
            logger.warning(
                f"{self.response.url} :: INVALID DATA STATUS {e}", exc_info=True
            )
        return None

    def get_lot_link(self, lot_number: str, data_origin) -> str or None:
        try:
            legend = self.response.xpath(self.loc_auc.lot_table).get()
            if legend:
                legend = BS(str(legend), features="lxml")
                table = legend.find("legend", string="Лоты аукциона").parent
                if table and len(table) > 0:
                    link = table.find("a", string=lot_number.strip())
                    if link:
                        link = link.get("href")
                        return URL.url_join(data_origin, link)
        except Exception as e:
            logger.warning(
                f"{self.response.url} :{e}: INVALID DATA LOT TABLE", exc_info=True
            )
        return None

    def lot_number_on_lot_page(self, referer=None, lot_number=None):
        try:
            lot_legend = self.response.xpath(self.loc_auc.lot_number_loc).get()
            if lot_legend:
                legend = BS(str(lot_legend), features="lxml").get_text()
                number = re.findall(r"\d+$", dedent_func(legend.strip()))
                if number and lot_number:
                    if lot_number == "".join(number):
                        return "".join(number)
        except Exception as e:
            logger.warning(f"{self.response.url} :: referer {referer} \n{e}")
        return None

    @property
    def short_name(self):
        short = self.response.xpath(self.loc_auc.short_name_loc).get()
        if short:
            short = dedent_func(BS(str(short), features="lxml").get_text())
            return short.strip()
        return None

    @property
    def lot_info(self):
        lot_info = self.response.xpath(self.loc_auc.lot_info_loc).get()
        if lot_info:
            lot_info = dedent_func(BS(str(lot_info), features="lxml").get_text())
            return lot_info.strip()
        return None

    @property
    def property_information(self):
        property_info = self.response.xpath(self.loc_auc.property_info_loc).get()
        if property_info:
            property_info = dedent_func(
                BS(str(property_info), features="lxml").get_text()
            )
            return property_info.strip()
        return None

    @property
    def start_date_requests(self):
        try:
            start = self.response.xpath(self.loc_auc.start_date_request_loc).get()
            if start:
                start = dedent_func(BS(str(start), features="lxml").get_text())
                return DateTimeHelper.smart_parse(start.strip()).astimezone(DateTimeHelper.moscow_tz)
            else:
                logger.warning(
                    f"{self.response.url} :: START DATE REQUEST ERROR AUCTION(COMPETITION)"
                )
        except Exception as e:
            logger.warning(
                f"{self.response.url} :: START DATE REQUEST ERROR AUCTION(COMPETITION)::{e}"
            )
        return None

    @property
    def end_date_requests(self):
        try:
            end = self.response.xpath(self.loc_auc.end_date_request_loc).get()
            if end:
                end = dedent_func(BS(str(end), features="lxml").get_text())
                return DateTimeHelper.smart_parse(end.strip()).astimezone(DateTimeHelper.moscow_tz)
            else:
                logger.warning(
                    f"{self.response.url} :: end DATE REQUEST ERROR AUCTION(COMPETITION)"
                )
        except Exception as e:
            logger.warning(
                f"{self.response.url} :: end DATE REQUEST ERROR AUCTION(COMPETITION)::{e}"
            )
        return None

    @property
    def start_date_trading(self):
        try:
            start = self.response.xpath(self.loc_auc.start_date_trading_loc).get()
            if start:
                start = dedent_func(BS(str(start), features="lxml").get_text())
                return DateTimeHelper.smart_parse(start.strip()).astimezone(DateTimeHelper.moscow_tz)
            elif extra_start := self.response.xpath(
                self.loc_auc.extra_start_date_trading
            ).get():
                extra_start = dedent_func(
                    BS(str(extra_start), features="lxml").get_text()
                )
                return DateTimeHelper.smart_parse(extra_start.strip()).astimezone(DateTimeHelper.moscow_tz)
            elif start_utender := self.response.xpath(
                self.loc_auc.start_date_trading_utender_loc
            ).get():
                start_utender = dedent_func(
                    BS(str(start_utender), features="lxml").get_text()
                )
                return DateTimeHelper.smart_parse(start_utender.strip()).astimezone(DateTimeHelper.moscow_tz)
            else:
                logger.warning(
                    f"{self.response.url} :: START DATE TRADING ERROR AUCTION(COMPETITION)"
                )
        except Exception as e:
            logger.warning(
                f"{self.response.url} :: START DATE TRADING ERROR AUCTION(COMPETITION)::{e}"
            )
        return None

    @property
    def start_price(self):
        try:
            price = self.response.xpath(self.loc_auc.start_price_auc_loc).get()
            extra_price = self.response.xpath(
                self.loc_auc.start_price_extra_auc_loc
            ).get()
            if price:
                price = dedent_func(
                    BS(str(price), features="lxml").get_text().strip().replace(",", ".")
                )
                return make_float(price)
            elif extra_price:
                extra_price = dedent_func(
                    BS(str(extra_price), features="lxml")
                    .get_text()
                    .strip()
                    .replace(",", ".")
                )
                extra_price = "".join(
                    [x for x in extra_price if x.isdigit() or x == "."]
                )
                if len(extra_price) > 0:
                    return round(float(extra_price), 2)
            else:
                logger.warning(
                    f"{self.response.url} :: INVALID DATA START PRICE AUCTION/COMPETITION"
                )
        except Exception as e:
            logger.warning(
                f"{self.response.url} :: INVALID DATA START PRICE AUCTION/COMPETITION\n{e}"
            )
        return None

    @property
    def step_price(self):
        try:
            rub = (
                self.response.xpath(self.loc_auc.step_price_auc_rub).get()
                or self.response.xpath(self.loc_auc.step_price_auc_rub_2).get()
            )
            if rub:
                price = dedent_func(
                    BS(str(rub), features="lxml").get_text().strip().replace(",", ".")
                )
                if price:
                    return make_float(price)
            elif percent := self.response.xpath(
                self.loc_auc.step_price_auc_percent
            ).get():
                if percent:
                    price = dedent_func(
                        BS(str(rub), features="lxml")
                        .get_text()
                        .strip()
                        .replace(",", ".")
                    )
                    price = "".join([x for x in price if x.isdigit() or x == "."])
                    if len(price) > 0:
                        start_price = self.start_price
                        return round(float((start_price * int(price) / 100)), 2)
        except Exception as e:
            logger.warning(
                f"{self.response.url} :: INVALID DATA STEP PRICE AUCTION/COMPETITION\n{e}"
            )
        return None

    @property
    def categories(self):
        categories = self.response.xpath(self.loc_auc.categories_loc).get()
        if categories:
            return ". ".join(
                [
                    category.get_text(strip=True)
                    for category in BS(str(categories), features="lxml").find_all(
                        "tr", class_="gridRow"
                    )
                ]
            )
        return None
