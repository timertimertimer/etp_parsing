from random import choice
import requests
import shutil
SPLASH_DOWNLOAD = 'http://0.0.0.0:8054'
USER_AGENT = ["Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:76.0) Gecko/20100101 Firefox/76.0",
              "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.138 Safari/537.36",
              "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.149 Safari/537.36",
              "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.132 Safari/537.36",
              "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.138 Safari/537.36 OPR/68.0.3618.104"]

proxy_get = [
    'user43990:capfd6@2.59.51.45:8685',
    'user43990:capfd6@91.235.158.137:8685',
    'user43990:capfd6@91.241.181.139:8685',
    'user43990:capfd6@2.59.48.37:8685',
    'user43990:capfd6@5.182.117.34:8685',
    'user43990:capfd6@45.11.213.6:8685'
]
proxies = {
    'http': 'http://' + choice(proxy_get),
    'https': 'http://' + choice(proxy_get)

}
cookies ="ASP.NET_SessionId=iz0pa4jimgqrvq2x1q02nzt1; bankrotcookie=ad769f3b793af027a7518900a41e416e; MessageNumber=&MessageType=PropertyInventoryResult&MessageTypeText=%d0%9e%d1%82%d1%87%d0%b5%d1%82%20%d0%be%d1%86%d0%b5%d0%bd%d1%89%d0%b8%d0%ba%d0%b0%20%d0%be%d0%b1%20%d0%be%d1%86%d0%b5%d0%bd%d0%ba%d0%b5%20%d0%b8%d0%bc%d1%83%d1%89%d0%b5%d1%81%d1%82%d0%b2%d0%b0%20%d0%b4%d0%be%d0%bb%d0%b6%d0%bd%d0%b8%d0%ba%d0%b0&DateEndValue=09.10.2020+0%3a00%3a00&DateBeginValue=09.10.2020+0%3a00%3a00&PageNumber=0&DebtorText=&DebtorId=&DebtorType=&PublisherType=&PublisherId=&PublisherText=&IdRegion=&IdCourtDecisionType=&WithAu=False&WithViolation=False"
script_lua_request = """    treat = require("treat")
                            base64 = require("base64")
                              splash:on_request(function(request)
                                request:set_proxy{
                                host = '2.59.51.45',
                                port = 8685,
                                username = "user43990",
                                password = "capfd6",
                            }
                            end)
                                headers = {
                                    ['User-Agent'] = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.138 Safari/537.36'
                                }
                                splash:set_custom_headers(headers)
                                splash.images_enabled=false
                                splash.private_mode_enabled = false
                                splash.plugins_enabled = false
                                assert(splash:go(args.url))
                                assert(splash:wait(3.5))
                                return splash:html()
 
                                """

url = "https://bankrot.fedresurs.ru/Download/file.fo?guid=ca8f9118-3607-40a0-98f2-faa48e4f4ed8&type=MessageDocument"

session = requests.Session()
#session.proxies.update(proxies)
res = requests.post(url=f'{SPLASH_DOWNLOAD}/run', json={
    'lua_source': script_lua_request,
    'url': f'{url}'
})
print(res.content)
with open('test', 'wb') as f:
    res.raw.decode_content = True
    shutil.copyfileobj(res.raw, f)

 # html = splash:html(),
 #    png = splash:png(),
 #    har = splash:har(),