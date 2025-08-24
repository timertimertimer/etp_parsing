from datetime import datetime, timedelta

from app.utils.config import DateTimeHelper

data_origin_url = "https://heveya.ru/"
main_url = "https://heveya.ru/torgi-po-bankrotstvu"

days = 7
start_date = DateTimeHelper.format_datetime(
    datetime.now(DateTimeHelper.moscow_tz) - timedelta(days=days), "%d.%m.%Y"
)
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
