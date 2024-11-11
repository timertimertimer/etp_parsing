# -*- coding: utf-8 -*-
script_lua = """
         function main(splash)
            splash:on_request(function(request)
                if request.url:find('css') then
                    request.abort()
                end
            end)
            splash.images_enabled = false
            splash.plugins_enabled = false
            splash:init_cookies(splash.args.cookies)
            local success, response = pcall(function()
                assert(splash:go(splash.args.url))
            end)
            if response:find("503") then
                print("Received HTTP 503, processing JavaScript...")
                local scripts = splash:select_all('script')  -- Получаем все <script> элементы
                local js_code = ""
            
                for _, script in ipairs(scripts) do
                    local content = script.node.innerHTML
                    if content and content:find("document.cookie") then
                        js_code = js_code .. content  -- Собираем код
                    end
                end
                splash:runjs(js_code)
                assert(splash:wait(2))
            end
            assert(splash:go(splash.args.url))
            return {
                cookies = splash:get_cookies(),
                html = splash:html(),
            }
        end
                 """

script_lua_nojs = """
         function main(splash)
            print("Cookie: ", splash.args.cookies)
         splash:on_request(function(request)
             if request.url:find('css') then
                 request.abort()
                 end
             end)
             splash.images_enabled=false
             -- splash:autoload("https://code.jquery.com/jquery-1.7.1.min.js")
             -- splash.plugins_enabled = false
             splash.js_enabled = false
             splash:init_cookies(splash.args.cookies)
	         assert(splash:wait(1))
             assert(splash:go{
             splash.args.url,
             -- headers=splash.args.headers,
             http_method=splash.args.http_method,
             --  body=splash.args.body,
             })
             assert(splash:wait(4))
             -- local entries = splash:history()
            --  local last_response = entries[#entries].response
             -- splash:runjs("window.scrollTo(0,document.body.scrollHeight);")
             assert(splash:wait(2))
             return {
                 -- headers = last_response.headers,
                 cookies = splash:get_cookies(),
                 html = splash:html(),
                 }
         end
                 """
