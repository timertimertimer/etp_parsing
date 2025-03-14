from ..spiders.base import ItenderBaseSpider


class UtenderSpider(ItenderBaseSpider):
    name = 'utender'
    custom_settings = {
        # 'LOG_FILE': f'{name}.log',
    }
