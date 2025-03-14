from .base import TenderstandartBaseSpider


class ViomitraSpider(TenderstandartBaseSpider):
    name = "viomitra"
    custom_settings = {
        # 'LOG_FILE': f'{name}.log'
    }
