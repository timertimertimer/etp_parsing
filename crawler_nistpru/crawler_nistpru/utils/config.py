from general_utils.config import absolute_download_path, relative_download_path

end_request = ''
link_path_to_lots = '/etp/trade/inner-view-lots.html?perspective=inline&id='
_data_origin = 'https://nistp.ru/'
_trade_link = 'https://nistp.ru/bankrot'
path_absolute = f'{absolute_download_path}/etp_nistp'
path_relative = f'{relative_download_path}/etp_nistp'
script_lua = """
         function main(splash)
         splash:on_request(function(request)
             if request.url:find('css') then
                 request.abort()
             end 
             end)
             splash:autoload("https://nistp.ru/inc/js/jquery-3.5.1.min.js")
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
