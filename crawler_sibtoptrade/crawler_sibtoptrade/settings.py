from general_utils.settings import *

BOT_NAME = 'crawler_sibtoptrade'

SPIDER_MODULES = ['crawler_sibtoptrade.spiders']
NEWSPIDER_MODULE = 'crawler_sibtoptrade.spiders'
# DOWNLOAD_DELAY = 3
# CONCURRENT_REQUESTS_PER_DOMAIN = 1
# CONCURRENT_REQUESTS_PER_IP = 1

# LOG_FILE = 'sibtoptrade.log'
DEFAULT_REQUEST_HEADERS.pop('Accept-Encoding')
DOWNLOADER_MIDDLEWARES = DOWNLOADER_MIDDLEWARES | {
    'scrapy_splash.SplashCookiesMiddleware': 723,
    'scrapy_splash.SplashMiddleware': 725,
}

HTTPCACHE_ENABLED = True
HTTPCACHE_EXPIRATION_SECS = 120
HTTPCACHE_STORAGE = 'scrapy_splash.SplashAwareFSCacheStorage'
