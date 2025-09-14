from app.utils.config import start_dates

main_data_origin = "https://www.lot-online.ru/"
domains = ["rad", "confiscate", "lease", "privatization", "arrested"]
data_origin = {}
for domain in domains:
    data_origin[domain] = f"https://{domain}.lot-online.ru/"
crawler_name = 'lot_online_old'
start_date = start_dates[crawler_name]
form_data = {
    "saleTypeId": "3001",
    "applicationSubmitStart": start_date,
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
