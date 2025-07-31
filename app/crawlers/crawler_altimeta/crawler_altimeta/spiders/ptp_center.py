from app.utils.config import write_log_to_file
from .base import AltimetaBaseSpider


class PtpCenterSpider(AltimetaBaseSpider):
    name = "ptp_center"
    custom_settings = {
        "LOG_FILE": f"{name}.log" if write_log_to_file else None,
    }
