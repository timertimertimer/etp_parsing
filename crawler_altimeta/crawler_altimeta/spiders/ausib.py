from .base import AltimetaBaseSpider


class AusibSpider(AltimetaBaseSpider):
    name = 'ausib'
    custom_settings = {
        # 'LOG_FILE': f'{name}.log',
    }
