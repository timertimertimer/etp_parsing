from datetime import datetime

from app.utils.config import DateTimeHelper, start_dates

crawler_name = "electro_torgi"
start_date = start_dates[crawler_name]
end_date = DateTimeHelper.format_datetime(datetime.now(), "%d.%m.%Y 23:59")

data_origin_urls = {
    "vetp_bankrupt": "https://xn--80ab2alglp.xn--b1a0ai7b.xn--p1ai/",
    "vetp_arrested": "https://xn--80ab2alglp.xn--b1a0ai7b.xn--p1ai/",
    "uralbidin": "https://uralbidin.ru/",
    "electro_torgi": "https://bankrotstvo.electro-torgi.ru/",
}
urls = data_origin_urls.copy() | {
    "vetp_arrested": "https://xn--80ak6aff.xn--b1a0ai7b.xn--p1ai/"
}
