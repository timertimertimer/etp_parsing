from app.utils.config import write_log_to_file
from .base import ElectroTorgiBaseSpider


class VetpBankruptSpiderElectroTorgi(ElectroTorgiBaseSpider):
    name = "vetp_bankrupt"
    custom_settings = {
        "LOG_FILE": f"{name}.log" if write_log_to_file else None,
    }
