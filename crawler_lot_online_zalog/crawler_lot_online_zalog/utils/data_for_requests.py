script_lua = """
         function main(splash)
         splash:on_request(function(request)
             if request.url:find('css') then
                 request.abort()
                 end
             end)
             splash.images_enabled=false
             splash.js_enabled=true
             assert(splash:autoload("https://code.jquery.com/jquery-3.2.1.min.js"))
             splash.private_mode_enabled = false
             splash:init_cookies(splash.args.cookies)
             assert(splash:go{
             splash.args.url,
             headers=splash.args.headers,
             http_method=splash.args.http_method,
             body=splash.args.body,
             })
             assert(splash:wait(3))
             assert(splash:runjs("document.querySelector('div .content-block p:nth-child(2) a').click()"))
             assert(splash:wait(10))
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

script_lua_2 = """
         function main(splash)
         splash:on_request(function(request)
             if request.url:find('css') then
                 request.abort()
                 end
             end)
             splash.images_enabled=false
             splash.js_enabled=false
            assert(splash:autoload("https://code.jquery.com/jquery-3.2.1.min.js"))
             splash.private_mode_enabled = false
             splash:init_cookies(splash.args.cookies)
             assert(splash:go{
             splash.args.url,
             headers=splash.args.headers,
             http_method=splash.args.http_method,
             body=splash.args.body,
             })
             assert(splash:wait(3))
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