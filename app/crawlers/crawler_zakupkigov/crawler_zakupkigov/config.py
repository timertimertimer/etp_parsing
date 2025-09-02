# https://zakupki.gov.ru/epz/order/extendedsearch/results.html?morphology=on&search-filter=Дате+размещения&pageNumber=1&sortDirection=false&recordsPerPage=_10&showLotsInfoHidden=false&sortBy=UPDATE_DATE&fz44=on&af=on&ca=on&pc=on&pa=on&currencyIdGeneral=-1 fz44
# https://zakupki.gov.ru/epz/order/extendedsearch/results.html?morphology=on&search-filter=Дате+размещения&pageNumber=1&sortDirection=false&recordsPerPage=_10&showLotsInfoHidden=false&sortBy=UPDATE_DATE&ppRf615=on&af=on&ca=on&pc=on&pa=on&currencyIdGeneral=-1 captial_repair
from app.utils.config import start_dates

data_origin = 'https://zakupki.gov.ru/'
search_link = 'https://zakupki.gov.ru/epz/order/extendedsearch/results.html'

crawler_name = 'zakupkigov'
start_date = start_dates[crawler_name]
initial_formdata = {
    "morphology": "on",
    "search-filter": "Дате размещения",
    "pageNumber": "1",
    "sortDirection": "false",
    "recordsPerPage": "_500",
    "showLotsInfoHidden": "false",
    "sortBy": "UPDATE_DATE",
    "af": "on",
    "ca": "on",
    "pc": "on",
    "pa": "on",
    "currencyIdGeneral": "-1",
    "publishDateFrom": start_date
}

formdata = {
    'fz44': initial_formdata | {'fz44': 'on'},
    'capital_repair': initial_formdata | {'ppRf615': 'on'},
}
