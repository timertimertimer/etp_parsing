from random import choice

from crawler_lot_online_zalog.utils.config import agent_list

headers_category = {
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,'
              '*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
    'Accept-Encoding': 'gzip, deflate, br',
    'Accept-Language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7',
    'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
    'Connection': 'keep-alive',
    'Faces-Request': 'partial/ajax',
    'Cookie': '',
    'Host': 'sales.lot-online.ru',
    'Origin': 'https://sales.lot-online.ru',
    'Pragma': 'no-cache',
    'Referer': '',
    'Sec-Fetch-Dest': 'empty',
    'Sec-Fetch-Mode': 'cors',
    'Sec-Fetch-Site': 'same-origin',
    'sec-gpc': '1',
    'X-Requested-With': 'XMLHttpRequest',
    'User-Agent': choice(agent_list)
}

headers_filter = {
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,'
              '*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
    'Accept-Encoding': 'gzip, deflate, br',
    'Accept-Language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7',
    'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
    'Faces-Request': 'partial/ajax',
    'Cache-Control': 'no-cache',
    'Connection': 'keep-alive',
    'Cookie': '',
    'Host': 'sales.lot-online.ru',
    'Origin': 'https://sales.lot-online.ru',
    'Pragma': 'no-cache',
    'Referer': '',
    'Sec-Fetch-Dest': 'document',
    'Sec-Fetch-Mode': 'navigate',
    'Sec-Fetch-Site': 'same-origin',
    'Sec-Fetch-User': '?1',
    'sec-gpc': '1',
    'Upgrade-Insecure-Requests': '1',
    'User-Agent': choice(agent_list)
}

headers_lot = {
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
    'Accept-Encoding': 'gzip, deflate, br',
    'Accept-Language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7',
    'Cache-Control': 'no-cache',
    'Connection': 'keep-alive',
    'Cookie': '',
    'Host': 'sales.lot-online.ru',
    'Pragma': ' no-cache',
    'Referer': '',
    'Sec-Fetch-Dest': 'document',
    'Sec-Fetch-Mode': 'navigate',
    'Sec-Fetch-Site': 'same-origin',
    'Sec-Fetch-User': '?1',
    'sec-gpc': '1',
    'Upgrade-Insecure-Requests': '1',
    'User-Agent': choice(agent_list)
}
