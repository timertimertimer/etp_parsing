from .base import AltimetaBaseSpider


class AtctradeSpider(AltimetaBaseSpider):
    name = 'atctrade'
    custom_settings = {
        # 'LOG_FILE': f'{name}.log',
    }
