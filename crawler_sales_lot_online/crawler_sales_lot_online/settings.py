# -*- coding: utf-8 -*-

# Scrapy settings for crawler_sales_lot_online project
#
# For simplicity, this file contains only settings considered important or
# commonly used. You can find more settings consulting the documentation:
#
#     https://docs.scrapy.org/en/latest/topics/settings.html
#     https://docs.scrapy.org/en/latest/topics/downloader-middleware.html
#     https://docs.scrapy.org/en/latest/topics/spider-middleware.html
from crawler_sales_lot_online.utils.config import headers_brow, Referer, path_to_proxy

BOT_NAME = 'crawler_sales_lot_online'

SPIDER_MODULES = ['crawler_sales_lot_online.spiders']
NEWSPIDER_MODULE = 'crawler_sales_lot_online.spiders'

USER_AGENT = headers_brow['User-Agent']
ROBOTSTXT_OBEY = False

CONCURRENT_REQUESTS = 2

# DOWNLOAD_DELAY = 2.5
# The download delay setting will honor only one of:
# CONCURRENT_REQUESTS_PER_DOMAIN = 1
# CONCURRENT_REQUESTS_PER_IP = 1

# Disable cookies (enabled by default)
COOKIES_ENABLED = True


DEFAULT_REQUESTS_HEADERS = {

    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,'
              '*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
    'Accept-Encoding': 'gzip, deflate, br',
    'Accept-Language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7',
    'Cache-Control': 'no-cache',
    'Connection': 'keep-alive',
    'Host': 'sales.lot-online.ru',
    'Pragma': 'no-cache',
    'Referer': Referer,
    'Sec-Fetch-Dest': 'document',
    'Sec-Fetch-Mode': 'navigate',
    'Sec-Fetch-Site': 'none',
    'Upgrade-Insecure-Requests': '1',
    'User-Agent': USER_AGENT,
}

# LOG_LEVEL = 'INFO'
# LOG_FILE = 'lot_online.log'
LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'

# Enable or disable spider middlewares
# See https://docs.scrapy.org/en/latest/topics/spider-middleware.html
# SPIDER_MIDDLEWARES = {
#    'crawler_sales_lot_online.middlewares.CrawlerSalesLotOnlineSpiderMiddleware': 543,
# }
SPLASH_URL = 'http://localhost:8050'
SPIDER_MIDDLEWARES = {
    'scrapy_splash.SplashDeduplicateArgsMiddleware': 100,
}

DOWNLOADER_MIDDLEWARES = {
    'crawler_sales_lot_online.middlewares.UserAgentMiddleware': 500,
    'rotating_proxies.middlewares.RotatingProxyMiddleware': 610,
    'rotating_proxies.middlewares.BanDetectionMiddleware': 620,
    'scrapy_splash.SplashCookiesMiddleware': 723,
    'scrapy_splash.SplashMiddleware': 725,
    'scrapy.downloadermiddlewares.httpcompression.HttpCompressionMiddleware': 810,
    # 'crawler_sales_lot_online.middlewares.CookiesMiddleware': 120,
    # 'crawler_sales_lot_online.middlewares.CrawlerSalesLotOnlineSpiderMiddleware': 150,

}

ROTATING_PROXY_LIST_PATH = path_to_proxy
ROTATING_PROXY_LOGSTATS_INTERVAL = 60
ROTATING_PROXY_PAGE_RETRY_TIMES = 15

ITEM_PIPELINES = {
    'crawler_sales_lot_online.pipelines.CrawlerLotOnlinePipeline': 300,
    'crawler_sales_lot_online.pipelines.CrawlerDbConnect': 350,
}
RETRY_ENABLED = True
RETRY_TIMES = 21
RETRY_HTTP_CODES = [500, 502, 503, 504, 522,
                    524, 408, 429, 407, 403, 404, 400, 401, 498]
# Enable and configure the AutoThrottle extension (disabled by default)
# See https://docs.scrapy.org/en/latest/topics/autothrottle.html
AUTOTHROTTLE_ENABLED = True
# The initial download delay
AUTOTHROTTLE_START_DELAY = 6
# The maximum download delay to be set in case of high latencies
AUTOTHROTTLE_MAX_DELAY = 90
# The average number of requests Scrapy should be sending in parallel to
# each remote server
AUTOTHROTTLE_TARGET_CONCURRENCY = 1.5
# Enable showing throttling stats for every response received:
AUTOTHROTTLE_DEBUG = False

# Enable and configure HTTP caching (disabled by default)
# See https://docs.scrapy.org/en/latest/topics/downloader-middleware.html#httpcache-middleware-settings
SPLASH_COOKIES_DEBUG = False
SPLASH_LOG_400 = True
DUPEFILTER_CLASS = 'scrapy_splash.SplashAwareDupeFilter'
# HTTPCACHE_ENABLED = False
# HTTPCACHE_EXPIRATION_SECS = 300
# HTTPCACHE_DIR = 'httpcache'
# HTTPCACHE_IGNORE_HTTP_CODES = [407]
# HTTPCACHE_STORAGE = 'scrapy_splash.SplashAwareFSCacheStorage'
