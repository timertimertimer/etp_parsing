# -*- coding: utf-8 -*-
from ..utils.config import headers_brow

script_lua = """
         function main(splash)
         splash:on_request(function(request)
             if request.url:find('css') then
                 request.abort()
                 end
             end)
             -- assert(splash:autoload("https://m-ets.ru/js/jquery-1.7.2.min.js?v=11"))
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
             assert(splash:wait(7))
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

script_lua_category = """
         function main(splash)
         splash:on_request(function(request)
             if request.url:find('css') then
                 request.abort()
                 end
             end)
             -- assert(splash:autoload("https://m-ets.ru/js/jquery-1.7.2.min.js?v=11"))
             splash.images_enabled=false
             splash.private_mode_enabled = false
             splash.plugins_enabled = false
             splash.js_enable = false
             splash:init_cookies(splash.args.cookies)
	         assert(splash:wait(0.5))
             assert(splash:go{
             splash.args.url,
             headers=splash.args.headers,
             http_method=splash.args.http_method,
             body=splash.args.body,
             })
             assert(splash:wait(5.5))
             local entries = splash:history()
             local last_response = entries[#entries].response
             splash:runjs("window.scrollTo(0,document.body.scrollHeight);")
             assert(splash:wait(0.5))
             return {
                 headers = last_response.headers,
                 cookies = splash:get_cookies(),
                 html = splash:html(),
                 }
         end
                 """

script_pagination_lua = """
         function main(splash)
         splash:on_request(function(request)
             if request.url:find('css') then
                 request.abort()
                 end
             end)
             splash.images_enabled=false
             splash.private_mode_enabled = false
             splash.plugins_enabled = false
             splash.js_enable = false
	         assert(splash:wait(0.5))
             assert(splash:go{
             splash.args.url,
             headers=splash.args.headers,
             })
             assert(splash:wait(5.5))
             splash:runjs("window.scrollTo(0,document.body.scrollHeight);")
            assert(splash:wait(0.5))
             return {
                    html = splash:html(),
                   
                        }
            end

  
                 """

post_headers = {
    ':authority': 'bankrot.fedresurs.ru',
    ':method': 'POST',
    ':path': '/Messages.aspx',
    ':scheme': 'https',
    'accept': '*/*',
    'accept-encoding': 'gzip, deflate, br',
    'accept-language': 'en-US,en;q=0.9,ru-RU;q=0.8,ru;q=0.7,de-DE;q=0.6,de;q=0.5,uk-UA;q=0.4,uk;q=0.3,ro-RO;q=0.2,ro;q=0.1',
    'cache-control': 'no-cache',
    # 'content-type': 'application/x-www-form-urlencoded; charset=UTF-8',
    'dnt': '1',
    'origin': 'https://bankrot.fedresurs.ru',
    'pragma': 'no-cache',
    'cookie': '',
    'referer': '',
    'sec-fetch-dest': 'empty',
    'sec-fetch-mode': 'cors',
    'sec-fetch-site': 'same-origin',
    'x-microsoftajax': 'Delta=true',
    'x-requested-with': 'XMLHttpRequest',
    'user-agent': headers_brow['User-Agent']

}

request_headers_msg = {
    ':authority': 'bankrot.fedresurs.ru',
    ':method': 'POST',
    ':path': '/Messages.aspx',
    ':scheme': 'https',
    'accept': '*/*',
    'accept-encoding': 'gzip, deflate, br',
    'accept-language': 'en-US,en;q=0.9,ru-RU;q=0.8,ru;q=0.7,de-DE;q=0.6,de;q=0.5,uk-UA;q=0.4,uk;q=0.3,ro-RO;q=0.2,ro;q=0.1',
    'cache-control': 'no-cache',
    # 'content-type': 'application/x-www-form-urlencoded; charset=UTF-8',
    'dnt': '1',
    'origin': 'https://bankrot.fedresurs.ru',
    'pragma': 'no-cache',
    'referer': '',
    'sec-fetch-dest': 'empty',
    'sec-fetch-mode': 'cors',
    'sec-fetch-site': 'same-origin',
    'x-microsoftajax': 'Delta=true',
    'x-requested-with': 'XMLHttpRequest',
    'user-agent': headers_brow['User-Agent']

}

headers_msg_page = {
    ':authority': 'bankrot.fedresurs.ru',
    ':method': 'GET',
    ':path': '',
    ':scheme': 'https',
    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
    'accept-encoding': 'gzip, deflate, br',
    'accept-language': 'en-US,en;q=0.9,ru-RU;q=0.8,ru;q=0.7,de-DE;q=0.6,de;q=0.5,uk-UA;q=0.4,uk;q=0.3,ro-RO;q=0.2,ro;q=0.1',
    'cache-control': 'no-cache',
    # 'content-type': 'application/x-www-form-urlencoded; charset=UTF-8',
    'dnt': '1',
    'origin': 'https://bankrot.fedresurs.ru',
    'pragma': 'no-cache',
    # 'cookie': '',
    'referer': '',
    'connection': 'keep-alive',
    'sec-fetch-dest': 'document',
    'sec-fetch-mode': 'navigate',
    'sec-fetch-site': 'same-origin',
    'sec-fetch-user': '?1',
    'upgrade-insecure-requests': '1',
    # 'x-microsoftajax': 'Delta=true',
    # 'x-requested-with': 'XMLHttpRequest',
    'user-agent': headers_brow['User-Agent']

}
