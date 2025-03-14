from ..spiders.base import ItenderBaseSpider


class GloriaserviceSpider(ItenderBaseSpider):
    name = 'gloriaservice'
    custom_settings = {
        # 'LOG_FILE': f'{name}.log',
    }
