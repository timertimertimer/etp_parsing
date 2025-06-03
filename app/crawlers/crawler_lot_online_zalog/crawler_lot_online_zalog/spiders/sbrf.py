from general_utils.config import write_log_to_file
from .base import LotOnlineZalogBaseSpider


class LotOnlineZalogSbrfSpider(LotOnlineZalogBaseSpider):
    name = 'sbrf'
    custom_settings = {
        'LOG_FILE': f'{name}.log' if write_log_to_file else None,
    }
