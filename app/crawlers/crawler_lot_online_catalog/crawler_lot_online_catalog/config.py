from datetime import timedelta, datetime

from app.utils import DateTimeHelper

domains = ["bankruptcy", "private_property"]
data_origin = "https://www.lot-online.ru/"

# https://catalog.lot-online.ru/index.php?dispatch=categories.view&category_id=9876&features_hash=172-186357&filter_fields[is_archive]=all
hashes = {
    "lot_online_bankruptcy": "172-186359",
    "lot_online_private_property": "172-186357",
    "lot_online_rent": "172-25147"
}
form_data = {
    "dispatch": "categories.view",
    "category_id": "9876",
    "features_hash": "",
    "filter_fields[is_archive]": "all",
    "sort_by": "timestamp",
    "sort_order": "desc",
    "layout": "short_list",
    "result_ids": "pagination_contents",
    "items_per_page": "96",
    "page": "1",
    "is_ajax": "1",
}
days = 7
start_datetime = datetime.now() - timedelta(days=days)
