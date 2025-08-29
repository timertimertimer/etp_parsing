# https://www.b2b-center.ru/market/?searching=1&company_type=2&price_currency=0&date=1&date_start_dmy=25.07.2025&trade=buy&purchase_223fz=1
import uuid
from datetime import datetime, timedelta

from app.utils import DateTimeHelper
from app.utils.config import headers

login_url = 'https://www.b2b-center.ru/auth/credentials_ajax_login.html'
login_data = {
    "login_form[location_form]": "form_with_popup_page",
    "login_form[login]": "bemaster1209@mail.ru",
    "login_form[password]": "pm52PC1NS8EzDDf",
    "login_form[remember_me]": "1",
    "fingerprint": uuid.uuid4().hex,
    "fingerprint_desc": headers['User-Agent']
}

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
