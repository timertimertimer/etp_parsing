param_id = 'filter_id'
param_id_value = '6'

lots_on_page = '40'

auction_link_pattern = '/market/view.html?action=view_auction'
auction_oazf_link_pattern = '/trades/bankruptcy/AuctionHiddenPrice/'
offer_link_pattern = '/v2/trades/procedure/view/'
competition_link_pattern = '/market/view.html?action=view_tender'

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
