from app.utils.config import (
    format_parse_date,
)

host = "ru-trade24.ru"
hosts = {
    'bankruptcy': "ru-trade24.ru",
    'commercial': "com.ru-trade24.ru"
}
data_origin = "http://ru-trade24.ru/"
data_origins = {
    'bankruptcy': data_origin,
    'commercial': "https://com.ru-trade24.ru"
}
start_urls = {
    'bankruptcy': 'https://ru-trade24.ru/query/Filter',
    'commercial': 'https://com.ru-trade24.ru/query/Filter',
}

formdata = {
    "MainPageFilterPartpAppDateBegin": format_parse_date(30, "%d.%m.%Y %H:%M"),
    # "MainPageFilterTradeType": "Undefined",
    "MainPageFilterTradeStatus": "0",
}
page_limits = {
    "page_start": 0,  # страница начала парсинга (включительно)
    "page_stop": 15,  # страница остановки парсинга (включительно)
}
