from .utils.config import headers_brow, path_to_proxy

BOT_NAME = 'crawler_sberbank'

SPIDER_MODULES = ['crawler_sberbank.spiders']
NEWSPIDER_MODULE = 'crawler_sberbank.spiders'

USER_AGENT = headers_brow['User-Agent']

ROBOTSTXT_OBEY = False

# CONCURRENT_REQUESTS = 1

# DOWNLOAD_DELAY = 5
# The download delay setting will honor only one of:
# CONCURRENT_REQUESTS_PER_DOMAIN = 1
# CONCURRENT_REQUESTS_PER_IP = 1

# Disable cookies (enabled by default)
COOKIES_ENABLED = False
DEFAULT_REQUESTS_HEADERS = {
    ':authority': 'utp.sberbank-ast.ru',
    ':method': 'GET',
    ':path': '/Bankruptcy/SearchQuery/BidList',
    ':scheme': 'https',
    'accept': '*/*',
    # 'accept-encoding': 'gzip, deflate, br, sdch',
    'accept-language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7',
    'cache-control': 'no-cache',
    'origin': 'https://utp.sberbank-ast.ru',
    'referer': 'https://utp.sberbank-ast.ru/Bankruptcy/List/BidList',
    'pragma': 'no-cache',
    'sec-fetch-dest': 'empty',
    'sec-fetch-mode': 'cors',
    'sec-fetch-site': 'same-origin',
    'User-Agent': USER_AGENT,
    'x-requested-with': 'XMLHttpRequest',

}
# LOG_LEVEL = 'INFO'
# LOG_FILE = './sberbank.log'
LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'

SPLASH_URL = 'http://localhost:8050/'
# SPLASH_URL = 'http://172.21.0.7:8050'
SPIDER_MIDDLEWARES = {
    'scrapy_splash.SplashDeduplicateArgsMiddleware': 100,
}

DOWNLOADER_MIDDLEWARES = {
    'crawler_sberbank.middlewares.UserAgentMiddleware': 500,
    'rotating_proxies.middlewares.RotatingProxyMiddleware': 610,
    'rotating_proxies.middlewares.BanDetectionMiddleware': 620,
    'scrapy_splash.SplashCookiesMiddleware': 723,
    'scrapy_splash.SplashMiddleware': 725,
    'scrapy.downloadermiddlewares.httpcompression.HttpCompressionMiddleware': 810,
    # 'crawler_sberbank.middlewares.CookiesMiddleware': 120,
    # 'crawler_sberbank.middlewares.CrawlerSberbankDownloaderMiddleware': 150,

}

ROTATING_PROXY_LIST_PATH = path_to_proxy
ROTATING_PROXY_LOGSTATS_INTERVAL = 60
ROTATING_PROXY_PAGE_RETRY_TIMES = 2

ITEM_PIPELINES = {
    'crawler_sberbank.pipelines.CrawlerSberbankPipeline': 300,
    'crawler_sberbank.pipelines.CrawlerDbConnect': 350,
}

RETRY_ENABLED = True
RETRY_TIMES = 20
RETRY_HTTP_CODES = [500, 502, 503, 504, 522, 524, 408, 429, 407, 403, 404, 400, 401]
# Enable and configure the AutoThrottle extension (disabled by default)
# See https://docs.scrapy.org/en/latest/topics/autothrottle.html
AUTOTHROTTLE_ENABLED = True
# The initial download delay
AUTOTHROTTLE_START_DELAY = 6
# The maximum download delay to be set in case of high latencies
AUTOTHROTTLE_MAX_DELAY = 120
# The average number of requests Scrapy should be sending in parallel to
# each remote server
AUTOTHROTTLE_TARGET_CONCURRENCY = 1.0
# Enable showing throttling stats for every response received:
AUTOTHROTTLE_DEBUG = False

# Enable and configure HTTP caching (disabled by default)
# See https://docs.scrapy.org/en/latest/topics/downloader-middleware.html#httpcache-middleware-settings
SPLASH_COOKIES_DEBUG = False
SPLASH_LOG_400 = True
DUPEFILTER_CLASS = 'scrapy_splash.SplashAwareDupeFilter'
# HTTPCACHE_ENABLED = False
# HTTPCACHE_EXPIRATION_SECS = 120
# HTTPCACHE_DIR = 'httpcache'
# HTTPCACHE_IGNORE_HTTP_CODES = [407, 504]
# HTTPCACHE_STORAGE = 'scrapy_splash.SplashAwareFSCacheStorage'
