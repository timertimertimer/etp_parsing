from .search import SearchData
from .lot_page import LotPage
from .download_spider import DownloadSpider


class Combo:

    def __init__(self, response_):
        self.response = response_
        self.search = SearchData(self.response)
        self.lot = LotPage(self.response)
        self.downspider = DownloadSpider(self.response)