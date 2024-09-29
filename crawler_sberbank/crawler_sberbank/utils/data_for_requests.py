from .config import agent_list
from random import choice
# variable set in xml_data:
# start_date - date and time (00:00) from start publication
# end_date = period to the end of publication; date and time (00:00)
# total_lot = statistics value
# total_sum = statistics value
# total_org = statistics value
# amount_lot_on_page - how many lots views on page
# from_number - like page number but according how many lots on page (amount_lot_on_page). EXM: 100 lot on page - 1st page is 0 2d is 100
xml_data = '<elasticrequest><filters><mainSearchBar><value></value><type>best_fields</type><minimum_should_match>100%</minimum_should_match></mainSearchBar><purchAmount><minvalue></minvalue><maxvalue></maxvalue></purchAmount><PublicDate><minvalue>{start_date}</minvalue><maxvalue>{end_date}</maxvalue></PublicDate><PurchaseStageTerm><value></value><visiblepart></visiblepart></PurchaseStageTerm><RegionNameTerm><value></value><visiblepart></visiblepart></RegionNameTerm><DebtorINNnGram><value></value></DebtorINNnGram><DebtorName><value></value></DebtorName><IsPledgeTerm><checkbox></checkbox><value></value></IsPledgeTerm><RequestStartDate><minvalue></minvalue><maxvalue></maxvalue></RequestStartDate><RequestDate><minvalue></minvalue><maxvalue></maxvalue></RequestDate><AuctionBeginDate><minvalue></minvalue><maxvalue></maxvalue></AuctionBeginDate><okdp2MultiMatch><value></value></okdp2MultiMatch><okdp2tree><value></value><productField></productField><branchField></branchField></okdp2tree><classifier><visiblepart></visiblepart></classifier><orgCondition><value></value></orgCondition><orgDictionary><value></value></orgDictionary><organizator><visiblepart></visiblepart></organizator><PurchaseTypeNameTerm><value></value><visiblepart></visiblepart></PurchaseTypeNameTerm><statistic><totalProc>{total_lot}</totalProc><TotalSum>{total_sum}</TotalSum><DistinctOrgs>{total_org}</DistinctOrgs></statistic></filters><fields><field>TradeSectionId</field><field>purchAmount</field><field>CurrentAmount</field><field>purchCurrency</field><field>purchCodeTerm</field><field>PurchaseTypeName</field><field>BidStatusName</field><field>OrgName</field><field>SourceTerm</field><field>PublicDate</field><field>RequestDate</field><field>RequestStartDate</field><field>RequestAcceptDate</field><field>bankrAuctionStartDate</field><field>CreateRequestHrefTerm</field><field>CreateRequestAlowed</field><field>purchName</field><field>SourceHrefTerm</field><field>objectHrefTerm</field><field>ReqCnt</field><field>BidName</field><field>PurchaseTypeId</field><field>auctResultDate</field><field>needPayment</field><field>PurchaseTypeType</field></fields><sort><value>default</value><direction></direction></sort><aggregations><empty><filterType>filter_aggregation</filterType><field></field><min_doc_count>0</min_doc_count><order>asc</order></empty></aggregations><size>{amount_lot_on_page}</size><from>{from_number}</from></elasticrequest>'

script_lua_first_req = """
         function main(splash, args)
         splash:on_request(function(request)
             if request.url:find('css') then
                 request.abort()
                 end
             end)
             splash.images_enabled=false
             splash.private_mode_enabled = false
             splash:init_cookies(splash.args.cookies)
	         assert(splash:wait(1))
             assert(splash:go{
             splash.args.url,
             headers=splash.args.headers,
             http_method=splash.args.http_method,
             body=splash.args.body,
             })
             assert(splash:wait(4))
             local entries = splash:history()
             local last_response = entries[#entries].response
             local time_from = args.time_from
             local time_to = args.time_to
             local btn = args.btn
             assert(splash:runjs(time_from))
             assert(splash:wait(0.5)) 
             assert(splash:runjs(time_to))
             assert(splash:wait(0.5))
             assert(splash:runjs(btn))
             assert(splash:wait(5))
             return {
                
                 headers = last_response.headers,
                 http_status = last_response.status,
                 cookies = splash:get_cookies(),
                 html = splash:html(),
                 }
         end
                 """

