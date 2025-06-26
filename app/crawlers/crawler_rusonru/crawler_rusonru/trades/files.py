import logging
from bs4 import BeautifulSoup as BS

from general_utils import dedent_func
from general_utils.config import allowable_formats
from general_utils.models import DownloadData
from ..locators.locators_doc import LocatorDoc

logger = logging.getLogger(__name__)


class DocumentGeneral:
    def __init__(self, resposne_):
        self.response = resposne_
        self.soup = BS(
            str(self.response.body.decode("utf-8"))
            .replace("&lt;", "<")
            .replace("&gt;", ">"),
            features="lxml",
        )

    def get_doc_table(self):
        try:
            table_doc = self.response.xpath(LocatorDoc.document_general_loc).get()
            if table_doc:
                table_doc = BS(str(table_doc), features="lxml")
                return table_doc
        except Exception as ex:
            logger.error(
                f"{self.response.url} :: DURRING GETTING DOC TABLE ERROR HAD BEEN APEARED {ex}"
            )

    def get_name_links_doc_gen(self) -> list:
        block = self.get_doc_table()
        lst_docs = list()
        if block:
            all_a = block.find_all("a")
            for a in all_a:
                original_name = dedent_func(a.get_text().strip().replace(". ", "."))
                link_file = a.get("href")
                lst_docs.append((original_name, link_file))
            return lst_docs
        else:
            return list()

    def download_general(self):
        files = list()
        for d in self.get_name_links_doc_gen():
            name, link = d
            files.append(
                DownloadData(url=link, file_name=name, referer=self.response.url)
            )
        return files


class DocumentLot:
    def __init__(self, response):
        self.response = response
        self.soup = BS(
            str(self.response.body.decode("utf-8"))
            .replace("&lt;", "<")
            .replace("&gt;", ">"),
            features="lxml",
        )

    def get_lot_files(self, table: str):
        try:
            if table:
                soup = BS(str(table), features="lxml")
                files = soup.find_all("a", class_="file_link")
                if len(files) > 0:
                    lst_links = list()
                    for f in files:
                        lst_links.append((f.get_text(), f.get("href")))
                    return lst_links
                else:
                    return list()
        except Exception as ex:
            logger.error(
                f"{self.response.url} :: INVALID DATA get_lot_files {ex}", exc_info=True
            )
            return list()

    def download_lot_files(self, table):
        files = list()
        for d in self.get_lot_files(table):
            name, link = d
            file_type = link.split(".")[-1]
            if f".{file_type}" in allowable_formats:
                name = f"{name}.{file_type}" if f".{file_type}" not in name else name
            files.append(
                DownloadData(url=link, file_name=name, referer=self.response.url)
            )
        return files
