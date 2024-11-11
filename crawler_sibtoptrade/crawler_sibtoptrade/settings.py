# -*- coding: utf-8 -*-

# Scrapy settings for crawler_sibtoptrade project
#
# For simplicity, this file contains only settings considered important or
# commonly used. You can find more settings consulting the documentation:
#
#     https://docs.scrapy.org/en/latest/topics/settings.html
#     https://docs.scrapy.org/en/latest/topics/downloader-middleware.html
#     https://docs.scrapy.org/en/latest/topics/spider-middleware.html
from .config import headers_brow, Referer, path_to_proxy

BOT_NAME = 'crawler_sibtoptrade'

SPIDER_MODULES = ['crawler_sibtoptrade.spiders']
NEWSPIDER_MODULE = 'crawler_sibtoptrade.spiders'


USER_AGENT = headers_brow['User-Agent']
DEFAULT_REQUESTS_HEADERS = {

    'Accept': 'application/json, text/javascript, */*; q=0.01',
    'Accept-Encoding': 'gzip, deflate, br',
    'Accept-Language ': 'en-US,en;q=0.9,ru-RU;q=0.8,ru;q=0.7,de-DE;q=0.6,de;q=0.5,uk-UA;q=0.4,uk;q=0.3,ro-RO;q=0.2,ro;q=0.1',
    'Cache-Control': 'no-cache',
    'Connection': 'keep-alive',
    'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
    'DNT': '1',
    'Host': 'sibtoptrade.ru',
    'Origin': 'https://sibtoptrade.ru',
    'Pragma': 'no-cache',
    'Referer': Referer,
    'Sec-Fetch-Dest': 'empty',
    'Sec-Fetch-Mode': 'cors',
    'Sec-Fetch-Site': 'same-origin',
    'User-Agent': USER_AGENT,
}
# Crawl respon
# Crawl responsibly by identifying yourself (and your website) on the user-agent
#USER_AGENT = 'crawler_kartoteka (+http://www.yourdomain.com)'

# Obey robots.txt rules
ROBOTSTXT_OBEY = False

# Configure maximum concurrent requests performed by Scrapy (default: 16)
#CONCURRENT_REQUESTS = 32

# Configure a delay for requests for the same website (default: 0)
# See https://docs.scrapy.org/en/latest/topics/settings.html#download-delay
# See also autothrottle settings and docs
DOWNLOAD_DELAY = 3
# The download delay setting will honor only one of:
CONCURRENT_REQUESTS_PER_DOMAIN = 1
CONCURRENT_REQUESTS_PER_IP = 1

# LOG_LEVEL = 'INFO'
# LOG_FILE = './sibtoptrade.log'
LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'

SPLASH_URL = 'http://localhost:8065'
SPIDER_MIDDLEWARES = {
    'scrapy_splash.SplashDeduplicateArgsMiddleware': 100,
}

DOWNLOADER_MIDDLEWARES = {
    'crawler_sibtoptrade.middlewares.UserAgentMiddleware': 500,
    'rotating_proxies.middlewares.RotatingProxyMiddleware': 610,
    'rotating_proxies.middlewares.BanDetectionMiddleware': 620,
    'scrapy_splash.SplashCookiesMiddleware': 723,
    'scrapy_splash.SplashMiddleware': 725,
    'scrapy.downloadermiddlewares.httpcompression.HttpCompressionMiddleware': 810,
    'crawler_sibtoptrade.middlewares.CookiesMiddleware': 820,
}
ROTATING_PROXY_LIST_PATH = path_to_proxy
ROTATING_PROXY_LOGSTATS_INTERVAL = 60
ROTATING_PROXY_PAGE_RETRY_TIMES = 10
# Enable or disable extensions
# See https://docs.scrapy.org/en/latest/topics/extensions.html
# EXTENSIONS = {
#    'scrapy.extensions.telnet.TelnetConsole': None,
# }

# Configure item pipelines
# See https://docs.scrapy.org/en/latest/topics/item-pipeline.html
ITEM_PIPELINES = {
    'crawler_sibtoptrade.pipelines.CrawlerSibtoptradePipeline': 300,
    'crawler_sibtoptrade.pipelines.CrawlerDbConnect': 350,
}

RETRY_ENABLED = True
RETRY_TIMES = 10
RETRY_HTTP_CODES = [500, 502, 503, 504, 522, 524, 408, 429, 407, 403, 404, 400]

# Enable and configure the AutoThrottle extension (disabled by default)
# See https://docs.scrapy.org/en/latest/topics/autothrottle.html
AUTOTHROTTLE_ENABLED = True
# The initial download delay
AUTOTHROTTLE_START_DELAY = 3
# The maximum download delay to be set in case of high latencies
AUTOTHROTTLE_MAX_DELAY = 90
# The average number of requests Scrapy should be sending in parallel to
# each remote server
AUTOTHROTTLE_TARGET_CONCURRENCY = 1.0
# Enable showing throttling stats for every response received:
AUTOTHROTTLE_DEBUG = False

# Enable and configure HTTP caching (disabled by default)
# See https://docs.scrapy.org/en/latest/topics/downloader-middleware.html#httpcache-middleware-settings
SPLASH_COOKIES_DEBUG = True
SPLASH_LOG_400 = True
DUPEFILTER_CLASS = 'scrapy_splash.SplashAwareDupeFilter'
HTTPCACHE_ENABLED = True
HTTPCACHE_EXPIRATION_SECS = 120
#HTTPCACHE_DIR = 'httpcache'
#HTTPCACHE_IGNORE_HTTP_CODES = []
HTTPCACHE_STORAGE = 'scrapy_splash.SplashAwareFSCacheStorage'
