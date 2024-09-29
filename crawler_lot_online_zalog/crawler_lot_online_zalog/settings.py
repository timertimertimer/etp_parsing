from crawler_lot_online_zalog.utils.config import path_to_proxy, agent_list, Referer
from random import choice

BOT_NAME = 'crawler_lot_online_zalog'

SPIDER_MODULES = ['crawler_lot_online_zalog.spiders']
NEWSPIDER_MODULE = 'crawler_lot_online_zalog.spiders'

# Crawl responsibly by identifying yourself (and your website) on the user-agent
# USER_AGENT = 'crawler_lot_online_zalog (+http://www.yourdomain.com)'
AJAXCRAWL_ENABLED = True
# Obey robots.txt rules
ROBOTSTXT_OBEY = False

# Configure maximum concurrent requests performed by Scrapy (default: 16)
CONCURRENT_REQUESTS = 1
USER_AGENT = choice(agent_list)
# Override the default request headers:
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

COOKIES_ENABLED = False
SPLASH_URL = 'http://localhost:8064'
SPIDER_MIDDLEWARES = {
    'scrapy_splash.SplashDeduplicateArgsMiddleware': 100,
}

DOWNLOADER_MIDDLEWARES = {
    'crawler_lot_online_zalog.middlewares.UserAgentMiddleware': 500,
    'rotating_proxies.middlewares.RotatingProxyMiddleware': 610,
    'rotating_proxies.middlewares.BanDetectionMiddleware': 620,
    'scrapy_splash.SplashCookiesMiddleware': 723,
    'scrapy_splash.SplashMiddleware': 725,
    'scrapy.downloadermiddlewares.httpcompression.HttpCompressionMiddleware': 810,
}

LOG_LEVEL = 'INFO'
LOG_FILE = './lot_online.log'
LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
# Enable or disable downloader middlewares
# See https://docs.scrapy.org/en/latest/topics/downloader-middleware.html


ROTATING_PROXY_LIST_PATH = path_to_proxy
ROTATING_PROXY_LOGSTATS_INTERVAL = 60
ROTATING_PROXY_PAGE_RETRY_TIMES = 15

# Configure item pipelines
# See https://docs.scrapy.org/en/latest/topics/item-pipeline.html
ITEM_PIPELINES = {
    'crawler_lot_online_zalog.pipelines.CrawlerLotOnlineZalogPipeline': 300,
    'crawler_lot_online_zalog.pipelines.LotOnlineZalogConnect': 350,
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
AUTOTHROTTLE_TARGET_CONCURRENCY = 1
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
