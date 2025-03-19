from general_utils.config import write_log_to_file
from .base import LotOnlineCatalogBaseSpider


class LotOnlineBankruptcySpider(LotOnlineCatalogBaseSpider):
    name = "lot_online_bankruptcy"
    custom_settings = {
        'LOG_FILE': f'{name}.log' if write_log_to_file else None,
    }
