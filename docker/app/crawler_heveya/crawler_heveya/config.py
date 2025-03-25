from general_utils.config import start_date, absolute_download_path, relative_download_path

data_origin_url = "https://heveya.ru/"
main_url = "https://heveya.ru/torgi-po-bankrotstvu"

params = {"direction[]": "bankruptcy", "publish_date_begin": start_date, "search_by_all_fields": "description"}
path_absolute = f"{absolute_download_path}/etp_heveya"
path_relative = f"{relative_download_path}/etp_heveya"
