from general_utils.config import write_log_to_file
from .base import ElectroTorgiBaseSpider


class UralbidinSpiderElectroTorgi(ElectroTorgiBaseSpider):
    name = "uralbidin"
    custom_settings = {
        "LOG_FILE": f"{name}.log" if write_log_to_file else None,
    }
