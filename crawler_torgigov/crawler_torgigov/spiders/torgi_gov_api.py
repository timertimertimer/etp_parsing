# import copy
# import logging
# from abc import ABC
# from random import choice
#
# import aiohttp
# from aiohttp_socks import ProxyConnector
# from icecream import ic
# from scrapy import Request, FormRequest
# from scrapy.http.cookies import CookieJar
# from scrapy.spiders import Spider
#
# from crawler_torgigov.utils.db import *
# from crawler_torgigov.utils.db_check_download import *
# from ..items import CrawlerTorgigovItem, CrawlerTorgigovItemLoader
# from ..manage_spider.aiohttp_manage import *
# from ..manage_spider.aiohttp_manage import ChangeLink
# from ..manage_spider.app import Combo
# from ..utils.config import government_link
#
# from ..utils.download import agent_list, socks_list_vip
# from ..utils.global_functions import GlobalFeatures
# from ..utils.headers import headers, headers_for_lot_page, short_headers
# from ..utils.work_with_text_and_number import cookie_parser
# from ..utils.working_with_time import return_parse_date
#
# logger = logging.getLogger(__name__)
#
#
# class TorgiGovApiSpider(Spider, ABC):
#     name = 'torgi_gov_api'
#
#     custom_settings = {
#         'LOG_FILE': './torgi_bankrot.log',
#         'LOG_LEVEL': 'INFO',
#         'DOWNLOADER_MIDDLEWARES': {
#             'crawler_torgigov.middlewares.CrawlerTorgigovDownloaderMiddleware': 543,
#             'rotating_proxies.middlewares.RotatingProxyMiddleware': 610,
#             'rotating_proxies.middlewares.BanDetectionMiddleware': 620,
#         },
#         'ITEM_PIPELINES': {
#             'crawler_torgigov.pipelines.CrawlerTorgigovPipeline': 300,
#             'crawler_torgigov.pipelines.TorgiGovConnectGovernment': 350,
#         }
#
#     }
#
#     def __init__(self):
#         super(TorgiGovApiSpider, self).__init__()
#
