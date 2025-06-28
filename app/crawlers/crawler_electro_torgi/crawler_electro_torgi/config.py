from app.utils.config import format_parse_date

start_date = format_parse_date(30, "%d.%m.%Y 00:01")
end_date = format_parse_date(0, "%d.%m.%Y 23:59")

data_origin_urls = {
    "vetp_bankrupt": "https://xn--80ab2alglp.xn--b1a0ai7b.xn--p1ai/",
    "vetp_arrest": "https://xn--80ab2alglp.xn--b1a0ai7b.xn--p1ai/",
    "uralbidin": "https://uralbidin.ru/",
    "electro_torgi": "https://bankrotstvo.electro-torgi.ru/",
}
urls = data_origin_urls.copy() | {
    "vetp_arrest": "https://xn--80ak6aff.xn--b1a0ai7b.xn--p1ai/"
}
