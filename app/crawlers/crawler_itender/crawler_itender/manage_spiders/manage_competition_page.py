import re

from bs4 import BeautifulSoup as BS

from app.utils import dedent_func, DateTimeHelper, logger
from ..locators.serp_locator import LocatorSerp
from ..locators.competition_locator import CompetLocator


class CompetitionPage:
    def __init__(self, _response):
        self.response = _response
        self.loc = LocatorSerp
        self.loc_comp = CompetLocator
        self.soup = BS(
            str(self.response.body.decode("utf-8"))
            .replace("&lt;", "<")
            .replace("&gt;", ">"),
            features="lxml",
        )

    @property
    def trading_number(self):
        try:
            legend = self.response.xpath(self.loc_comp.trading_num_loc).get()
            if legend:
                legend = BS(str(legend), features="lxml").get_text()
                legend = "".join(re.findall(r"\d+", legend))
                return legend
        except Exception as e:
            logger.warning(
                f"{self.response.url} :: ERROR TRADING NUMBER\n{e}", exc_info=True
            )
        return None

    @property
    def msg_number(self):
        msg = self.response.xpath(self.loc_comp.msg_number_loc).get()
        if msg:
            msg = BS(str(msg), features="lxml").get_text()
            return " ".join(re.findall(r"\d{6,8}", dedent_func(msg)))
        return None

    @property
    def trading_form(self):
        try:
            form = self.response.xpath(self.loc_comp.trading_form_loc).get()
            if form:
                form = BS(str(form), features="lxml").get_text().lower()
                if "открытая" == form:
                    return "open"
                elif "закрытая" == form:
                    return "closed"
                else:
                    logger.warning(f"{self.response.url} :: ERROR TRADING FORM")
        except Exception:
            logger.warning(f"{self.response.url} :: TRDING TYPE ERROR")
        return None

    @property
    def start_date_requests(self):
        try:
            start = self.response.xpath(self.loc_comp.start_date_request_loc).get()
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
            end = self.response.xpath(self.loc_comp.end_date_request_loc).get()
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
            start = self.response.xpath(self.loc_comp.start_date_trading_loc).get()
            if start:
                start = dedent_func(BS(str(start), features="lxml").get_text())
                return DateTimeHelper.smart_parse(start.strip()).astimezone(DateTimeHelper.moscow_tz)
            elif extra_start := self.response.xpath(
                self.loc_comp.extra_start_date_trading
            ).get():
                extra_start = dedent_func(
                    BS(str(extra_start), features="lxml").get_text()
                )
                return DateTimeHelper.smart_parse(extra_start.strip()).astimezone(DateTimeHelper.moscow_tz)
            elif start_utender := self.response.xpath(
                self.loc_comp.start_date_trading_utender_loc
            ).get():
                start_utender = dedent_func(
                    BS(str(start_utender), features="lxml").get_text()
                )
                return DateTimeHelper.smart_parse(start_utender.strip()).astimezone(DateTimeHelper.moscow_tz)
            else:
                logger.warning(
                    f"{self.response.url} :: START DATE TRADING ERROR (COMPETITION)"
                )
        except Exception as e:
            logger.warning(
                f"{self.response.url} :: START DATE TRADING ERROR (COMPETITION)::{e}"
            )
        return None

    @property
    def property_information(self):
        property_info = self.response.xpath(self.loc_comp.property_info_loc).get()
        if property_info:
            property_info = dedent_func(
                BS(str(property_info), features="lxml").get_text()
            )
            return property_info.strip()
        return None
