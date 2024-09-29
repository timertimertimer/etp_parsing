from crawler_fabricant.utils.config import headers_brow, Referer, path_to_proxy

BOT_NAME = 'crawler_fabricant'

SPIDER_MODULES = ['crawler_fabricant.spiders']
NEWSPIDER_MODULE = 'crawler_fabricant.spiders'

# Crawl responsibly by identifying yourself (and your website) on the user-agent
USER_AGENT = headers_brow['User-Agent']

ROBOTSTXT_OBEY = False

CONCURRENT_REQUESTS = 2

DOWNLOAD_DELAY = 3
# The download delay setting will honor only one of:
CONCURRENT_REQUESTS_PER_DOMAIN = 2
CONCURRENT_REQUESTS_PER_IP = 2

# Disable cookies (enabled by default)
COOKIES_ENABLED = True
# COOKIES_DEBUG = True

# Override the default request headers:
DEFAULT_REQUESTS_HEADERS = {

    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,'
              'application/signed-exchange;v=b3;q=0.9',
    'Accept-Encoding': 'gzip, deflate, br',
    'Accept-Language': 'en-US,en;q=0.9,ru-RU;q=0.8,ru;q=0.7,de-DE;q=0.6,de;q=0.5,uk-UA;q=0.4,uk;q=0.3,'
                       'ro-RO;q=0.2,ro;q=0.1',
    'Cache-Control': 'no-cache',
    'Connection': 'keep-alive',
    'DNT': '1',
    'Host': 'www.fabrikant.ru',
    'Pragma': 'no-cache',
    'Referer': Referer,
    'Sec-Fetch-Dest': 'document',
    'Sec-Fetch-Mode': 'navigate',
    'Sec-Fetch-Site': 'same-origin',
    'Sec-Fetch-User': '?1',
    'User-Agent': USER_AGENT,
}

LOG_LEVEL = 'DEBUG'
LOG_FILE = './fabricant.log'
LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'

SPLASH_URL = 'http://localhost:8049'
SPIDER_MIDDLEWARES = {
    'scrapy_splash.SplashDeduplicateArgsMiddleware': 100,
}

DOWNLOADER_MIDDLEWARES = {
    'crawler_fabricant.middlewares.UserAgentMiddleware': 500,
    'rotating_proxies.middlewares.RotatingProxyMiddleware': 610,
    'rotating_proxies.middlewares.BanDetectionMiddleware': 620,
    'scrapy_splash.SplashCookiesMiddleware': 723,
    'scrapy_splash.SplashMiddleware': 725,
    'scrapy.downloadermiddlewares.httpcompression.HttpCompressionMiddleware': 810,
    'crawler_fabricant.middlewares.CookiesMiddleware': 120,

}
ROTATING_PROXY_LIST_PATH = path_to_proxy
ROTATING_PROXY_LOGSTATS_INTERVAL = 60
ROTATING_PROXY_PAGE_RETRY_TIMES = 10
# See https://docs.scrapy.org/en/latest/topics/extensions.html
# EXTENSIONS = {
#    'scrapy.extensions.telnet.TelnetConsole': None,
# }

# Configure item pipelines
# See https://docs.scrapy.org/en/latest/topics/item-pipeline.html
ITEM_PIPELINES = {
    'crawler_fabricant.pipelines.CrawlerFabricantPipeline': 300,
    'crawler_fabricant.pipelines.CrawlerDbConnect': 350,
}

RETRY_ENABLED = True
RETRY_TIMES = 10
RETRY_HTTP_CODES = [500, 502, 503, 504, 522, 524, 408, 429, 407, 403, 404, 400]

# Enable and configure the AutoThrottle extension (disabled by default)
# See https://docs.scrapy.org/en/latest/topics/autothrottle.html
AUTOTHROTTLE_ENABLED = True
AUTOTHROTTLE_START_DELAY = 5
AUTOTHROTTLE_MAX_DELAY = 90
AUTOTHROTTLE_TARGET_CONCURRENCY = 1.0
AUTOTHROTTLE_DEBUG = False

SPLASH_COOKIES_DEBUG = True
SPLASH_LOG_400 = True
DUPEFILTER_CLASS = 'scrapy_splash.SplashAwareDupeFilter'
HTTPCACHE_ENABLED = True
HTTPCACHE_EXPIRATION_SECS = 3600
# HTTPCACHE_DIR = 'httpcache'
# HTTPCACHE_IGNORE_HTTP_CODES = [407]
HTTPCACHE_STORAGE = 'scrapy_splash.SplashAwareFSCacheStorage'
