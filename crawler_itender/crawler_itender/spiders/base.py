import logging
from scrapy import Request
from general_utils.base_spider import BaseSpider
from ..utils.config import return_auction_link, data_origin, return_offer_link, return_compet_link

logger = logging.getLogger(__name__)


class ItenderBaseSpider(BaseSpider):
    name = 'base'
    custom_settings = {
        # 'LOG_FILE': f'{name}.log',
    }

    @classmethod
    def set_links(cls):
        cls.data_origin = data_origin.get(cls.name)

    def __init__(self):
        self.set_links()
        super(ItenderBaseSpider, self).__init__(self.data_origin)

    def start_requests(self):
        yield Request(self.data_origin, self.choose_datatype)

    def choose_datatype(self, response):
        for _type in ['auction', 'offer', 'competition']:
            if _type == 'auction':
                yield Request(return_auction_link(self.data_origin), self.parse_, cb_kwargs={'_type': 'auction'})
            if _type == 'offer':
                yield Request(return_offer_link(self.data_origin), self.parse_, cb_kwargs={'_type': 'offer'})
            if _type == 'competition':
                yield Request(return_compet_link(self.data_origin), self.parse_, cb_kwargs={'_type': 'competition'})

    def parse_(self, response, _type: str):
        ...