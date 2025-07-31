import re

from bs4 import BeautifulSoup as BS

from app.utils import URL, logger
from ..locators.serp_locator import LocatorSerp


class SerpPageSearchInfo:
    def __init__(self, _response):
        self.response = _response
        self.loc = LocatorSerp
        self.soup = BS(
            str(self.response.body.decode("utf-8"))
            .replace("&lt;", "<")
            .replace("&gt;", ">"),
            features="lxml",
        )

    def fetch_pagination_links(self):
        try:
            set_link = set()
            _a = self.response.xpath(self.loc.pager_href).getall()
            for a in _a:
                set_link.add(a)
            return sorted(list(set_link))
        except Exception:
            pass

    def fetch_pagination_links_lot_page(self):
        try:
            set_link = set()
            _a = self.response.xpath(self.loc.pager_lot_page).getall()
            for a in _a:
                set_link.add(a)
            return sorted(list(set_link))
        except Exception:
            pass

    def get_href_post(self):
        try:
            lst_num_page = list()
            lst_href = list()
            for a in self.fetch_pagination_links():
                a = BS(str(a), features="lxml").find("a")
                if a:
                    a_href = "".join(
                        re.findall(r"ctl.*\d", URL.unquote_url(a.get("href")))
                    )
                    a_text = a.get_text()
                    lst_href.append(str(a_href))
                    lst_num_page.append(a_text)
            return lst_href, lst_num_page
        except Exception as e:
            logger.warning(f"{self.response.url} :: ")
            return []

    def get_href_post_lot_page(self):
        try:
            lst_num_page = list()
            lst_href = list()
            for a in self.fetch_pagination_links_lot_page():
                a = BS(str(a), features="lxml").find("a")
                if a:
                    a_href = "".join(
                        re.findall(r"ctl.*\d", URL.unquote_url(a.get("href")))
                    )
                    a_text = a.get_text()
                    lst_href.append(str(a_href))
                    lst_num_page.append(a_text)
                    if len(lst_href) > 0:
                        return lst_href, lst_num_page
        except Exception as e:
            logger.warning(f"{self.response.url} :: ")
            return []
        return None

    def get_current_page(self):
        try:
            number = self.soup.find("td", class_="pager")
            if number:
                number = number.find_all("span", string=re.compile(r"\d"))
                if len(number) == 1:
                    number = BS(str(number[0]), features="lxml").get_text()
                    if number.isdigit():
                        return number
                    else:
                        logger.warning("NOT A NUMBER")
                        return None
            else:
                number = "1"
                return number
        except Exception as e:
            logger.warning(
                f"{self.response.url} :: ERROR CURRENT PAGE\n{e}", exc_info=True
            )
            with open("error_current_page.txt", "w") as f:
                f.write(self.response.text)
        return None

    def get_next_page(self):
        try:
            next_page = self.soup.find("td", class_="pager")
            if next_page:
                next_page = next_page.find(
                    "span", string=self.get_current_page()
                ).findNext("a")
                if next_page:
                    next_page = next_page.get_text()
                    if next_page and (next_page.isdigit() or next_page == ">>"):
                        if next_page == ">>":
                            next_page = int(self.get_current_page()) + 1
                        return next_page
                else:
                    return 0
            else:
                return 0
        except Exception as e:
            logger.warning(f"{self.response.url}\n{e} ::: get_next_page", exc_info=True)
            with open("error_next_page.txt", "w") as f:
                f.write(self.response.text)
        return None

    def get_previous_page(self):
        try:
            previous = self.soup.find("td", class_="pager")
            if previous:
                previous = previous.find(
                    "span", string=self.get_current_page()
                ).findPrevious("a")
                if previous:
                    previous = previous.get_text()
                    if previous and (previous.isdigit()):
                        return previous
                else:
                    return 0
            else:
                return 0
        except Exception as e:
            logger.warning(
                f"{self.response.url}\n{e} ::: get_previous_page", exc_info=True
            )
            with open("error_previous_page.txt", "w") as f:
                f.write(self.response.text)
        return None

    def body_scripts(self):
        try:
            next_page = self.soup.find("td", class_="pager")
            if next_page:
                next_page = next_page.find(
                    "span", string=self.get_current_page()
                ).findNext("a")
                if next_page:
                    next_page = next_page.get_text()
                a = self.soup.find("td", class_="pager").findChild(
                    "a", string=next_page
                )
                if a:
                    a_href = "".join(re.findall(r"ctl.*\d", a.get("href")))
                    return a_href
        except Exception as e:
            logger.warning(f"{self.response.url}\n{e} :: body_script", exc_info=True)
            with open("body_scripts.txt", "w") as f:
                f.write(self.response.text)
        return None

    def body_scripts_1st_page(self):
        try:
            td = self.soup.find("td", class_="pager")
            if td:
                first_page = td.find("a")
                if first_page:
                    first_page_text = first_page.get_text()
                    if first_page_text == "1":
                        a = first_page.get("href")
                        a_href = "".join(re.findall(r"ctl.*\d", a))
                        return a_href
        except Exception as e:
            logger.warning(
                f"{self.response.url}\n{e} :: body_scripts_1st_page", exc_info=True
            )
            with open("body_scripts_1st_page.txt", "w") as f:
                f.write(self.response.text)
        return None

    def get_tr_lot_data_serp(self):
        try:
            lst_data_links = self.soup.find_all("tr", class_="gridRow")
            if len(lst_data_links) > 0:
                return lst_data_links
        except Exception as e:
            logger.warning(f"{self.response}\n{e}", exc_info=True)
        return None

    def get_max_page_pagination(self) -> str or None:
        try:
            num = self.response.xpath(self.loc.max_page_number_loc).get()
            if num:
                if len(num) == 1:
                    return num.strip()
            return None
        except Exception:
            return None

    def get_link_to_lot(self, current_page, data_origin) -> list or None:
        try:
            lst_link_lot = list()
            if self.get_tr_lot_data_serp():
                for tr in self.get_tr_lot_data_serp():
                    link = BS(str(tr), features="lxml").find_all("td")[0].find("a")
                    if link:
                        link = link.get("href")
                        if link:
                            link = URL.url_join(data_origin, link)
                    lot_ = BS(str(tr), features="lxml").find_all("td")[2].find("a")
                    if lot_:
                        lot = lot_.get_text()
                        lot_link = lot_.get("href")
                        if lot.isdigit():
                            lot = lot
                        else:
                            logger.warning(
                                f"{link} :: current page {current_page} :: WITHOUT LOT NUMBER"
                            )
                            return list()
                        lst_link_lot.append(
                            (link, lot, URL.url_join(data_origin, lot_link))
                        )
                return lst_link_lot
            else:
                return list()
        except Exception as e:
            logger.warning(
                f"{self.response.url}:: get_link_to_lot:::{e}", exc_info=True
            )
            return list()

    def find_error_page(self):
        error_text = "В приложении произошла ошибка"
        if error_text in self.response.text:
            return f"{self.response.url} :: НЕВОЗМОЖНО ОТОБРАЗИТЬ СТРАНИЦУ"
        return None
