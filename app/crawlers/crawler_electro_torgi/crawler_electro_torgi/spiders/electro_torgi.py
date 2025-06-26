from general_utils.config import write_log_to_file
from .base import ElectroTorgiBaseSpider


class ElectroTorgiSpiderElectroTorgi(ElectroTorgiBaseSpider):
    name = "electro_torgi"
    custom_settings = {
        "LOG_FILE": f"{name}.log" if write_log_to_file else None,
    }