# script_lua = """
#    treat = require("treat")
#    function wait_for_element(splash, css, maxwait)
#     -- Wait until a selector matches an element
#     -- in the page. Return an error if waited more
#     -- than maxwait seconds.
#     if maxwait == nil then
#         maxwait = 10
#     end
#     return splash:wait_for_resume(string.format([[
#       function main(splash) {
#         var selector = '%s';
#         var maxwait = %s;
#         var end = Date.now() + maxwait*1000;
#
#         function check() {
#           if(document.querySelector(selector)) {
#             splash.resume('Element found');
#           } else if(Date.now() >= end) {
#             var err = 'Timeout waiting for element';
#             splash.error(err + " " + selector);
#           } else {
#             setTimeout(check, 1200);
#           }
#         }
#         check();
#       }
#     ]], css, maxwait))
#   end
#
#     function main(splash, args)
#     splash:on_request(function(request)
#              if request.url:find('css') then
#                  request.abort()
#                  end
#              end)
#     splash.images_enabled=false
#     splash.private_mode_enabled = false
#     assert(splash:autoload("https://utp.sberbank-ast.ru/js/jquery-1.7.1.min.js"))
#     assert(splash:autoload("https://utp.sberbank-ast.ru/Scripts/jquery.easing.1.3.js"))
#     assert(splash:autoload("https://utp.sberbank-ast.ru/Scripts/jquery.extender.js"))
#     assert(splash:autoload("https://utp.sberbank-ast.ru/Scripts/jquery.validate.min.js"))
#     assert(splash:autoload("https://utp.sberbank-ast.ru/Scripts/utils.js"))
#     assert(splash:autoload("https://utp.sberbank-ast.ru/Scripts/jquery.unobtrusive-ajax.js"))
#     splash:init_cookies(splash.args.cookies)
#     assert(splash:wait(2))
#     assert(splash:go{
#         splash.args.url,
#         headers=splash.args.headers,
#         http_method=splash.args.http_method,
#         body=splash.args.body,
#         })
#     assert(splash:wait(5))
#     local time_from = args.time_from
#     local time_to = args.time_to
#     local btn = args.btn
#     wait_for_element(splash, "#foo")
#     assert(splash:runjs(time_from))
#     assert(splash:wait(1))
#     assert(splash:runjs(time_to))
#     assert(splash:wait(1))
#     assert(splash:runjs(btn))
#     assert(splash: runjs("$('#headerPagerSelect').val('100').change()"))
#     assert(splash:wait(3))
#
#
#   -- get all page number from pagination
#   local page_num = splash:evaljs("document.querySelector('#footerPagesControl').outerText")
#   -- function for leave only unique page number
#   local uniqItem_func = splash:jsfunc([[
#   function(lst) {
#         var arrayA = [];
#     for (let i = 0; i < lst.length; i++) {
#   		if (isInteger(lst[i])) {
#   		arrayA.push(lst[i]);}
# }
#     return Array.from(new Set(arrayA))
#   }
#     ]])
#     assert(splash:wait(1))
#   -- variable for save only unique page number
#   local uniqueNum = uniqItem_func(page_num)
#
#   -- function click on page number pagination
#   local click_page = splash:jsfunc([[
#     function(num_page) {
#         document.querySelector('#footerPager span[content="' + num_page + '"]:first-child').click();
#     }
#   ]])
#
#   -- iterate throught pages of pagination and get xml content
#   local array_xml = treat.as_array({})
#   for i=1, #uniqueNum do
#   	click_page(i)
#     assert(splash:wait(2))
#     array_xml[i] = splash:evaljs("document.getElementById('xmlData').defaultValue;")
#   	assert(splash:wait(1))
#   end
#   local entries = splash:history()
#   local last_response = entries[#entries].response
#     return {
#             url = splash:url(),
#             headers = last_response.headers,
#             http_status = last_response.status,
#             cookies = splash:get_cookies(),
#             arrayXml = array_xml
#              }
#   end
#                  """

# script_pagination = """
#          function main(splash)
#          splash:on_request(function(request)
#              if request.url:find('css') then
#                  request.abort()
#                  end
#              end)
#              splash.images_enabled=false
#              splash.js_enabled=true
#              splash.private_mode_enabled = false
#              splash:init_cookies(splash.args.cookies)
#              assert(splash:go{
#              splash.args.url,
#              headers=splash.args.headers,
#              http_method=splash.args.http_method,
#              body=splash.args.body,
#              })
#              assert(splash:wait(4))
#              local entries = splash:history()
#              local last_response = entries[#entries].response
#              assert(splash: runjs("$('input[name=PublicDateMin]').val('datefrom')"))
#              assert(splash:wait(1))
#              assert(splash: runjs("$('input[name=PublicDateMax]').val('dateto')"))
#              assert(splash:wait(1))
#              assert(splash: runjs("$('input[type=button][value=Поиск]').click()"))
#              assert(splash:wait(0.2))
#              assert(splash: runjs("$('#headerPagerSelect').val('100').change()"))
#              assert(splash:wait(2))
#              assert(splash:runjs("$('#footerPager span[content=page]:first-child').click()"))
#              assert(splash:wait(2))
#              splash:set_viewport_size(1980, 1020)
#              return {
#                  url = splash:url(),
#                  headers = last_response.headers,
#                  http_status = last_response.status,
#                  cookies = splash:get_cookies(),
#                  html = splash:html(),
#                  }
#          end
#                  """


