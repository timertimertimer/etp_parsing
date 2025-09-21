import re
import urllib.parse

import pandas as pd
import numpy as np

from bs4 import BeautifulSoup as BS

from app.utils import (
    URL,
    dedent_func,
    Contacts,
    delete_extra_symbols,
    cut_lot_number,
    get_lot_number,
    DateTimeHelper,
    logger,
)
from ..locators_and_attributes.locators_attributes import Offer
from ..config import trade_page


class OfferSpider:
    def __init__(self, response):
        self.response = response
        self.soup = BS(
            str(self.response.body.decode("utf-8"))
            .replace("&lt;", "<")
            .replace("&gt;", ">"),
            features="lxml",
        )

    def get_post_data_values(self, tag_html: str, post_argument: str) -> str | None:
        try:
            tag_html = self.soup.find(tag_html, id=post_argument)
            if tag_html:
                tag_html = tag_html["value"]
                return tag_html
        except Exception as e:
            logger.error(f" :: Exeption during fetching tag {tag_html} :: {e} ")
        return ""

    def get_ajax_and_token(self):
        try:
            ajax_control = "".join(
                [
                    s.get("src")
                    for s in self.soup.find_all("script")
                    if "AjaxControlToolkit" in str(s.get("src"))
                ]
            )
            if ajax_control and len(ajax_control) > 0:
                a = "".join(re.findall(r"TSM_CombinedScripts_=(.*)$", ajax_control))
                return urllib.parse.unquote(a, encoding="utf-8")
        except Exception as e:
            logger.error(
                f"{self.response.url} :: ERROR GETTING ctl00_ToolkitScriptManager1_HiddenField value ::\n{e}"
            )
        return ""

    @property
    def trade_link_serp(self) -> set | None:
        try:
            link_set = set()
            list_tag_links = self.response.xpath(Offer.trading_links_loc).getall()
            if list_tag_links and len(list_tag_links) > 0:
                for link in list_tag_links:
                    if link and re.match("/public.+aspx.+\d+$", link):
                        link_set.add(URL.url_join(trade_page, link))
                return link_set
        except Exception as e:
            logger.error(
                f"{self.response.url} :: ERROR DURING GETTING LINKS TO TRADING PAGE"
            )
        return set()

    def get_total_visible_pages(self, page, date):
        try:
            select = self.soup.find(
                "select", title="Выбор номера страницы"
            ).find_all_next("option")
            if len(select) > 0:
                number = select[-1].get_text()
                if number and len(number) <= 6:
                    if re.match(r"^\d+$", number):
                        return int(number)
            else:
                return 0
        except ValueError as e:
            logger.error(
                f"{e} :: {self.response.url} :: ERROR on page {page} :: time {date} "
            )
        return None

    def get_total_pages(self):
        pages = self.soup.find("span", class_="page_info").get_text(strip=True)
        current_page, total_pages = pages.split("/")
        return total_pages.strip()

    @property
    def trading_number(self) -> str | None:
        trade_number = self.response.xpath(Offer.trading_number_loc).get()
        if trade_number and len(trade_number) > 0:
            t = dedent_func(BS(str(trade_number), features="lxml").get_text()).strip()
            if len(t) > 0 and re.match(r"\d{1,12}", t):
                return Contacts.check_number(t)
        else:
            logger.warning(
                f"{self.response.url} :: INVALID DATA OR IS MISSING TARDING NUMBER"
            )
        return None

    @property
    def trading_type(self):
        trading_type = self.response.xpath(Offer.trading_type_loc).get()
        if trading_type and len(trading_type) > 0:
            type_ = dedent_func(
                BS(str(trading_type), features="lxml").get_text()
            ).strip()
            if type_ in [
                "Публичное предложение",
                "Открытое публичное предложение",
                "Закрытое публичное предложение",
            ]:
                return "offer"
            else:
                logger.warning(f"{self.response.url} :: INVALID DATA TRADING TYPE")
        return None

    @property
    def status(self):
        trading_status = self.response.xpath(Offer.trading_status_loc).get()
        if trading_status and len(trading_status) > 0:
            status = (
                dedent_func(BS(str(trading_status), features="lxml").get_text())
                .strip()
                .lower()
            )
            if status == "прием заявок":
                return "active"
            elif status == "торги объявлены":
                return "pending"
            else:
                return "ended"
        return None

    @property
    def trading_form(self):
        trading_type = self.response.xpath(Offer.trading_type_loc).get()
        if trading_type and len(trading_type) > 0:
            type_ = dedent_func(
                BS(str(trading_type), features="lxml").get_text()
            ).strip()
            if type_ in [
                "Аукцион",
                "Открытый аукцион",
                "Конкурс",
                "Открытый конкурс",
                "Публичное предложение",
                "Открытое публичное предложение",
            ]:
                return "open"
            else:
                return "closed"
        return None

    @property
    def trading_org(self):
        try:
            if_company = self.response.xpath(Offer.list_of_company_id).getall()
            person = self.response.xpath(Offer.list_person_info_id).getall()
            if len(if_company) > 0:
                for tr in if_company:
                    td = BS(str(tr), features="lxml").find_all("td")
                    if len(td) == 2:
                        if "олное наименование организаци" in dedent_func(
                                td[0].get_text()
                        ):
                            return dedent_func(td[1].get_text())
            elif len(person) > 0:
                lastname, fistname, middlename = "", "", ""
                for tr in person:
                    td = BS(str(tr), features="lxml").find_all("td")
                    if len(td) == 2:
                        if "амили" in dedent_func(td[0].get_text()):
                            lastname = dedent_func(td[1].get_text())
                        if "Имя" in dedent_func(td[0].get_text()):
                            fistname = dedent_func(td[1].get_text())
                        if "тчество" in dedent_func(td[0].get_text()):
                            middlename = dedent_func(td[1].get_text())
                return lastname + " " + fistname + " " + middlename
        except Exception as e:
            logger.error(
                f"{self.response.url} :: ERROR GETTING ORGANIZER COMPANY NAME - {e}",
                exc_info=True,
            )
        return None

    @property
    def trading_org_inn(self) -> str | None:
        try:
            if_company = self.response.xpath(Offer.list_of_company_id).getall()
            person = self.response.xpath(Offer.list_person_info_id).getall()
            if len(if_company) > 0:
                for tr in if_company:
                    td = BS(str(tr), features="lxml").find_all("td")
                    if len(td) == 2:
                        if "ИНН" in dedent_func(td[0].get_text()):
                            return Contacts.check_inn(
                                dedent_func(td[1].get_text())
                            )
            elif len(person) > 0:
                for tr in person:
                    td = BS(str(tr), features="lxml").find_all("td")
                    if len(td) == 2:
                        if "ИНН" in dedent_func(td[0].get_text()):
                            return Contacts.check_inn(
                                dedent_func(td[1].get_text())
                            )
        except Exception as e:
            logger.error(f"{self.response.url} :: {e}\n INVALID DATA ORG INN")
        return None

    @property
    def email(self):
        try:
            email = self.soup.find(id=Offer.org_email_loc).get_text()
            if email:
                return Contacts.check_email(dedent_func(email))
        except Exception as e:
            logger.error(f"{self.response.url} :: INVALID DATA EMAIL ORG\{e}")
        return None

    @property
    def phone(self):
        try:
            phone_ = self.response.xpath(Offer.phone_org_loc).get()
            if phone_:
                phone = BS(str(phone_), features="lxml").get_text()
                return Contacts.check_phone(dedent_func(phone))
        except Exception as e:
            logger.error(f"{self.response.url} :: INVALID DATA EMAIL ORG\{e}")
        return None

    @property
    def trading_org_contacts(self):
        return {"email": self.email, "phone": self.phone}

    @property
    def msg_number(self):
        msg = self.soup.find(id="ctl00_cph1_trIDEFRSB")
        if msg:
            msg_ = msg.find_next("td")
            if msg_:
                msg__ = msg_.find_next("td")
                if msg__:
                    msg = dedent_func(msg__.get_text())
                return " ".join(re.findall(r"\d{6,9}", msg))
        return None

    @property
    def case_number(self):
        case = self.soup.find(id="ctl00_cph1_trDealNum")
        if case:
            case_ = case.find_next("td")
            if case_:
                case__ = case_.find_next("td")
                if case__:
                    case = dedent_func(case__.get_text())
                    if len(case) > 4:
                        return Contacts.check_case_number(case)
        return None

    @property
    def debtor_inn(self):
        try:
            debtor = self.response.xpath(Offer.list_debtor_id).getall()
            if len(debtor) > 0:
                for tr in debtor:
                    td = BS(str(tr), features="lxml").find_all("td")
                    if len(td) == 2:
                        if "ИНН" in dedent_func(td[0].get_text()):
                            return Contacts.check_inn(
                                dedent_func(td[1].get_text())
                            )
        except Exception as e:
            logger.error(f"{self.response.url} :: INVALID DATA dbtor inn")
        return None

    @property
    def address(self):
        try:
            address = self.response.xpath(Offer.sud_loc).get()
            if address:
                address = BS(str(address), features="lxml").find(
                    "span", id="ctl00_cph1_lDealArbJud"
                )
                if address:
                    return dedent_func(" ".join(address.get_text(strip=True).split()))
        except Exception as e:
            logger.error(f"{self.response.url} :: INVALID DATA sud address")
        return None

    @property
    def arbit_manager(self):
        try:
            arbitr = self.response.xpath(Offer.list_arbitr_id).getall()
            lastname, fistname, middlename = "", "", ""
            for tr in arbitr:
                td = BS(str(tr), features="lxml").find_all("td")
                if len(td) == 2:
                    if "Не требуется для данных торгов" not in td[1].get_text():
                        if "амили" in dedent_func(td[0].get_text()):
                            lastname = dedent_func(td[1].get_text())
                        if "Имя" in dedent_func(td[0].get_text()):
                            fistname = dedent_func(td[1].get_text())
                        if "тчество" in dedent_func(td[0].get_text()):
                            middlename = dedent_func(td[1].get_text())
                    else:
                        return None
            return " ".join([lastname, fistname, middlename])
        except Exception as e:
            logger.error(f"{self.response.url} :: INVALID DATA ARBITR NAME")
        return None

    @property
    def arbit_manager_inn(self):
        try:
            arbitr = self.response.xpath(Offer.list_arbitr_id).getall()
            if len(arbitr) > 0:
                for tr in arbitr:
                    td = BS(str(tr), features="lxml").find_all("td")
                    if len(td) == 2:
                        if "ИНН" in dedent_func(td[0].get_text()):
                            return Contacts.check_inn(
                                dedent_func(td[1].get_text()).strip()
                            )
        except Exception as e:
            logger.error(f"{self.response.url} :: INVALID DATA arbitr inn")
        return None

    @property
    def arbit_manager_org(self):
        try:
            arbitr_org = self.response.xpath(Offer.list_arbitr_id).getall()
            if len(arbitr_org) > 0:
                for tr in arbitr_org:
                    td = BS(str(tr), features="lxml").find_all("td")
                    if len(td) == 2:
                        if "организации арбитражных управляющ" in dedent_func(
                                td[0].get_text().strip()
                        ):
                            org = dedent_func(td[1].get_text())
                            if "Не требуется для данных торгов" not in org:
                                if "(" in org:
                                    return "".join(re.split(r"\(", org, maxsplit=1)[0])
                                else:
                                    return org
        except Exception as e:
            logger.error(f"{self.response.url} :: INVALID DATA ARBITR COMPANY")
        return None

    @property
    @delete_extra_symbols
    @cut_lot_number
    def short_name(self):
        try:
            short_name = self.soup.find(id=Offer.short_name_id_loc)
            if short_name:
                return dedent_func(short_name.get_text())
        except Exception as e:
            logger.error(f"{self.response.url}")
        return None

    @property
    @delete_extra_symbols
    @cut_lot_number
    def lot_info(self):
        try:
            lot_info = self.soup.find(id=Offer.lot_info_id_loc)
            if lot_info:
                return dedent_func(lot_info.get_text())
        except Exception as e:
            logger.error(f"{self.response.url}:: INVALID DATA LOT INFO")
        return None

    @property
    @get_lot_number
    def lot_number(self):
        try:
            short_name = self.soup.find(id=Offer.short_name_id_loc)
            if short_name:
                return dedent_func(short_name.get_text())
        except Exception as e:
            logger.error(f"{self.response.url}")
        return None

    @property
    def property_information(self):
        try:
            property_ = self.soup.find(id=Offer.property_info_if_loc)
            if property_:
                return dedent_func(property_.get_text())
        except Exception as e:
            logger.error(f"{self.response.url}:: INVALID DATA LOT INFO")
        return None

    # WORKING WITH PERIOD TABLE
    def get_period_table(self) -> list | None:
        try:
            lst_table = self.response.xpath(Offer.period_table).getall()
            if lst_table and len(lst_table) > 0:
                return lst_table
            else:
                logger.error(f"{self.response.url} :: PERIOD TABLE WAS NOT FOUND")
        except Exception as e:
            logger.error(f"{e}")
        return None

    def clean_period_table(self):
        try:
            if self.get_period_table():
                table = BS(self.get_period_table()[0], features="lxml")
                new_lst = list()
                exc_w = [
                    "рафик снижения цены",
                    "ачало периода действи",
                    "онец периода действи",
                ]
                for tr in table.find_all("tr"):
                    text_tr = tr.get_text()
                    if (
                            (exc_w[0] not in text_tr)
                            and (exc_w[1] not in text_tr)
                            and (exc_w[2] not in text_tr)
                    ):
                        if len(text_tr) > 0:
                            new_lst.append(BS(str(tr), features="lxml"))
                return new_lst
        except Exception as e:
            logger.error(
                f"{e} :: ERROR FORMATING NEW LIST WITH TABLE PERIOD DATA T ODATA FRAME"
            )
        return None

    def create_df_period(self):
        try:
            lst_df = list()
            for d in self.clean_period_table():
                td = [t.get_text() for t in d.find_all("td")]
                lst_df.append(td)
            df2 = pd.DataFrame(
                np.array(lst_df), columns=["seq", "start_date", "end_date", "price"]
            )
            return df2
        except Exception as e:
            logger.error(
                f"{self.response.url} :: ERROR CREATE DATA FRAME(PERIOD TABLE) :: {e}"
            )
        return None

    @property
    def periods(self):
        df = self.create_df_period()

        periods = list()
        for i in range(len(df)):
            start = self.create_df_period().iloc[i]["start_date"]
            end = self.create_df_period().iloc[i]["end_date"]
            price = self.create_df_period().iloc[i]["price"]
            if isinstance(price, str):
                price = "".join(re.sub(r"\s", "", price)).replace(",", ".")
                price = round(float(price), 2)
            else:
                # if numpy object (but in this case it's not imposible and just in case)
                price = round(float(price), 2)
            period = {
                "start_date_requests": DateTimeHelper.smart_parse(start).astimezone(DateTimeHelper.moscow_tz),
                "end_date_requests": DateTimeHelper.smart_parse(end).astimezone(DateTimeHelper.moscow_tz),
                "end_date_trading": DateTimeHelper.smart_parse(end).astimezone(DateTimeHelper.moscow_tz),
                "current_price": price,
            }
            periods.append(period)
        return periods

    @property
    def start_date_requests(self):
        try:
            start_date = self.create_df_period().iloc[0]["start_date"]
            return DateTimeHelper.smart_parse(start_date).astimezone(DateTimeHelper.moscow_tz)
        except Exception as e:
            logger.error(
                f"{self.response.url} :: START DATE REQUEST ERROR - OFFER\n{e}"
            )
        return None

    @property
    def start_date_trading(self):
        return self.start_date_requests

    @property
    def end_date_requests(self):
        try:
            start_date = self.create_df_period().iloc[-1]["end_date"]
            return DateTimeHelper.smart_parse(start_date).astimezone(DateTimeHelper.moscow_tz)
        except Exception as e:
            logger.error(
                f"{self.response.url} :: START DATE REQUEST ERROR - OFFER\n{e}"
            )
        return None

    @property
    def end_date_trading(self):
        return self.end_date_requests

    @property
    def start_price(self):
        try:
            price = self.create_df_period.iloc[0]["price"]
            price = "".join(re.sub(r"\s", "", price)).replace(",", ".")
            return round(float(price), 2)
        except Exception as e:
            logger.error(
                f"{self.response.url} :: START DATE REQUEST ERROR - OFFER\n{e}"
            )
        return None
