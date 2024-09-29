from random import choice
from .config import agent_list
headers = {
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
    'Accept-Encoding': 'gzip, deflate, br',
    'Accept-Language ': 'ru-RU,ru;q=0.9',
    'Cache-Control': 'no-cache',
    'Connection': 'keep-alive',
    'DNT': '1',
    'Host': 'etp.kartoteka.ru',
    'Pragma': 'no-cache',
    'Referer': '',
    'Sec-Fetch-Dest': 'document',
    'Sec-Fetch-Mode': 'navigate',
    'Sec-Fetch-Site': 'same-site',
    'Sec-Fetch-User': ' ?1',
    'Upgrade-Insecure-Requests': '1',
    'User-Agent': choice(agent_list),
}
