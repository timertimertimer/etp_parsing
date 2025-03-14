from .base import TenderstandartBaseSpider


class TorggroupSpider(TenderstandartBaseSpider):
    name = "torggroup"
    custom_settings = {
        # 'LOG_FILE': f'{name}.log'
    }
