from general_utils.config import absolute_download_path, relative_download_path, format_parse_date

host = 'ru-trade24.ru'
data_origin = 'http://ru-trade24.ru/'
formdata = {
    'MainPageFilterPartpAppDateBegin': format_parse_date(30, '%d.%m.%Y %H:%M'),
    'MainPageFilterTradeType': 'Undefined',
    'MainPageFilterTradeStatus': '0'
}
page_limits = {
    'page_start': 0,  # страница начала парсинга (включительно)
    'page_stop': 15  # страница остановки парсинга (включительно)
}

absolute_path = absolute_download_path / 'etp_rutrade24'
relative_path = relative_download_path / 'etp_rutrade24'