# # splash.js_enabled=false
script_trading = """
        function wait_for_element(splash, css, maxwait)
          -- Wait until a selector matches an element
          -- in the page. Return an error if waited more
          -- than maxwait seconds.
          if maxwait == nil then
              maxwait = 10
          end
          return splash:wait_for_resume(string.format([[
            function main(splash) {
              var selector = '%s';
              var maxwait = %s;
              var end = Date.now() + maxwait*1000;
        
              function check() {
                if(document.querySelector(selector)) {
                  splash.resume('Element found');
                } else if(Date.now() >= end) {
                  var err = 'Timeout waiting for element';
                  splash.error(err + " " + selector);
                } else {
                  setTimeout(check, 2000);
                }
              }
              check();
            }
          ]], css, maxwait))
        end

         function main(splash)
         splash:on_request(function(request)
             if request.url:find('css') then
                 request.abort()
                 end
             end)
             splash.images_enabled=false
             splash.private_mode_enabled = false
             splash.plugins_enabled = false
             splash.javascript_enabled = false
             splash:init_cookies(splash.args.cookies)
             assert(splash:go{
             splash.args.url,
             headers=splash.args.headers,
             http_method=splash.args.http_method,
             body=splash.args.body,
             })
             assert(splash:wait(3))
             local entries = splash:history()
             local xml_data = splash:evaljs("document.getElementById('xmlData').defaultValue;")
             assert(splash:wait(0.5))
             local last_response = entries[#entries].response
             return {
                 url = splash:url(),
                 headers = last_response.headers,
                 cookies = splash:get_cookies(),
                 html = splash:html(),
                 xmldata = xml_data
                 }
         end
                 """

script_lot = """
         function main(splash)
         splash:on_request(function(request)
             if request.url:find('css') then
                 request.abort()
                 end
             end)
             splash.images_enabled=false
             splash.private_mode_enabled = false
             splash.plugins_enabled = false
             splash:init_cookies(splash.args.cookies)
             assert(splash:go{
             splash.args.url,
             headers=splash.args.headers,
             http_method=splash.args.http_method,
             body=splash.args.body,
             })
             assert(splash:wait(3))
            local entries = splash:history()
            local xml_data = splash:evaljs("document.getElementById('xmlData').defaultValue;")
            assert(splash:wait(0.5))
            return {html = splash:html(),url = splash:url(), xmldata = xml_data}
         end
                 """

script_lot_nojs = """
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
             splash:init_cookies(splash.args.cookies)
             assert(splash:go{
             splash.args.url,
             headers=splash.args.headers,
             http_method=splash.args.http_method,
             body=splash.args.body,
             })
             assert(splash:wait(3))
            local entries = splash:history()
            local xml_data = splash:evaljs("document.getElementById('xmlData').defaultValue;")
            assert(splash:wait(0.5))
            return {html = splash:html(),url = splash:url(), xmldata = xml_data}
         end
                 """

simle_script_lua = """
         function main(splash)
         splash:on_request(function(request)
             if request.url:find('css') then
                 request.abort()
                 end
             end)
             splash.images_enabled=false
             -- splash:autoload("https://code.jquery.com/jquery-1.7.1.min.js")
             splash.private_mode_enabled = false
             splash.plugins_enabled = false
             -- splash.js_enabled = true
             splash:init_cookies(splash.args.cookies)
	         assert(splash:wait(1))
             assert(splash:go{
             splash.args.url,  
             headers=splash.args.headers,
             http_method=splash.args.http_method,
             body=splash.args.body,
             })
             assert(splash:wait(4))
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

simle2_script_lua = """
         function main(splash)
         splash:on_request(function(request)
             if request.url:find('css') then
                 request.abort()
                 end
             end)
             splash.images_enabled=false
             -- splash:autoload("https://code.jquery.com/jquery-1.7.1.min.js")
             splash.private_mode_enabled = false
             splash.plugins_enabled = false
             splash.js_enabled = false
             splash:init_cookies(splash.args.cookies)
	         assert(splash:wait(1))
             assert(splash:go{
             splash.args.url,  
             headers=splash.args.headers,
             http_method=splash.args.http_method,
             body=splash.args.body,
             })
             assert(splash:wait(4))
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
headers = {
    ':authority': 'utp.sberbank-ast.ru',
    ':method': 'POST',
    ':path': '/Bankruptcy/SearchQuery/BidList',
    ':scheme': 'https',
    'accept': '*/*',
    #'accept-encoding': 'gzip, deflate, br',
    'accept-language': 'n-US,en;q=0.9,ru-RU;q=0.8,ru;q=0.7,de-DE;q=0.6,de;q=0.5,uk-UA;q=0.4,uk;q=0.3,ro-RO;q=0.2,ro;q=0.1',
    'cache-control': 'no-cache',
    'content-type': 'application/x-www-form-urlencoded',
    'origin': 'https://utp.sberbank-ast.ru',
    'referer': 'https://utp.sberbank-ast.ru/Bankruptcy/List/BidList',
    'pragma': 'no-cache',
    'sec-fetch-dest': 'empty',
    'sec-fetch-mode': 'cors',
    'sec-fetch-site': 'same-origin',
    'User-Agent': choice(agent_list),
    'x-requested-with': 'XMLHttpRequest',
}