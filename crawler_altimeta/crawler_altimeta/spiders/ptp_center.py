from .base import AltimetaBaseSpider


class PtpCenterSpider(AltimetaBaseSpider):
    name = 'ptp_center'
    custom_settings = {
        # 'LOG_FILE': f'{name}.log',
    }
