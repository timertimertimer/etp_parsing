from ..spiders.base import ItenderBaseSpider


class Ets24Spider(ItenderBaseSpider):
    name = "ets24"
    custom_settings = {
        # 'LOG_FILE': f'{name}.log',
    }
