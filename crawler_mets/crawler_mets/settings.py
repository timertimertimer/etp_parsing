# -*- coding: utf-8 -*-

# Scrapy settings for crawler_mets project
#
# For simplicity, this file contains only settings considered important or
# commonly used. You can find more settings consulting the documentation:
#
#     https://docs.scrapy.org/en/latest/topics/settings.html
#     https://docs.scrapy.org/en/latest/topics/downloader-middleware.html
#     https://docs.scrapy.org/en/latest/topics/spider-middleware.html
from random import choice

from .utils.config import referer, agent_list, path_to_proxy

BOT_NAME = 'crawler_mets'

SPIDER_MODULES = ['crawler_mets.spiders']
NEWSPIDER_MODULE = 'crawler_mets.spiders'

DOWNLOAD_HANDLERS = {
    "http": "scrapy_playwright.handler.ScrapyPlaywrightDownloadHandler",
    "https": "scrapy_playwright.handler.ScrapyPlaywrightDownloadHandler",
}
TWISTED_REACTOR = "twisted.internet.asyncioreactor.AsyncioSelectorReactor"

# Crawl responsibly by identifying yourself (and your website) on the user-agent
USER_AGENT = choice(agent_list)

# Obey robots.txt rules
ROBOTSTXT_OBEY = False

# CONCURRENT_REQUESTS = 1

# DOWNLOAD_DELAY = 7
# The download delay setting will honor only one of:
# CONCURRENT_REQUESTS_PER_DOMAIN = 1
# CONCURRENT_REQUESTS_PER_IP = 1

# Disable cookies (enabled by default)
# COOKIES_ENABLED = False
# COOKIES_DEBUG = True

DEFAULT_REQUESTS_HEADERS = {
    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
    'accept-encoding': 'gzip, deflate, br',
    'accept-language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7',
    'cache-control': 'no-cache',
    'origin': 'www.m-ets.ru',
    'pragma': 'no-cache',
    'sec-fetch-dest': 'empty',
    'sec-fetch-mode': 'navigate',
    'sec-fetch-site': 'same-origin',
    'referer': referer,
    'upgrade-insecure-requests': '1',
    'User-Agent': USER_AGENT
}
# LOG_LEVEL = 'ERROR'
# LOG_FILE = './mets.log'
LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'


#SPLASH_URL = 'http://172.20.0.7:8050/'
SPLASH_URL = 'http://localhost:8050/'
SPIDER_MIDDLEWARES = {
    'scrapy_splash.SplashDeduplicateArgsMiddleware': 100,
}

# Enable or disable spider middlewares
# See https://docs.scrapy.org/en/latest/topics/spider-middleware.html
# SPIDER_MIDDLEWARES = {
#    'crawler_mets.middlewares.CrawlerMetsSpiderMiddleware': 543,
# }

# Enable or disable downloader middlewares
# See https://docs.scrapy.org/en/latest/topics/downloader-middleware.html

DOWNLOADER_MIDDLEWARES = {
    'crawler_mets.middlewares.UserAgentMiddleware': 100,
    'rotating_proxies.middlewares.RotatingProxyMiddleware': 610,
    'rotating_proxies.middlewares.BanDetectionMiddleware': 620,
    'scrapy_splash.SplashCookiesMiddleware': 723,
    'scrapy_splash.SplashMiddleware': 725,
    'scrapy.downloadermiddlewares.httpcompression.HttpCompressionMiddleware': 810,
    # 'crawler_mets.middlewares.CookiesMiddleware': 120,
    'crawler_mets.middlewares.CrawlerMetsDownloaderMiddleware': 150,

}
ROTATING_PROXY_LIST_PATH = path_to_proxy
ROTATING_PROXY_LOGSTATS_INTERVAL = 60
ROTATING_PROXY_PAGE_RETRY_TIMES = 10

ITEM_PIPELINES = {
    'crawler_mets.pipelines.CrawlerMetsPipeline': 300,
    'crawler_mets.pipelines.CrawlerDbConnect': 350,
}

RETRY_ENABLED = True
RETRY_TIMES = 19
RETRY_HTTP_CODES = [500, 502, 503, 504,  522,
                    524, 408, 429, 407, 403, 404, 400, 401]
# Enable and configure the AutoThrottle extension (disabled by default)
# See https://docs.scrapy.org/en/latest/topics/autothrottle.html
AUTOTHROTTLE_ENABLED = True
# The initial download delay
AUTOTHROTTLE_START_DELAY = 12
# The maximum download delay to be set in case of high latencies
AUTOTHROTTLE_MAX_DELAY = 180
# The average number of requests Scrapy should be sending in parallel to
# each remote server
AUTOTHROTTLE_TARGET_CONCURRENCY = 1.0
# Enable showing throttling stats for every response received:
AUTOTHROTTLE_DEBUG = False


SPLASH_COOKIES_DEBUG = False
SPLASH_LOG_400 = True
DUPEFILTER_CLASS = 'scrapy_splash.SplashAwareDupeFilter'
# HTTPCACHE_ENABLED = False
# HTTPCACHE_EXPIRATION_SECS = 600
# #HTTPCACHE_DIR = 'httpcache'
# #HTTPCACHE_IGNORE_HTTP_CODES = [407]
# HTTPCACHE_STORAGE = 'scrapy_splash.SplashAwareFSCacheStorage'
