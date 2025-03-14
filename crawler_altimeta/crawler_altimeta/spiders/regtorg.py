from .base import AltimetaBaseSpider


class RegtorgSpider(AltimetaBaseSpider):
    name = 'regtorg'
    custom_settings = {
        # 'LOG_FILE': f'{name}.log',
    }
