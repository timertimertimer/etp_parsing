from ..spiders.base import ItenderBaseSpider


class MetaInvestSpider(ItenderBaseSpider):
    name = 'meta_invest'
    custom_settings = {
        # 'LOG_FILE': f'{name}.log',
    }
