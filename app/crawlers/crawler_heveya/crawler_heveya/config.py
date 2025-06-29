from app.utils.config import format_parse_date

data_origin_url = "https://heveya.ru/"
main_url = "https://heveya.ru/torgi-po-bankrotstvu"

params = {
    "publish_date_begin": format_parse_date(7),
    "search_by_all_fields": "description",
}
bankruptcy_params = params | {
    "direction[]": "bankruptcy",
}
arrested_params = params | {
    "direction[]": "seized_property",
}
