import logging
import re

from general_utils import UrlConfig
from general_utils.models import DownloadData
from .pre_trade import PreTradePage
from .general_info_page import MainTradingPage
from .trade_page_with_tabs import TradePage
from .debtor_tab_page import DebrorTab
from .lot_auction_page import LotAuctionPage
from .lot_offer_page import LotOfferPage
from bs4 import BeautifulSoup as BS

from ..utils.config import data_origin

logger = logging.getLogger(__name__)


class Combo:

    def __init__(self, _response):
        self.response = _response
        self.soup = BS(
            str(self.response.body.decode('utf-8')).replace('&lt;', '<').replace('&gt;', '>'),
            features='lxml'  # DO NOT CHANGE TO XML
        )
        self.pre = PreTradePage(self.response, self.soup)
        self.main_ = MainTradingPage(self.response, self.soup)
        self.trade = TradePage(self.response, self.soup)
        self.deb = DebrorTab(self.response, self.soup)
        self.auc = LotAuctionPage(self.response, self.soup)
        self.offer = LotOfferPage(self.response, self.soup)

    @property
    def start_price(self) -> float | None:
        try:
            start_price = self.soup.find('label', string=re.compile('Начальная стоимость:', re.IGNORECASE))
            start_price = start_price.parent
            start_price = start_price.get_text().strip().split(':', maxsplit=1)[-1].strip().replace(',', '.')
            p = ''.join([p for p in start_price if p.isdigit() or p == '.'])
            p = re.sub(r'\.$', '', p).strip()
            if len(p) > 0:
                return round(float(p), 2)
        except Exception as e:
            logger.error(f'{self.response.url} :: ERROR START PRICE {e}')

    @property
    def step_price(self) -> float | None:
        try:
            step_price = self.soup.find('label', string=re.compile('Шаг аукциона:?', re.IGNORECASE))
            if step_price:
                step_price = step_price.next_sibling
                p = ''.join([p for p in step_price if p.isdigit() or p == '.'])
                p = re.sub(r'\.$', '', p).strip()
                if len(p) > 0:
                    return round(float(p), 2)
        except Exception as e:
            logger.error(f'{self.response.url} :: ERROR STEP PRICE {e}')

    @property
    def categories(self):
        try:
            category = self.soup.find('label', string=re.compile('Классификатор товара, работ, услуг:', re.IGNORECASE))
            if category:
                category = category.next_sibling.text
                return [category.split('/')[-1].strip()]
        except Exception as e:
            logger.error(f'{self.response.url} :: ERROR CATEGORY {e}')

    def get_lot_images(self):
        gallery = self.soup.find('div', id='formMain:idGallery')
        if not gallery:
            return
        return gallery.find_all('img')

    def download_lot(self):
        # load = DownloadFiles()
        files = list()
        # files_dir = FilesDir(relative_path, absolute_path)
        images = self.get_lot_images()
        if not images:
            return
        for t in images:
            name = t.get('title')
            url = UrlConfig.url_join(data_origin, t.get('src'))
            # if len(name) > 75:
            #     name = name[:30] + '_' + name[-35::1]
            # name_on_server = files_dir.name_file_on_server(trading_id=trading_id, lot_number=lot_number, original_name=name)
            # files_dir.create_dir()
            # path_absolute = files_dir.return_absolute_path(name_on_server)
            # path_relative = files_dir.return_relative_path(name_on_server)
            files.append(DownloadData(url=url, file_name=name, verify=False))
            # load.request_to_download_general(
            #     request_data=request_data,
            #     absolute_path=path_absolute,
            #     relative_path=path_relative,
            #     trading_id=trading_id,
            # )
            # files.append({
            #     'original_name': name,
            #     'link': files_dir.return_relative_path(name_on_server).as_posix(),
            #     'link_etp': url
            # })
        return files

