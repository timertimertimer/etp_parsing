from general_utils.config import (
    absolute_download_path,
    relative_download_path,
    format_parse_date,
)

start_date = format_parse_date(0, "%d.%m.%y")
search_link = "https://www.roseltorg.ru/search/sale"
formdata = {"sale": "all", "section-type[]": "all", "start_date_published": start_date}

data_origin = "https://www.roseltorg.ru/"
path_absolute = f"{absolute_download_path}/etp_roseltorg"
path_relative = f"{relative_download_path}/etp_roseltorg"
