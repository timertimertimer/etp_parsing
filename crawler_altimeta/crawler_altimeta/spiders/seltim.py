from .base import AltimetaBaseSpider


class SeltimSpider(AltimetaBaseSpider):
    name = 'seltim'
    custom_settings = {
        # 'LOG_FILE': f'{name}.log',
    }
