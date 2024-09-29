from crawler_sales_lot_online.utils.config import headers_brow, Referer_lot

USER_AGENT = headers_brow['User-Agent']

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
             assert(splash:runjs("document.querySelector('div .content-block p:first-child a').click()"))
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
             
             -- assert(splash:runjs("$('a[id*=switcher-filter]').click()"))
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

script_lua_lot = """
         function main(splash)
         splash:on_request(function(request)
             if request.url:find('css') then
                 request.abort()
                 end
             end)
             splash.images_enabled=false
             -- assert(splash:autoload("https://code.jquery.com/jquery-3.2.1.min.js"))
             splash.private_mode_enabled = false
             splash.plugins_enabled = false
             splash:init_cookies(splash.args.cookies)
             assert(splash:go{
             splash.args.url,
             headers=splash.args.headers,
             http_method=splash.args.http_method,
             body=splash.args.body,
             })
             assert(splash:wait(2))
             splash:set_viewport_size(1980, 1020)
             assert(splash:wait(1))
              -- element -> arbitr info (click)
              if splash:select('a[id="formMain:clDpExpEvent4"]') then
                local element = splash:select('a[id="formMain:clDpExpEvent4"]')
                local bounds = element:bounds()
                assert(element:mouse_click{x=bounds.width/3, y=bounds.height/3})
                end
             assert(splash:wait(2))
             local entries = splash:history()
             local last_response = entries[#entries].response
             return {
                 html = splash:html(),
                 cookies = splash:get_cookies()
                 }
         end
                 """

form_data = {'javax.faces.partial.ajax': 'true',
             'javax.faces.source': 'formMain:cbFilter',
             'javax.faces.partial.execute': 'formMain:cbFilter formMain:pgFilterFields',
             'javax.faces.partial.render': 'formMain:pgFilterFields formMain:panelList formMain:LotListPaginatorID formMain:lotListHeaderPanel',
             'formMain:cbFilter': 'formMain:cbFilter',
             'formMain': 'formMain',
             'formMain:inputServerTime': '',
             'formMain:commonSearchCriteriaStr': '',
             'formMain:j_idt82': '22',
             'formMain:scmTypeAuctionId_focus': '',
             'formMain:scmTypeAuctionId': ['100', '21', '22', '24', '28'],
             'formMain:scmSubjectRFId_focus': '',
             'formMain:itKeyWords': '',
             'formMain:itTradeOrganizer': '',
             'formMain:auctionDatePlanBID_input': '',
             'formMain:auctionDatePlanEID_input': '',
             'formMain:costBValueB': '',
             'formMain:costBValueE': '',
             'formMain:itLotNoticeNum': '',
             'formMain:itAuctionRegNum': '',
             'formMain:selectIndRightEnsure': '2',
             'formMain:selectIndPublish': '3',
             'javax.faces.ViewState': ''}

form_data_ = {'javax.faces.partial.ajax': 'true',
              'javax.faces.source': 'formMain:cbFilter',
              'javax.faces.partial.execute': '@all',
              'javax.faces.partial.render': 'formMain:inputServerTime',
              'formMain:j_idt10': 'formMain:j_idt10',
              'formMain': 'formMain',
              'formMain:inputServerTime': '',
              'formMain:commonSearchCriteriaStr': '',
              'formMain:j_idt82': '22',
              'formMain:scmTypeAuctionId_focus': '',
              'formMain:scmTypeAuctionId': ['100', '21', '22', '24', '28'],
              'formMain:scmSubjectRFId_focus': '',
              'formMain:itKeyWords': '',
              'formMain:itTradeOrganizer': '',
              'formMain:auctionDatePlanBID_input': '',
              'formMain:auctionDatePlanEID_input': '',
              'formMain:costBValueB': '0',
              'formMain:costBValueE': '0',
              'formMain:itLotNoticeNum': '',
              'formMain:itAuctionRegNum': '',
              'formMain:selectIndRightEnsure': '2',
              'formMain:selectIndPublish': '3',
              'javax.faces.ViewState': ''}

data_switcher = {'javax.faces.partial.ajax': 'true',
                 'javax.faces.source': 'formMain:switcher-filter',
                 'javax.faces.partial.execute': 'formMain:switcher-filter',
                 'javax.faces.partial.render': 'formMain:switcher-filter formMain:form-filter-tender',
                 'formMain:switcher-filter': 'formMain:switcher-filter',
                 'formMain': 'formMain',
                 'formMain:inputServerTime': '',
                 'formMain:commonSearchCriteriaStr': '',
                 'javax.faces.ViewState': ''}

data_next_page = {'javax.faces.partial.ajax': 'true',
                  'javax.faces.source': 'formMain:clNext',
                  'javax.faces.partial.execute': 'formMain:clNext',
                  'javax.faces.partial.render': 'formMain:panelList formMain:LotListPaginatorID',
                  'formMain:clNext': 'formMain:clNext',
                  'formMain': 'formMain',
                  'formMain:inputServerTime': '',
                  'formMain:commonSearchCriteriaStr': '',
                  'formMain:j_idt82': '22',
                  'formMain:scmTypeAuctionId_focus': '',
                  'formMain:scmTypeAuctionId': ['100', '21', '22', '24', '28'],
                  'formMain:scmSubjectRFId_focus': '',
                  'formMain:itKeyWords': '',
                  'formMain:itTradeOrganizer': '',
                  'formMain:auctionDatePlanBID_input': '',
                  'formMain:auctionDatePlanEID_input': '',
                  'formMain:costBValueB': '0',
                  'formMain:costBValueE': '0',
                  'formMain:itLotNoticeNum': '',
                  'formMain:itAuctionRegNum': '',
                  'formMain:selectIndRightEnsure': '2',
                  'formMain:selectIndPublish': '3',
                  'javax.faces.ViewState': ''}

headers_for_lot = {

    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,'
              '*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
    'Accept-Encoding': 'gzip, deflate, br',
    'Accept-Language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7',
    'Cache-Control': 'no-cache',
    'Connection': 'keep-alive',
    'Host': 'sales.lot-online.ru',
    'Pragma': 'no-cache',
    'Referer': Referer_lot,
    'Sec-Fetch-Dest': 'document',
    'Sec-Fetch-Mode': 'navigate',
    'Sec-Fetch-Site': 'none',
    'Upgrade-Insecure-Requests': '1',
    'User-Agent': USER_AGENT,
}

header_arbitr_get = {'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,'
                               '*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
                     'Accept-Encoding': 'gzip, deflate, br',
                     'Accept-Language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7', }
