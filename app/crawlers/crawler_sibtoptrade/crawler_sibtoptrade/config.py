from general_utils.config import absolute_download_path, relative_download_path

data_origin = "https://sibtoptrade.ru/"
url_bankrupty = "https://sibtoptrade.ru/trade/bankruptcy/#state=1&page=1& "

start_urls = "https://sibtoptrade.ru/trade/bankruptcy/#state=1&page={}&"
start_urls1 = "https://sibtoptrade.ru/trade/bankruptcy/#state=1&page=1&"
start_page = 1
finish_page = 10
Referer = "https://sibtoptrade.ru/trade/bankruptcy/"

absolute_path = f"{absolute_download_path}/etp_sibtoptrade"
relative_path = f"{relative_download_path}/etp_sibtoptrade"

pattern_trade_links = "sibtoptrade.ru/trade/"
# splash.js_enabled=false
script_lua = """
         function main(splash)
         splash:on_request(function(request)
             if request.url:find('css') then
                 request.abort()
             end 
             end)
             splash.images_enabled=false
             
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
