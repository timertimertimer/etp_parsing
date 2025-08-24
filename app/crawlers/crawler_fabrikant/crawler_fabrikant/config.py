from datetime import datetime, timedelta

from app.utils import DateTimeHelper
from app.utils.config import days

data_origin_url = "https://www.fabrikant.ru/"
start_url = "https://www.fabrikant.ru/trades/procedure/search/"

# fz223 https://www.fabrikant.ru/procedure/search?page_number=1&section_ids%5B%5D=5
# legal_entities https://www.fabrikant.ru/procedure/search/purchases?procedure_direction=buy&section_ids[]=2&page_number=1
# commercial https://www.fabrikant.ru/procedure/search/sales?procedure_direction=sell&section_ids[]=8&page_number=1
# bankruptcy https://www.fabrikant.ru/procedure/search?page_number=1&section_ids%5B%5D=6
sections = ["fz223", "legal_entities", "commercial", "bankruptcy"]
section_ids = dict(zip(sections, ["5", "8", "2", "6"]))
start_urls = dict(
    zip(
        sections,
        [
            "https://www.fabrikant.ru/procedure/search",
            "https://www.fabrikant.ru/procedure/search/purchases",
            "https://www.fabrikant.ru/procedure/search/sales",
            "https://www.fabrikant.ru/procedure/search",
        ],
    )
)

start_date = DateTimeHelper.format_datetime(
    datetime.now(DateTimeHelper.moscow_tz) - timedelta(days=days), "%Y-%m-%d"
)

formdatas = {
    'fz223': {
        'date_publication_from': start_date,
        'page_number': '1',
        'page_limit': '100',
        'section_ids[]': '5'
    },
    'legal_entities': {
        'date_publication_from': start_date,
        'procedure_direction': 'buy',
        'section_ids[]': '2',
        'page_number': '1',
        'page_limit': '100',
    },
    'commercial': {
        'date_publication_from': start_date,
        'procedure_direction': 'sell',
        'section_ids[]': '8',
        'page_number': '1',
        'page_limit': '100',
    },
    'bankruptcy': {
        'date_publication_from': start_date,
        'page_number': '1',
        'page_limit': '100',
        'section_ids[]': '6'
    }
}
# splash.js_enabled=false
script_lua = """
         function main(splash)
         splash:on_request(function(request)
             if request.url:find('css') then
                 request.abort()
                 end
             end)
             splash.images_enabled=false
             splash.js_enabled=true
             splash.private_mode_enabled = false
             splash:init_cookies(splash.args.cookies)
             assert(splash:go{
             splash.args.url,
             headers=splash.args.headers,
             http_method=splash.args.http_method,
             body=splash.args.body,
             })
             assert(splash:wait(4))
             local entries = splash:history()
             local last_response = entries[#entries].response
             return {
                 url = splash:url(),
                 headers = last_response.headers,
                 http_status = last_response.status,
                 cookies = splash:get_cookies(),
                 html = splash:html(),
                 }
         end
                 """
