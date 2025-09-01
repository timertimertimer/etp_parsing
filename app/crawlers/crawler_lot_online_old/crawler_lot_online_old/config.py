from datetime import timedelta, datetime

from app.utils import DateTimeHelper

main_data_origin = "https://www.lot-online.ru/"
domains = ["rad", "confiscate", "lease", "privatization", "arrested"]
data_origin = {}
path_absolute = {}
path_relative = {}
for domain in domains:
    data_origin[domain] = f"https://{domain}.lot-online.ru/"
form_data = {
    "saleTypeId": "3001",
    "applicationSubmitStart": DateTimeHelper.format_datetime(datetime.now() - timedelta(days=30), "%d/%m/%Y"),
    "applicationSubmitStop": "",
    "biddingStart": "",
    "biddingStop": "",
    "tenderType": "",
    "nonElectronic": "",
    "country": "1001",
    "region": "",
    "category": "",
    "keyWords": "",
    "tenderLotFilter": "TENDER",
    "tenderStatusSet": "",
    "lotStatusSet": "",
    "profileId": "",
    "_search": "false",
    "rows": "100",
    "page": "1",
    "sidx": "",
    "sord": "asc",
}
