# https://www.b2b-center.ru/market/?searching=1&company_type=2&price_currency=0&date=1&date_start_dmy=25.07.2025&trade=buy&purchase_223fz=1
from datetime import datetime, timedelta

from app.utils import DateTimeHelper

days = 7
params = {
    "searching": "1",
    "company_type": "2",
    "price_currency": "0",
    "date": "1",
    "date_start_dmy": DateTimeHelper.format_datetime(datetime.now() - timedelta(days=days), '%d.%m.%Y'),
    "trade": "buy",
    "purchase_223fz": "1"
}
data_origin = 'https://www.b2b-center.ru/'
