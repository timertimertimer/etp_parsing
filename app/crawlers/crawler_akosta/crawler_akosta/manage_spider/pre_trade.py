import re
import math

from bs4 import BeautifulSoup as BS

from app.crawlers.crawler_akosta.crawler_akosta.locators.pre_trade_page_locator import (
    SearchLocator,
)
from app.crawlers.crawler_akosta.crawler_akosta.utils.config import data_origin
from app.utils import dedent_func, format_time_period, URL, logger


class PreTradePage:
    def __init__(self, _response, soup):
        self.response = _response
        self.soup = soup
        self.loc = SearchLocator

    @property
    def get_link_to_serp_trade(self):
        try:
            section_with_link = self.response.xpath(
                self.loc.link_to_serp_trades_loc
            ).get()
            if section_with_link:
                link = BS(str(section_with_link), features="lxml").find("a")
                if link:
                    link = re.sub(r"^.", "", link.get("href"))
                    return URL.url_join(data_origin[:-1], link)
        except Exception as e:
            logger.warning(
                f"{self.response.url} | ERROR GETTING LINK TO TRADING LOTS OF AKOSTA\n{e}"
            )
            with open("main_link_to_trades_ERROR.txt", "w") as f:
                f.write(self.response.text)
        return None

    def get_post_data_values(self, tag_html: str, post_argument: str) -> str or None:
        try:
            tag_html = self.soup.find(tag_html, id=post_argument)
            if tag_html:
                return tag_html["value"]
        except Exception as e:
            logger.warning(f"{self.response.url} | Error during fetching tag {tag_html} | {e} ")
        return None

    @property
    def get_total_and_current_page(self) -> tuple or None:
        try:
            span = self.soup.find("span", class_="ui-paginator-current").get_text()
            logger.info(f'THIS IS SPAN "PRE_TRADE" {span}')
            pattern = re.compile(r"\d+\/\d+")
            p = pattern.findall(span)
            current_page = "".join(p).split("/")[0]
            total_page = "".join(p).split("/")[1]
            return int(current_page), int(total_page)
        except Exception as e:
            logger.warning(
                f'{self.response.url} |{e}|\n page download with error -> error file name "pagination_error.txt" '
            )
            with open("pagination_error.html", "w") as f:
                f.write(self.response.text)
        return None

    def get_trade_links(self):
        try:
            links_div = self.soup.find("div", id="formMain:lotListTable")
            links = links_div.find_all("tr", attrs={"data-ri": re.compile(r"\d+")})
            return links
        except Exception as e:
            logger.warning(
                f"{self.response.url} |{e}| DURING GETTING LINKS TO TRADE PAGES OCCURE ERROR(1)",
                exc_info=True,
            )
            with open("getting_links_to_trading_page.html", "w") as f:
                f.write(self.response.text)
        return None

    def get_id_a_trade(self):
        try:
            lst_with_id = list()
            for tr in self.get_trade_links():
                soup_ = BS(str(tr), features="lxml")
                _id = soup_.find("a").get("id")
                if _id:
                    lst_with_id.append(_id)
            return lst_with_id
        except Exception as e:
            logger.warning(
                f"{self.response.url} :{e}: ERROR GETTING FORM DATA LIKE A LINK"
            )
            with open("error_form_data_link.html", "w") as f:
                f.write(self.response.text)
        return None

    def get_post_id_and_trading_id(self, tr):
        try:
            soup_ = BS(str(tr), features="lxml")
            link_to_trade = soup_.find("a")
            _id = link_to_trade.get("id")
            if _id:
                return _id, link_to_trade.get_text().strip()
            logger.warning(f"{self.response.url} | EMPTY  DATA LINK TO TRADE")
        except Exception as e:
            logger.warning(
                f"{self.response.url} :{e}: ERROR GETTING FORM DATA LIKE A LINK"
            )
            with open("error_form_data_link.html", "w") as f:
                f.write(self.response.text)
        return None

    def get_only_one_needed_id(self, trade):
        try:
            all_id = self.get_id_a_trade()
            lst_temp = list()
            lst_id_number = list()
            for i in all_id:
                number = self.soup.find("a", id=i)
                if number:
                    number = dedent_func(number.get_text().strip())
                    if trade in number:
                        lst_temp.append(number)
                        lst_id_number.append((number, i))
            set_trading_number = set(lst_temp)
            if 0 <= len(set_trading_number) <= 1:
                _id = "".join(lst_id_number[0][1])
                return [(_id, trade)]
            else:
                num = list()
                _id = list()
                for i in list(lst_id_number):
                    date = self.check_start_date_requet(i[0])
                    if len(date) > 0:
                        if date[0] > "2019-12-31 23:59:59":
                            if i[0] not in num:
                                num.append(i[0])
                                _id.append(i[1])
                total = list(zip(_id, num))
            return total
        except Exception as e:
            logger.warning(f"{e}", exc_info=True)
        return None

    def check_start_date_requet(self, text):
        out_put_list = list()
        dates = self.response.xpath(self.loc.start_date_request.format(text)).getall()
        for d in dates:
            out_put_list.append(format_time_period(d))
        return out_put_list

    def get_trading_number(self, page_number):
        try:
            _id = self.get_id_a_trade()
            trading = self.response.xpath(self.loc.trading_number_loc.format(_id)).get()
            tra = BS(str(trading), features="lxml").get_text()
            return dedent_func(tra.strip())
        except Exception as ex:
            logger.critical(f"ON PAGE - {page_number} | ERROR GETTING TRADING ID {ex}")
        return None

    def get_trading_number_1(self, _id, page_number):
        try:
            # _id = self.get_id_a_trade_1(tr)
            trading = self.response.xpath(
                self.loc.trading_number_loc.format(_id[0])
            ).get()
            tra = BS(str(trading), features="lxml").get_text()
            return dedent_func(tra.strip())
        except Exception as ex:
            logger.critical(f"ON PAGE - {page_number} | ERROR GETTING TRADING ID {ex}")
        return None

    def get_view_after_first_page(self, html):
        try:
            string = str(html).replace("&lt;", "<").replace("&gt;", ">")
            pattern = re.compile(
                r'<update id="j_id1:javax.faces.ViewState:0"><!\[CDATA\[(.*)\]\]></update>'
            )
            res = pattern.findall(string)[0]
            if res:
                if len(res) > 0:
                    res = str(res).replace("]]><![CDATA[le", "")
                    return res
        except Exception:
            logger.warning(
                f"{self.response.url} | INVALID DATA VIEWSTATE (when page >= 2",
                exc_info=True,
            )
        return None

    def get_trade_links_2(self):
        sources = dict()
        for el in self.soup.find_all("a", id=lambda x: x and "j_idt" in x):
            sources[dedent_func(el.text)] = el.get("id")
        return sources

    def count_total_pages(self, html):
        try:
            string = str(html).replace("&lt;", "<").replace("&gt;", ">")
            pattern = re.compile('type="args">{"totalRecords":(.*)}</extension>')
            res = "".join([x for x in pattern.findall(string)[0] if x.isdigit()])
            try:
                res = int(res)
                number_of_pages = math.ceil(int(res) / 50)
                return number_of_pages
            except Exception:
                res = None
                logger.warning(f"{self.response.url} | total pages not int")
                return res
        except Exception:
            logger.warning(
                f"{self.response.url} | INVALID DATA VIEWSTATE (when page >= 2",
                exc_info=True,
            )
        return None