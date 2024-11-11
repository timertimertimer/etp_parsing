# -*- coding: utf-8 -*-

# Scrapy settings for crawler_sistematorg project
#
# For simplicity, this file contains only settings considered important or
# commonly used. You can find more settings consulting the documentation:
#
#     https://docs.scrapy.org/en/latest/topics/settings.html
#     https://docs.scrapy.org/en/latest/topics/downloader-middleware.html
#     https://docs.scrapy.org/en/latest/topics/spider-middleware.html
from .config import headers_brow, reffer, path_to_proxy


BOT_NAME = 'crawler_sistematorg'

SPIDER_MODULES = ['crawler_sistematorg.spiders']
NEWSPIDER_MODULE = 'crawler_sistematorg.spiders'

USER_AGENT = headers_brow['User-Agent']
DEFAULT_REQUESTS_HEADERS = {

    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
    'Accept-Encoding': 'gzip,deflate,br',
    'Accept-Language': 'en-US,en;q=0.9,ru-RU;q=0.8,ru;q=0.7,de-DE;q=0.6,de;q=0.5,uk-UA;q=0.4,uk;q=0.3,ro-RO;q=0.2,ro;q=0.1',
    'Cache-Control': 'no-cache',
    'Connection': 'keep-alive',
    'DNT': ' 1',
    'Host': 'sistematorg.com',
    'Pragma': 'no-cache',
    'Referer: https': reffer,
    'Sec-Fetch-Dest': 'document',
    'Sec-Fetch-Mode': 'navigate',
    'Sec-Fetch-Site': 'same-origin',
    'Sec-Fetch-User': '?1',
    'Upgrade-Insecure-Requests': '1',
    'User-Agent': USER_AGENT
        }

# Crawl responsibly by identifying yourself (and your website) on the user-agent
#USER_AGENT = 'crawler_sistematorg +http://www.yourdomain.com)'

# Obey robots.txt rules
ROBOTSTXT_OBEY = False
# LOG_FILE = 'sistematorg.log'
# LOG_LEVEL= 'INFO'
#
#MAIL_FROM = 'xxxxxxxxxx@outlook.com'
#MAIL_HOST = 'smtp.office365.com'
#MAIL_PORT = 587
#MAIL_USER = 'xxxxxxxxxxxxx@outlook.com'
#MAIL_PASS = 'xxxxxxxxxxxxxx'
#MAIL_TLS = True

# Configure maximum concurrent requests performed by Scrapy (default: 16)
CONCURRENT_REQUESTS = 1

# Configure a delay for requests for the same website (default: 0)
# See https://docs.scrapy.org/en/latest/topics/settings.html#download-delay
# See also autothrottle settings and docs
#DOWNLOAD_DELAY = 3
# The download delay setting will honor only one of:
CONCURRENT_REQUESTS_PER_DOMAIN = 1
CONCURRENT_REQUESTS_PER_IP = 1

# Disable cookies (enabled by default)


# Disable Telnet Console (enabled by default)
#TELNETCONSOLE_ENABLED = False


# Override the default request headers:
#DEFAULT_REQUEST_HEADERS = {
#   'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
#   'Accept-Language': 'en',
#}

# Enable or disable spider middlewares
# See https://docs.scrapy.org/en/latest/topics/spider-middleware.html
#SPIDER_MIDDLEWARES = {
#    'crawler_ruson.middlewares.CrawlerRusonSpiderMiddleware': 543,
#}

# Enable or disable downloader middlewares
# See https://docs.scrapy.org/en/latest/topics/downloader-middleware.html

COOKIES_ENABLED = True
COOKIES_PERSISTENCE = True
COOKIES_PERSISTENCE_DIR = './cookies'
DOWNLOADER_MIDDLEWARES = {
    'rotating_proxies.middlewares.RotatingProxyMiddleware': 610,
    'rotating_proxies.middlewares.BanDetectionMiddleware': 620,
    'crawler_sistematorg.middlewares.UserAgentMiddleware':100,
    'scrapy.downloadermiddlewares.cookies.CookiesMiddleware': None,
    'scrapy_cookies.downloadermiddlewares.cookies.CookiesMiddleware': 700,

}
# COOKIES_STORAGE = 'scrapy_cookies.storage.sqlite.SQLiteStorage'
# COOKIES_SQLITE_DATABASE = ':memory:'
ROTATING_PROXY_LIST_PATH = path_to_proxy
ROTATING_PROXY_LOGSTATS_INTERVAL = 60
ROTATING_PROXY_PAGE_RETRY_TIMES = 10
# Enable or disable extensions
# See https://docs.scrapy.org/en/latest/topics/extensions.html
#EXTENSIONS = {
#    'scrapy.extensions.telnet.TelnetConsole': None,
#}

# Configure item pipelines
# See https://docs.scrapy.org/en/latest/topics/item-pipeline.html
ITEM_PIPELINES = {
    'crawler_sistematorg.pipelines.CrawlerSistematorgPipeline': 300,
    'crawler_sistematorg.pipelines.CrawlerDbConnect' : 500,
}

RETRY_ENABLED =True
RETRY_TIMES = 10
RETRY_HTTP_CODES = [500, 502, 503, 504, 522, 524, 408, 429, 407, 403, 404, 400]


AUTOTHROTTLE_ENABLED = True
# The initial download delay
AUTOTHROTTLE_START_DELAY = 5
# The maximum download delay to be set in case of high latencies
AUTOTHROTTLE_MAX_DELAY = 60
# The average number of requests Scrapy should be sending in parallel to
# each remote server
AUTOTHROTTLE_TARGET_CONCURRENCY = 1.0
# Enable showing throttling stats for every response received:
AUTOTHROTTLE_DEBUG = False

# Enable and configure HTTP caching (disabled by default)
# See https://docs.scrapy.org/en/latest/topics/downloader-middleware.html#httpcache-middleware-settings
HTTPCACHE_ENABLED = True
HTTPCACHE_EXPIRATION_SECS = 10
#HTTPCACHE_DIR = 'httpcache'
HTTPCACHE_IGNORE_HTTP_CODES = [403, 407, 500, 502, 503]
HTTPCACHE_STORAGE = 'scrapy.extensions.httpcache.FilesystemCacheStorage'