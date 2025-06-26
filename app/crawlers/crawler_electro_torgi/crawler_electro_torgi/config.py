from general_utils.config import (
    absolute_download_path,
    relative_download_path,
    format_parse_date,
)

start_date = format_parse_date(30, "%d.%m.%Y 00:01")
end_date = format_parse_date(0, "%d.%m.%Y 23:59")

data_origin = {
    "vetp": "https://xn--80ab2alglp.xn--b1a0ai7b.xn--p1ai/",
    "uralbidin": "https://uralbidin.ru/",
    "electro_torgi": "https://bankrotstvo.electro-torgi.ru/",
}

path_absolute = {
    "uralbidin": absolute_download_path / "etp_uralbidin",
    "vetp": absolute_download_path / "etp_vetp",
    "electro_torgi": absolute_download_path / "etp_electro_torgi",
}
path_relative = {
    "uralbidin": relative_download_path / "etp_uralbidin",
    "vetp": relative_download_path / "etp_vetp",
    "electro_torgi": relative_download_path / "etp_electro_torgi",
}
