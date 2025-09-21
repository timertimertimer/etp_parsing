from enum import verify

from app.db.models import DownloadData
from .libraries import *


class Files:
    def __init__(self, response_):
        self.response = response_
        self.soup = soup(self.response)

    def section_docs(self):
        _div = self.soup.find("div", id="divDocuments")
        if _div:
            return _div
        else:
            logger.error(
                f"{self.response.url} :: ERROR function class Files {self.section_docs.__name__}"
            )
            return None

    def find_files(self, data_origin):
        files = list()
        if not (table := self.section_docs()):
            return files
        a_tag = table.find_all(href=re.compile("/Document/.+/.+"))
        for a in a_tag:
            link = a.get("href")
            link = re.sub(r"/$", "", data_origin) + link
            name = dedent_func(a.get_text())
            files.append((name, link))
        if img := self.images_on_page(data_origin):
            files.extend(img)
        return deque(files)

    def images_on_page(self, data_origin: str) -> list:
        images = list()
        _div = self.soup.find("div", class_="links picture-links")
        if not _div:
            return images
        a_tag = _div.find_all(href=re.compile("/Picture/.+/.+"))
        for a in a_tag:
            link = a.get("href")
            link = re.sub(r"/$", "", data_origin) + link
            name = pathlib.Path(str(link)).stem + ".jpg"
            images.append((name, link))
        return images

    def download_files(self, data_origin: str):
        files = list()
        if not (lst := self.find_files(data_origin)):
            return files
        for f in lst:
            name, url = f
            files.append(
                DownloadData(url=url, file_name=name, referer=self.response.url, verify=False)
            )
        return files
