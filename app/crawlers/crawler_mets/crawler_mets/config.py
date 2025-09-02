from app.utils.config import start_dates

data_origin_url = "https://m-ets.ru/"
url_start = "https://m-ets.ru/search"
crawler_name = 'mets'
start_date = start_dates[crawler_name]

pattern_without_hash = r"https.+m-ets.+generalView.+id=\d+"
pattern_trade_links = r"https.+mets.+View.+id=\d+.(lot1)$"

script_lua = """
         function main(splash)
         splash:on_request(function(request)
             if request.url:find('css') then
                 request.abort()
                 end
             end)
             assert(splash:autoload("https://m-ets.ru/js/jquery-1.7.2.min.js?v=11"))
             splash.images_enabled=false
             splash.private_mode_enabled = false
             splash.plugins_enabled = false
             splash:init_cookies(splash.args.cookies)
	     assert(splash:wait(1))
             assert(splash:go{
             splash.args.url,
             headers=splash.args.headers,
             http_method=splash.args.http_method,
             body=splash.args.body,
             })
             assert(splash:wait(3))
             local entries = splash:history()
             local last_response = entries[#entries].response
             splash:runjs("window.scrollTo(0,document.body.scrollHeight);")
             assert(splash:wait(2))
             return {
                 headers = last_response.headers,
                 cookies = splash:get_cookies(),
                 html = splash:html(),
                 }
         end
                 """

data_search = {
    "submit": "",
    "lots": "",
    "lotst": "2",
    "lotst[]": "2",
    "displayby": "2",
    "displayby[]": "2",
    "isbankr": "on",
    "isauk": "on",
    "ispub": "on",
    "isaukupdown": "on",
    "zay": "",
    "autoyear_ot": "",
    "autoyear_do": "",
    "cadastr": "",
    "iskl": "",
    "debtor": "",
    "arb": "",
    "org": "",
    "arb_org": "",
    "arb_org[]": "",
    "foto": "",
    "zadat": "",
    "cena_nach_ot": "",
    "cena_nach_do": "",
    "cena_tek_ot": "",
    "cena_tek_do": "",
    "cena_min_ot": "",
    "cena_min_do": "",
    "proc_snij_ot": "",
    "proc_snij_do": "",
    "date_nach_ot": "",
    "date_nach_do": "",
    "date_kon_ot": "",
    "date_kon_do": "",
    "search_category": "",
}

script_lua_lot = """
          function main(splash)
         splash:on_request(function(request)
             if request.url:find('css') then
                 request.abort()
                 end
             end)
             splash.images_enabled=false
             splash.js_enabled=false
             splash.private_mode_enabled = false
             splash.plugins_enabled = false
             splash:init_cookies(splash.args.cookies)
	         assert(splash:wait(0.5))
             assert(splash:go{
             splash.args.url,
             headers=splash.args.headers,
             http_method=splash.args.http_method,
             body=splash.args.body,
             })
             assert(splash:wait(3))
             local entries = splash:history()
             local last_response = entries[#entries].response
             assert(splash:wait(2))
             return {
                 html = splash:html(),
                 }
         end
                 """
