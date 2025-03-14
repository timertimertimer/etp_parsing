from .base import TenderstandartBaseSpider


class AuProSpider(TenderstandartBaseSpider):
    name = "au_pro"
    custom_settings = {
        # 'LOG_FILE': f'{name}.log'
    }
