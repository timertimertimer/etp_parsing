from app.utils.config import start_dates

data_origin_url = "https://heveya.ru/"
main_url = "https://heveya.ru/torgi-po-bankrotstvu"

crawler_name = 'heveya'
start_date = start_dates[crawler_name]
params = {
    "publish_date_begin": start_date,
    "search_by_all_fields": "description",
}
bankruptcy_params = params | {
    "direction[]": "bankruptcy",
}
arrested_params = params | {
    "direction[]": "seized_property",
}
