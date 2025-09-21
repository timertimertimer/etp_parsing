import re

from bs4 import BeautifulSoup as BS

from app.utils import dedent_func, URL, logger, DateTimeHelper
from app.db.models import DownloadData
from ..config import trade_page_file
from ..locators_and_attributes.locators_attributes import Auction


class AuctionSpider:
    def __init__(self, response):
        self.response = response
        self.soup = BS(
            str(self.response.body.decode("utf-8"))
            .replace("&lt;", "<")
            .replace("&gt;", ">"),
            features="lxml",
        )

    @property
    def trading_type(self):
        trading_type = self.response.xpath(Auction.trading_type_loc).get()
        if trading_type and len(trading_type) > 0:
            type_ = dedent_func(
                BS(str(trading_type), features="lxml").get_text()
            ).strip()
            if type_ in [
                "Аукцион",
                "Открытый аукцион",
                "Закрытый аукцион",
                "Конкурс",
                "Открытый конкурс",
                "Закрытый конкурс",
            ]:
                return "auction"
            else:
                logger.warning(f"{self.response.url} :: INVALID DATA TRADING TYPE")
        return None

    @property
    def start_date_requests(self):
        try:
            s = self.soup.find(id=Auction.start_date_req_loc)
            if s:
                date = dedent_func(s.get_text())
                return DateTimeHelper.smart_parse(date).astimezone(DateTimeHelper.moscow_tz)
        except Exception as e:
            logger.error(
                f"{self.response.url} :: INVAID DATA START DATE REQUST AUCTION"
            )
        return None

    @property
    def end_date_requests(self):
        try:
            e = self.soup.find(id=Auction.end_date_req_loc)
            if e:
                date = dedent_func(e.get_text())
                return DateTimeHelper.smart_parse(date).astimezone(DateTimeHelper.moscow_tz)
        except Exception as e:
            logger.error(f"{self.response.url} :: INVALID DATA END DATE TRADING")
        return None

    @property
    def start_date_trading(self):
        try:
            st = self.soup.find(id=Auction.start_date_trading)
            if st:
                date = dedent_func(st.get_text())
                return DateTimeHelper.smart_parse(date).astimezone(DateTimeHelper.moscow_tz)
            else:
                st = self.soup.find(id=Auction.extra_start_date_trading)
                if st:
                    date = dedent_func(st.get_text())
                    return DateTimeHelper.smart_parse(date).astimezone(DateTimeHelper.moscow_tz)
        except Exception as e:
            logger.error(f"{self.response.url} :: INVALID DATA START DATE TRADING")
        return None

    @property
    def end_date_trading(self):
        try:
            st = self.soup.find(id=Auction.end_date_trading)
            if st:
                date = dedent_func(st.get_text())
                return DateTimeHelper.smart_parse(date).astimezone(DateTimeHelper.moscow_tz)
        except Exception as e:
            logger.error(f"{self.response.url} :: INVALID DATA END DATE TRADING")
        return None

    @property
    def start_price(self):
        try:
            p = self.soup.find(id=Auction.start_price_auc_loc)
            if p:
                p = re.sub(
                    r"\s", "", dedent_func(p.get_text().strip()).replace(",", ".")
                )
                p = "".join([x for x in p if x.isdigit() or x == "."])
                if len(p) > 0:
                    return round(float(p), 2)
        except ValueError as e:
            logger.error(f"{self.response.url} :: INVALID DATA START PRICE\n{e}")
        return None

    @property
    def step_price(self):
        try:
            p = self.soup.find(id=Auction.step_price_auc_loc)
            if p:
                p = re.sub(
                    r"\s", "", dedent_func(p.get_text().strip()).replace(",", ".")
                )
                p = "".join([x for x in p if x.isdigit() or x == "."])
                if len(p) > 0:
                    return round(float(p), 2)
        except ValueError as e:
            logger.error(f"{self.response.url} :: INVALID DATA STEP PRICE\n{e}")
        return None

    # FILES
    @property
    def list_link_to_file_lot(self):
        try:
            links = self.response.xpath(Auction.to_lot_files_loc).getall()
            if len(links) > 0:
                return links
        except Exception as e:
            logger.error(f"{self.response.url} :: INVALID DATA LINK TO LOT FILE\n{e}")
        return None

    @property
    def clean_files_lot_links(self):
        clean_set = set()
        if self.list_link_to_file_lot:
            for link in self.list_link_to_file_lot:
                try:
                    link = BS(str(link), features="lxml").find("a").get("href")
                    link = URL.parse_url(
                        URL.url_join(trade_page_file, link)
                    )
                    clean_set.add(link)
                except Exception as e:
                    continue
        return clean_set

    def general_file_link_doc_1(self):
        try:
            td = self.response.xpath(Auction.to_dohovor_loc).get()
            if td:
                link = BS(str(td), features="lxml").find("a")
                if link:
                    return URL.parse_url(
                        URL.url_join(trade_page_file, link.get("href"))
                    )
                else:
                    return list()
        except Exception as e:
            logger.error(f"{self.response.url} :: ERROR GETTING GREF TO FILE GENERAL")
        return None

    def general_file_link_doc_2(self):
        try:
            td = self.response.xpath(Auction.to_proekt_loc).get()
            if td:
                link = BS(str(td), features="lxml").find("a")
                if link:
                    return URL.parse_url(
                        URL.url_join(trade_page_file, link.get("href"))
                    )
                else:
                    return list()
        except Exception as e:
            logger.error(
                f"{self.response.url} :: ERROR GETTING GREF TO FILE GENERAL\n{e}"
            )
        return None

    def find_all_files(self, referer):
        link = self.soup.find_all(
            "a", {"href": re.compile(r"undef/card/download.aspx\?fileid.+0")}
        )
        if link:
            return link
        else:
            logger.error(f"{referer} :: ERROR WITH DOCUMENTS", exc_info=True)
            with open("ERROR_doc_page.txt", "w") as f:
                f.write(self.response.text)
        return list()

    @staticmethod
    def download(lst: list) -> list:
        files = list()
        for f in lst:
            file_ = BS(str(f), features="lxml")
            if file_:
                file_ = file_.find("a")
                if file_:
                    file_link = re.sub(r"\s", "", dedent_func(file_.get("href")))
                    file_name = file_.get_text(strip=True)
                    files.append(
                        DownloadData(
                            url=URL.url_join(trade_page_file, file_link),
                            file_name=file_name,
                        )
                    )
        return files
