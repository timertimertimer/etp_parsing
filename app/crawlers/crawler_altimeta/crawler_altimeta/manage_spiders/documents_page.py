import pathlib
from bs4 import BeautifulSoup as BS

from app.utils import dedent_func, URL
from app.utils.config import allowable_formats
from app.db.models import DownloadData
from ..config import data_origin
from ..locators.locators_trade_page import LocatorTradePage


class DocPage:
    def __init__(self, response_):
        self.response = response_
        self.soup = BS(
            str(self.response.text).replace("&lt;", "<").replace("&gt;", ">"),
            features="lxml",
        )
        self.loc_trade = LocatorTradePage

    def get_all_doc_files(self):
        """get all  tags <a> and return list of this tag"""
        docs = self.response.xpath(self.loc_trade.files_data_loc).getall()
        return docs

    def general_docs(self, crawler_name: str) -> list[DownloadData]:
        docs = self.get_all_doc_files()
        return self.get_files(docs, data_origin[crawler_name])

    def get_lot_docs(self, table_, crawler_name: str) -> list[DownloadData]:
        soup = BS(str(table_), features="lxml")
        all_docs = soup.find_all("a")
        return self.get_files(all_docs, data_origin[crawler_name])

    def get_files(self, docs: list | None, host: str) -> list[DownloadData]:
        files = list()
        if not docs:
            return files
        for d in docs:
            d = BS(str(d), features="lxml")
            a = d.find("a")
            link_etp = a.get("href")
            link_etp = URL.url_join(host, link_etp)
            file_name = dedent_func(a.get_text().replace(". ", "."))
            if pathlib.Path(file_name).suffix.lower() in allowable_formats:
                files.append(
                    DownloadData(
                        url=link_etp, file_name=file_name, referer=self.response.url
                    )
                )
        return files
