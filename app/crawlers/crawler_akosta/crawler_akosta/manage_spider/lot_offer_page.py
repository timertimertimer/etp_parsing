import re
import unicodedata
from io import StringIO

import pandas as pd
from bs4 import BeautifulSoup as BS

from app.utils import dedent_func, DateTimeHelper, logger


class LotOfferPage:
    def __init__(self, _response, soup):
        self.response = _response
        self.soup = soup

    @property
    def start_price(self):
        try:
            start_price = self.soup.find(
                "label", string=re.compile("Начальная стоимость", re.IGNORECASE)
            ).parent
            start_price = (
                start_price.get_text().strip().split(":", maxsplit=1)[-1].strip()
            )
            start_price = dedent_func(
                unicodedata.normalize("NFKD", start_price)
            ).replace(",", ".")
            start_price = re.sub(
                r".$",
                "",
                "".join(
                    [
                        p
                        for p in re.sub(r"\s", "", start_price)
                        if p.isdigit() or p == "."
                    ]
                ),
            ).strip()
            return start_price
        except Exception as ex:
            logger.warning(
                f"{self.response.url} | INVALID DATA START PRICE OFFER \n {ex}"
            )
        return None

    def return_period_pagination(self):
        try:
            pag = self.soup.find("span", class_="ui-paginator-current").get_text()
            n1 = "".join(re.findall(r"of.+", pag))
            n1 = "".join([x for x in n1 if x.isdigit()])
            if re.match(r"\d+", n1):
                return int(n1)
        except Exception as e:
            logger.warning(f"{self.response} | ERROR RETURN NUMBER OF PAGES  {e}")
        return None

    def get_period_table(self):
        try:
            thead = self.soup.find("thead", id="formMain:dataRSList_head").parent
            if thead:
                thead.thead.decompose()
                html_content = re.sub(r",", ".", str(thead))
                table = pd.read_html(StringIO(html_content), header=None)
                if table:
                    return table[0]
        except Exception as e:
            logger.warning(f"{self.response.url} | INVALID DATA PERIOD TABLE {e}")
        return None

    def get_start_date_request(self, lst_period: list):
        try:
            last_element: dict = lst_period[0]
            return last_element["start_date_requests"]
        except Exception as e:
            logger.warning(f"{self.response.url} | ERROR END DATE TRADING {e}")
        return None

    def get_end_date_request(self, lst_period: list):
        try:
            last_element: dict = lst_period[-1]
            return last_element["end_date_requests"]
        except Exception as e:
            logger.warning(f"{self.response.url} | ERROR END DATE TRADING {e}")
        return None

    @property
    def periods(self):
        check_value = 10000000000000000000000
        periods = list()
        tbody_periods = self.get_period_table()
        for p in range(len(tbody_periods)):
            start = tbody_periods.iloc[p][0]
            end = tbody_periods.iloc[p][1]
            price_ = tbody_periods.iloc[p][2]
            price_ = re.sub(r"Руб.?", "", price_, re.IGNORECASE)
            try:
                if isinstance(price_, str):
                    price = "".join(re.sub(r"\s", "", price_)).replace(",", ".")
                    price = round(float(price), 2)
                else:
                    price = round(float(price_), 2)
                if check_value < price:
                    logger.critical(
                        f"{self.response.url} | INVALID PRICE ON PERIOD - CURRENT PRICE HIGHER THAN PREVIUOS"
                    )
                else:
                    check_value = price
            except Exception:
                logger.warning(
                    f"{self.response.url} Period Price - {price_} typeof - {type(price_)}"
                )
                return None
            try:
                period = {
                    "start_date_requests": DateTimeHelper.smart_parse(start).astimezone(DateTimeHelper.moscow_tz),
                    "end_date_requests": DateTimeHelper.smart_parse(end).astimezone(DateTimeHelper.moscow_tz),
                    "end_date_trading": DateTimeHelper.smart_parse(end).astimezone(DateTimeHelper.moscow_tz),
                    "current_price": price,
                }
                periods.append(period)
            except Exception:
                continue
        return periods

    def return_next_periods(self):
        periods = list()
        soup = BS(str(self.response.text), "html.parser")
        soup_new = BS(dedent_func(soup.get_text()), "lxml")
        for tr in soup_new.find_all("tr"):
            td = tr.find_all("td")
            start = td[0].get_text()
            end = td[1].get_text()
            price_ = td[2].get_text()
            price_ = re.sub(r"Руб.?", "", price_, re.IGNORECASE)
            price = "".join(re.sub(r"\s", "", price_)).replace(",", ".")
            price = round(float(price), 2)
            try:
                period = {
                    "start_date_requests": DateTimeHelper.smart_parse(start).astimezone(DateTimeHelper.moscow_tz),
                    "end_date_requests": DateTimeHelper.smart_parse(end).astimezone(DateTimeHelper.moscow_tz),
                    "end_date_trading": DateTimeHelper.smart_parse(end).astimezone(DateTimeHelper.moscow_tz),
                    "current_price": price,
                }
                periods.append(period)
            except Exception:
                continue
        return periods

    def get_refresh_form_j_idt55(self):
        try:
            tag_html = self.soup.find("div", id="formMain:opRefreshStatus_content")
            if tag_html:
                _value = tag_html.find(attrs={"name": "formMain:j_idt55"})
                if _value:
                    _value = _value["value"]
                return str(_value)
            else:
                return None
        except Exception as ex:
            logger.warning(f"{self.response.url} | ERROR FORM j_idt55, {ex}")
        return None
