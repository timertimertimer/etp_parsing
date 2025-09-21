import re
import pandas as pd
from bs4 import BeautifulSoup as BS

from app.utils import dedent_func, URL, DateTimeHelper, logger
from app.db.models import DownloadData
from ..config import data_origin
from ..locators.serp_locator import LocatorSerp
from ..locators.offer_locator import OfferLocator


class OfferPage:
    def __init__(self, _response):
        self.response = _response
        self.loc = LocatorSerp
        self.loc_offer = OfferLocator
        self.soup = BS(
            str(self.response.body.decode("utf-8"))
            .replace("&lt;", "<")
            .replace("&gt;", ">"),
            features="lxml",
        )

    @property
    def trading_number(self):
        try:
            legend = self.response.xpath(self.loc_offer.trading_num_loc).get()
            if legend:
                legend = BS(str(legend), features="lxml").get_text()
                legend = "".join(re.findall(r"\d+", legend))
                return legend
        except Exception as e:
            logger.warning(
                f"{self.response.url} :: ERROR TRADING NUMBER\n{e}", exc_info=True
            )
        return None

    def get_lot_link(self, lot_number: str, _data_origin) -> str or None:
        try:
            legend = self.response.xpath(self.loc_offer.lot_table).get()
            if legend:
                legend = BS(str(legend), features="lxml")
                table = legend.find(
                    "legend", string="Лоты публичного предложения"
                ).parent
                # choose type of trade
                if table and len(table) > 0:
                    link = table.find("a", string=lot_number)
                    if link:
                        link = link.get("href")
                        return URL.url_join(_data_origin, link)
        except Exception as e:
            logger.warning(
                f"{self.response.url} :{e}: INVALID DATA LOT TABLE", exc_info=True
            )
        return None

    @property
    def property_information(self):
        property_info = self.response.xpath(self.loc_offer.property_info_loc).get()
        if property_info:
            property_info = dedent_func(
                BS(str(property_info), features="lxml").get_text()
            )
            return property_info.strip()
        return None

    @property
    def msg_number(self):
        msg = self.response.xpath(self.loc_offer.msg_number_loc).get()
        if msg:
            msg = BS(str(msg), features="lxml").get_text()
            return " ".join(re.findall(r"\d{6,8}", dedent_func(msg)))
        return None

    @property
    def trading_form(self):
        try:
            form = (
                    self.response.xpath(self.loc_offer.trading_form_loc).get()
                    or self.response.xpath(self.loc_offer.trading_form_loc_2).get()
            )
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

    def get_period_table(self):
        try:
            table = self.response.xpath(self.loc_offer.period_table_loc).get()
            table = BS(str(table), features="lxml")
            table = pd.read_html(str(table).replace(",", "."))
            return table[0]
        except Exception as e:
            logger.warning(
                f"{self.response.url} :: PERIOD TABLE NOT FOUND {e}", exc_info=True
            )
        return None

    @property
    def periods(self):
        try:
            period_lst = list()
            periods = self.get_period_table()
            col = periods.columns
            for p in range(len(periods) - 1):
                try:
                    start = periods.iloc[p + 1][1]
                    end = periods.iloc[p + 1][2]
                    price = re.sub(r"\s", "", periods.iloc[p + 1][len(col) - 2])
                    price = round(float(price.replace("&nbsp;", "")), 2)

                    period = {
                        "start_date_requests": DateTimeHelper.smart_parse(start).astimezone(DateTimeHelper.moscow_tz),
                        "end_date_requests": DateTimeHelper.smart_parse(end).astimezone(DateTimeHelper.moscow_tz),
                        "end_date_trading": DateTimeHelper.smart_parse(end).astimezone(DateTimeHelper.moscow_tz),
                        "current_price": price,
                    }
                    period_lst.append(period)
                except Exception:
                    continue
            return period_lst
        except Exception as e:
            logger.warning(
                f"{self.response.url} :: INVALID DARA PERIOD TABLE\n{e}", exc_info=True
            )
        return None

    @property
    def start_date_requests(self):
        try:
            start = DateTimeHelper.smart_parse(self.get_period_table().iloc[1][1]).astimezone(DateTimeHelper.moscow_tz)
            return start
        except Exception as e:
            logger.warning(
                f"{self.response.url} :: INVALID DATA start date request offer\n{e}"
            )
        return None

    @property
    def end_date_requests(self):
        try:
            end = DateTimeHelper.smart_parse(self.get_period_table().iloc[-1][2]).astimezone(DateTimeHelper.moscow_tz)
            return end
        except Exception as e:
            logger.warning(
                f"{self.response.url} :: INVALID DATA start date request offer\n{e}"
            )
        return None

    @property
    def start_date_trading(self):
        return self.start_date_requests

    @property
    def end_date_trading(self):
        return self.end_date_requests

    @property
    def start_price(self):
        try:
            periods = self.get_period_table()
            col = periods.columns
            price = re.sub(r"\s", "", periods.iloc[1][len(col) - 2])
            return round(float(price), 2)
        except Exception as e:
            logger.warning(
                f"{self.response.url} :: INVALID DATA START PRICE offer\n{e}"
            )
        return None

    def download(self, crawler_name: str):
        files = list()
        for d in self.response.xpath(self.loc_offer.documents).getall():
            d = BS(str(d), features="lxml")
            a = d.find("a")
            link_etp = URL.url_join(data_origin[crawler_name], a.get("href")[1:])
            file_name = a.get_text()
            files.append(
                DownloadData(
                    url=link_etp,
                    file_name=file_name,
                    referer=self.response.url,
                    verify=False if crawler_name in ["etpu", "meta_invest", "arbbitlot"] else True,
                )
            )
        return files

    def find_error_page(self):
        error_text = "В приложении произошла ошибка"
        if error_text in self.response.text:
            logger.warning(f"{self.response.url} :: НЕВОЗМОЖНО ОТОБРАЗИТЬ СТРАНИЦУ")
        return None
