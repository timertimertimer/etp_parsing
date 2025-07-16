from app.utils.config import start_date

data_origin_url = "https://www.fabrikant.ru/"
start_url = 'https://www.fabrikant.ru/trades/procedure/search/'
filter_ids = {
    "bankruptcy": 6,
    "commercial": 8,
    "legal_entities": 2,
    "fz223": 5
}

formdata = {
    "type": "1",
    "org_type": "org",
    "currency": "0",
    "date_type": "date_publication",
    "date_from": f"{start_date}",
    "ensure": "all",
    "filter_id": "6",
    "okpd2_embedded": "1",
    "okdp_embedded": "1",
    "active": "",
    "count_on_page": "40",
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
