# -*- coding: utf-8 -*-
from crawler_alfalot.utils.headers_for_spiders.generate_user_agent import USER_AGENT


headers_alfalot = {
    # ':authority': 'bankrupt.alfalot.ru',
    # ':method': 'GET',
    # ':scheme': 'https',
    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
    'accept-encoding': 'gzip, deflate, br',
    'accept-language': 'ru-RU,ru;q=0.9',
    'cache-control': 'no-cache',
    'connection': 'keep-alive',
    'pragma': 'no-cache',
    'sec-fetch-dest': 'document',
    'sec-fetch-mode': 'navigate',
    'sec-fetch-site': 'none',
    'sec-fetch-user': '?1',
    'upgrade-insecure-requests': '1',
    'User-Agent': USER_AGENT
}
