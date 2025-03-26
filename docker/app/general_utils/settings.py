from pathlib import Path

from general_utils.config import headers, proxy_path

# Obey robots.txt rules
ROBOTSTXT_OBEY = False

CONCURRENT_REQUESTS = 32
DOWNLOAD_DELAY = 0
CONCURRENT_REQUESTS_PER_DOMAIN = 16
CONCURRENT_REQUESTS_PER_IP = 16

# Disable cookies (enabled by default)
# COOKIES_ENABLED = False

# Disable Telnet Console (enabled by default)
# TELNETCONSOLE_ENABLED = False
# Override the default request headers:
USER_AGENT = headers['User-Agent']
DEFAULT_REQUEST_HEADERS = headers.copy()

# LOG_LEVEL = 'INFO'
LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
LOG_FILE_APPEND = False

# Enable or disable spider middlewares
# See https://docs.scrapy.org/en/latest/topics/spider-middleware.html
# SPIDER_MIDDLEWARES = {
#    'crawler_akosta.middlewares.CrawlerAkostaSpiderMiddleware': 543,
# }

# Enable or disable downloader middlewares
# See https://docs.scrapy.org/en/latest/topics/downloader-middleware.html
DOWNLOADER_MIDDLEWARES = {
    'scrapy.downloadermiddlewares.cookies.CookiesMiddleware': 120,
    'general_utils.middlewares.UserAgentMiddleware': 150,
    'general_utils.middlewares.ETPDownloaderMiddleware': 160,
    'rotating_proxies.middlewares.RotatingProxyMiddleware': 610,
    'rotating_proxies.middlewares.BanDetectionMiddleware': 620,
    'scrapy.downloadermiddlewares.httpcompression.HttpCompressionMiddleware': 810,
}

# ROTATING_PROXY_LIST_PATH = proxy_path if Path(proxy_path).exists() else None
ROTATING_PROXY_LOGSTATS_INTERVAL = 60
ROTATING_PROXY_PAGE_RETRY_TIMES = 7
# Enable or disable extensions
# See https://docs.scrapy.org/en/latest/topics/extensions.html
# EXTENSIONS = {
#    'scrapy.extensions.telnet.TelnetConsole': None,
# }

# Configure item pipelines
# See https://docs.scrapy.org/en/latest/topics/item-pipeline.html
ITEM_PIPELINES = {
    'general_utils.pipelines.BasePipeline': 300,
}
RETRY_ENABLED = True
RETRY_TIMES = 7
RETRY_HTTP_CODES = [500, 502, 503, 504, 522,
                    524, 408, 429, 407, 403, 404, 400, 401, 498]
# Enable and configure the AutoThrottle extension (disabled by default)
# See https://docs.scrapy.org/en/latest/topics/autothrottle.html
AUTOTHROTTLE_ENABLED = True
# The initial download delay
AUTOTHROTTLE_START_DELAY = 5
# The maximum download delay to be set in case of high latencies
AUTOTHROTTLE_MAX_DELAY = 120
# The average number of requests Scrapy should be sending in parallel to
# each remote server
AUTOTHROTTLE_TARGET_CONCURRENCY = 2
# Enable showing throttling stats for every response received:
AUTOTHROTTLE_DEBUG = False
DUPEFILTER_CLASS = 'scrapy.dupefilters.BaseDupeFilter'
# Enable and configure HTTP caching (disabled by default)
# See https://docs.scrapy.org/en/latest/topics/downloader-middleware.html#httpcache-middleware-settings
# HTTPCACHE_ENABLED = True
# HTTPCACHE_EXPIRATION_SECS = 3600
# HTTPCACHE_DIR = 'httpcache'
# HTTPCACHE_IGNORE_HTTP_CODES = [500, 502, 503, 504,
#                                522, 524, 408, 429, 407, 403, 404, 400, 402]
# HTTPCACHE_STORAGE = 'scrapy.extensions.httpcache.FilesystemCacheStorage'

REQUEST_FINGERPRINTER_IMPLEMENTATION = "2.7"
TWISTED_REACTOR = "twisted.internet.asyncioreactor.AsyncioSelectorReactor"
FEED_EXPORT_ENCODING = "utf-8"
CLOSESPIDER_PAGECOUNT = 5000

SPLASH_URL = 'http://splash:8050/'
SPIDER_MIDDLEWARES = {
    'scrapy_splash.SplashDeduplicateArgsMiddleware': 100,
}

SPLASH_COOKIES_DEBUG = False
SPLASH_LOG_400 = True
