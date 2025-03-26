from general_utils.config import absolute_download_path, relative_download_path, format_parse_date

data_origin_url = "https://heveya.ru/"
main_url = "https://heveya.ru/torgi-po-bankrotstvu"

params = {"direction[]": "bankruptcy", "publish_date_begin": format_parse_date(7), "search_by_all_fields": "description"}
path_absolute = f"{absolute_download_path}/etp_heveya"
path_relative = f"{relative_download_path}/etp_heveya"
