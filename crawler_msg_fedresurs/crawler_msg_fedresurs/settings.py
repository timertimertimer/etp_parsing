# -*- coding: utf-8 -*-

# Scrapy settings for crawler_msg_fedresurs project
#
# For simplicity, this file contains only settings considered important or
# commonly used. You can find more settings consulting the documentation:
#
#     https://docs.scrapy.org/en/latest/topics/settings.html
#     https://docs.scrapy.org/en/latest/topics/downloader-middleware.html
#     https://docs.scrapy.org/en/latest/topics/spider-middleware.html
from crawler_msg_fedresurs.utils.config import headers_brow, SPLASH_URL_MSG, path_to_proxy

BOT_NAME = 'crawler_msg_fedresurs'

SPIDER_MODULES = ['crawler_msg_fedresurs.spiders']
NEWSPIDER_MODULE = 'crawler_msg_fedresurs.spiders'

USER_AGENT = headers_brow['User-Agent']

DEFAULT_REQUESTS_HEADERS = {
    ':authority': 'bankrot.fedresurs.ru',
    ':method': 'GET',
    ':path': '/',
    ':scheme': 'https',
    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
    'accept-encoding': 'gzip, deflate, br',
    'accept-language': 'en-US,en;q=0.9,ru-RU;q=0.8,ru;q=0.7,de-DE;q=0.6,de;q=0.5,uk-UA;q=0.4,uk;q=0.3,ro-RO;q=0.2,ro;q=0.1',
    'cache-control': 'no-cache',
    'dnt': '1',
    'pragma': 'no-cache',
    'sec-fetch-dest': 'document',
    'sec-fetch-mode': 'navigate',
    'sec-fetch-site': 'none',
    'upgrade-insecure-requests': '1',
    'User-Agent': USER_AGENT,

}
# CONCURRENT_REQUESTS = 1


SPLASH_URL = SPLASH_URL_MSG
SPIDER_MIDDLEWARES = {
    'scrapy_splash.SplashDeduplicateArgsMiddleware': 100,
    #'crawler_msg_fedresurs.middlewares.CrawlerMsgFedresursSpiderMiddleware': 543,
}

ROTATING_PROXY_LIST_PATH = path_to_proxy
ROTATING_PROXY_LOGSTATS_INTERVAL = 60
ROTATING_PROXY_PAGE_RETRY_TIMES = 2


# Disable cookies (enabled by default)
COOKIES_ENABLED = False

DOWNLOADER_MIDDLEWARES = {
    'crawler_msg_fedresurs.middlewares.UserAgentMiddleware': 500,
    'rotating_proxies.middlewares.RotatingProxyMiddleware': 610,
    'rotating_proxies.middlewares.BanDetectionMiddleware': 620,
    'scrapy_splash.SplashCookiesMiddleware': 723,
    'scrapy_splash.SplashMiddleware': 725,
    'scrapy.downloadermiddlewares.httpcompression.HttpCompressionMiddleware': 810,
}

LOG_LEVEL = 'INFO'
# LOG_FILE = 'fedres_msg.log'
LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'

RETRY_ENABLED = True
RETRY_TIMES = 20
RETRY_HTTP_CODES = [500, 502, 503, 504, 501, 522, 524, 408, 429, 407, 403, 404, 400, 401, 498]

# Enable or disable extensions
# See https://docs.scrapy.org/en/latest/topics/extensions.html
#EXTENSIONS = {
#    'scrapy.extensions.telnet.TelnetConsole': None,
#}

# Configure item pipelines
# See https://docs.scrapy.org/en/latest/topics/item-pipeline.html
ITEM_PIPELINES = {
   'crawler_msg_fedresurs.pipelines.CrawlerMsgFedresursPipeline': 300,
   'crawler_msg_fedresurs.pipelines.CrawlerDbConnect': 350,
}

# Enable and configure the AutoThrottle extension (disabled by default)
# See https://docs.scrapy.org/en/latest/topics/autothrottle.html
AUTOTHROTTLE_ENABLED = True
# The initial download delay
AUTOTHROTTLE_START_DELAY = 5
# The maximum download delay to be set in case of high latencies
AUTOTHROTTLE_MAX_DELAY = 90
# The average number of requests Scrapy should be sending in parallel to
# each remote server
AUTOTHROTTLE_TARGET_CONCURRENCY = 2
# Enable showing throttling stats for every response received:
AUTOTHROTTLE_DEBUG = False

SPLASH_COOKIES_DEBUG = False
SPLASH_LOG_400 = True
DUPEFILTER_CLASS = 'scrapy_splash.SplashAwareDupeFilter'
#HTTPCACHE_ENABLED = True
#HTTPCACHE_EXPIRATION_SECS = 0
#HTTPCACHE_DIR = 'httpcache'
#HTTPCACHE_IGNORE_HTTP_CODES = []
#HTTPCACHE_STORAGE = 'scrapy.extensions.httpcache.FilesystemCacheStorage'
