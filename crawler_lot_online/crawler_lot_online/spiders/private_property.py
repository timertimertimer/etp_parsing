from general_utils.config import write_log_to_file
from .base_catalog import LotOnlineBaseSpider


class LotOnlineBankruptcySpider(LotOnlineBaseSpider):
    name = "lot_online_private_property"
    custom_settings = {
        'LOG_FILE': f'{name}.log' if write_log_to_file else None,
    }
