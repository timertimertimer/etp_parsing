from general_utils import headers
from ..spiders.base import ItenderBaseSpider


class TendergarantSpider(ItenderBaseSpider):
    name = 'tendergarant'
    custom_settings = {
        # 'LOG_FILE': f'{name}.log',
        'DEFAULT_REQUEST_HEADERS': headers | {'Accept-Encoding': 'gzip, deflate'}
    }
