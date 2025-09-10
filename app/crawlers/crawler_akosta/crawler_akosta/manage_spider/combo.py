import re

from app.utils import URL, logger
from app.db.models import DownloadData
from .pre_trade import PreTradePage
from .general_info_page import MainTradingPage
from .trade_page_with_tabs import TradePage
from .debtor_tab_page import DebtorTab
from .lot_auction_page import LotAuctionPage
from .lot_offer_page import LotOfferPage
from bs4 import BeautifulSoup as BS

from ..utils.config import data_origin


class Combo:
    def __init__(self, _response):
        self.response = _response
        self.soup = BS(
            str(self.response.body.decode("utf-8"))
            .replace("&lt;", "<")
            .replace("&gt;", ">"),
            features="lxml",  # DO NOT CHANGE TO XML
        )
        self.pre = PreTradePage(self.response, self.soup)
        self.main_ = MainTradingPage(self.response, self.soup)
        self.trade = TradePage(self.response, self.soup)
        self.deb = DebtorTab(self.response, self.soup)
        self.auc = LotAuctionPage(self.response, self.soup)
        self.offer = LotOfferPage(self.response, self.soup)

    @property
    def start_price(self) -> float | None:
        try:
            start_price = self.soup.find(
                "label", string=re.compile("Начальная стоимость:", re.IGNORECASE)
            )
            start_price = start_price.parent
            start_price = (
                start_price.get_text()
                .strip()
                .split(":", maxsplit=1)[-1]
                .strip()
                .replace(",", ".")
            )
            p = "".join([p for p in start_price if p.isdigit() or p == "."])
            p = re.sub(r"\.$", "", p).strip()
            if len(p) > 0:
                return round(float(p), 2)
        except Exception as e:
            logger.warning(
                f"{self.response.url} | Couldn't parse start price. Error: {e}"
            )
        return None

    @property
    def step_price(self) -> float | None:
        try:
            step_price = self.soup.find(
                "label", string=re.compile("Шаг аукциона:?", re.IGNORECASE)
            )
            if step_price:
                step_price = step_price.next_sibling
                p = "".join([p for p in step_price if p.isdigit() or p == "."])
                p = re.sub(r"\.$", "", p).strip()
                if len(p) > 0:
                    return round(float(p), 2)
        except Exception as e:
            logger.warning(
                f"{self.response.url} | Couldn't parse step price. Error: {e}"
            )
        return None

    @property
    def categories(self):
        try:
            category = self.soup.find(
                "label",
                string=re.compile("Классификатор товара, работ, услуг:", re.IGNORECASE),
            )
            if category:
                category = category.next_sibling.text
                return [category.split("/")[-1].strip()]
        except Exception as e:
            logger.warning(
                f"{self.response.url} | Couldn't parse categories. Error: {e}"
            )
        return None

    def get_lot_images(self):
        if not (gallery := self.soup.find("div", id="formMain:idGallery")):
            return None
        return gallery.find_all("img")

    def download_lot(self):
        files = list()
        if not (images := self.get_lot_images()):
            return None
        for i, t in enumerate(images):
            name = t.get("title")
            url = URL.url_join(data_origin, t.get("src"))
            files.append(DownloadData(url=url, file_name=name, verify=False, is_image=True, order=i))
        return files
