from .base import AltimetaBaseSpider


class EtpProfitSpider(AltimetaBaseSpider):
    name = 'etp_profit'
    custom_settings = {
        # 'LOG_FILE': f'{name}.log',
    }
