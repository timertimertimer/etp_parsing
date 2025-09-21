from datetime import datetime, timedelta

from app.utils import DateTimeHelper

hosts = {"bankruptcy": "ru-trade24.ru", "commercial": "com.ru-trade24.ru"}
main_data_origin = "http://ru-trade24.ru/"
data_origins = {"bankruptcy": main_data_origin, "commercial": "https://com.ru-trade24.ru"}
start_urls = {
    "bankruptcy": "https://ru-trade24.ru/query/Filter",
    "commercial": "https://com.ru-trade24.ru/query/Filter",
}
pagination_urls = {
    "bankruptcy": "https://ru-trade24.ru/Home/Trades",
    "commercial": "https://com.ru-trade24.ru/Home/Trades",
}

formdata = {
    "MainPageFilterPartpAppDateBegin": DateTimeHelper.format_datetime(
        datetime.now(DateTimeHelper.moscow_tz) - timedelta(days=30), "%d.%m.%Y %H:%M"
    ),
    # "MainPageFilterTradeType": "Undefined",
    "MainPageFilterTradeStatus": "0",
}
page_limits = {
    "page_start": 0,  # страница начала парсинга (включительно)
    "page_stop": 15,  # страница остановки парсинга (включительно)
}
