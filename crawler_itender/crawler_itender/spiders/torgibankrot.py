from ..spiders.base import ItenderBaseSpider


class TorgibankrotSpider(ItenderBaseSpider):
    name = 'torgibankrot'
    custom_settings = {
        # 'LOG_FILE': f'{name}.log',
    }