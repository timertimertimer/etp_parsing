from app.utils.config import start_date

main_data_origin = "https://www.lot-online.ru/"
start_url = "https://zalog.lot-online.ru"
go_to_urls = {
    "sbrf": "https://zalog.lot-online.ru/sbrf",
    "rshb": "https://zalog.lot-online.ru/rshb",
    "rad": "https://zalog.lot-online.ru/rad",
}
organization_ids = {
    "sbrf": "754001",
    "rshb": "17711002",
    "rad": "763001",
}
data_pagination = {
    "keyWords": "",
    "publicationDateFrom": start_date,
    "publicationDateTo": "",
    "organization": "",
    "organizationId": "",
    "propertyTypeId": "",
    "priceFrom": "0",
    "priceTo": "10000000000",
    "countryCode": "",
    "regionCode": "",
    "districtCode": "",
    "cityCode": "",
    "propertyList": [],
    "metroName": "",
    "page": "1",
}
pagination_url = "https://zalog.lot-online.ru/collateral/catalog.rest"

# -*- coding: utf-8 -*-
script_lua = """
         function main(splash)
         splash:on_request(function(request)
             if request.url:find('css') then
                 request.abort()
                 end
             end)
             splash.images_enabled=false
             splash.private_mode_enabled = false
             splash.plugins_enabled = false
             splash.js_enabled = true
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

script_lua1 = """
         function main(splash)
         splash:on_request(function(request)
             if request.url:find('css') then
                 request.abort()
                 end
             end)
             splash.images_enabled=false
             splash.private_mode_enabled = true
             splash.js_enabled = true

	         assert(splash:wait(1))
             assert(splash:go{
             splash.args.url,  


             })
             assert(splash:wait(4))

             assert(splash:wait(2))
             return {


                 html = splash:html(),
                 }
         end
                 """
