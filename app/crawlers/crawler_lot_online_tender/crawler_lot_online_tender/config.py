# https://tender.lot-online.ru/api-gateway/indexer/api/lots/query-extended?limit=10&page=0&publicationDateFrom=2025-07-24&sort=publicationDate&hash=ghkFcuqWPZ
from app.utils.config import start_dates

data_origin = 'https://www.lot-online.ru/'
search_link = 'https://tender.lot-online.ru/api-gateway/indexer/api/lots/query-extended'
# FIXME: может быть https://tender.lot-online.ru/api-gateway/etp/procedure/pr/RAD000-25000165500050?v=SiOzzlNbvA ("purchaseCategoryCode": "PriceRequestCase")
lot_link = 'https://tender.lot-online.ru/api-gateway/etp/procedure/{procedure_id}/1'
crawler_name = 'lot_online_tender'
start_date = start_dates[crawler_name]
formdata = {
    'limit': "100",
    'page': '0',
    'publicationDateFrom': start_date,
    'sort': 'publicationDate'
}
