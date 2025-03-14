from .base import ItenderBaseSpider


class SeltOnlineSpider(ItenderBaseSpider):
    name = 'selt_online'
    custom_settings = {
        # 'LOG_FILE': f'{name}.log',
    }
