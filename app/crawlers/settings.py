import sys
import logging
import warnings
from pathlib import Path

import scrapy.utils.log

from app.utils.config import headers, proxy_path
from app.utils.logger import logger
from bs4 import XMLParsedAsHTMLWarning


# Obey robots.txt rules
ROBOTSTXT_OBEY = False

CONCURRENT_REQUESTS = 32
DOWNLOAD_DELAY = 0
CONCURRENT_REQUESTS_PER_DOMAIN = 16
CONCURRENT_REQUESTS_PER_IP = 16

USER_AGENT = headers["User-Agent"]
DEFAULT_REQUEST_HEADERS = headers.copy()

DOWNLOADER_MIDDLEWARES = {
    "scrapy.downloadermiddlewares.cookies.CookiesMiddleware": 120,
    "crawlers.middlewares.UserAgentMiddleware": 150,
    "crawlers.middlewares.ETPDownloaderMiddleware": 160,
    "rotating_proxies.middlewares.RotatingProxyMiddleware": 610,
    "rotating_proxies.middlewares.BanDetectionMiddleware": 620,
    "scrapy.downloadermiddlewares.httpcompression.HttpCompressionMiddleware": 810,
}

ROTATING_PROXY_LIST_PATH = proxy_path if Path(proxy_path).exists() else None
ROTATING_PROXY_LOGSTATS_INTERVAL = 60
ROTATING_PROXY_PAGE_RETRY_TIMES = 7

ITEM_PIPELINES = {
    "crawlers.pipelines.BasePipeline": 300,
}
RETRY_ENABLED = True
RETRY_TIMES = 7
RETRY_HTTP_CODES = [
    500,
    502,
    503,
    504,
    522,
    524,
    408,
    429,
    407,
    403,
    400,
    401,
    498,
]
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
DUPEFILTER_CLASS = "scrapy.dupefilters.BaseDupeFilter"
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

SPLASH_URL = "http://etp_parsing_splash:8050/"
SPIDER_MIDDLEWARES = {
    "scrapy_splash.SplashDeduplicateArgsMiddleware": 100,
}

SPLASH_COOKIES_DEBUG = False
SPLASH_LOG_400 = True


class InterceptHandler(logging.Handler):
    def emit(self, record):
        level = (
            record.levelname
            if record.levelname in logger._core.levels
            else record.levelno
        )
        frame = sys._getframe(1)
        depth = 1
        while frame and frame.f_globals["__name__"].startswith("logging"):
            frame = frame.f_back
            depth += 1
        logger.opt(depth=depth, exception=record.exc_info).log(
            level, record.getMessage()
        )


def setup_logger():
    for warning in [XMLParsedAsHTMLWarning, SyntaxWarning, UserWarning, FutureWarning]:
        warnings.filterwarnings("ignore", category=warning)

    root_logger = logging.getLogger()
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)

    for name, log_instance in logging.root.manager.loggerDict.items():
        if isinstance(log_instance, logging.Logger):
            log_instance.handlers.clear()

    scrapy.utils.log.configure_logging = lambda settings: None
    logging.basicConfig(handlers=[InterceptHandler()], level=logging.INFO, force=True)


setup_logger()
LOG_ENABLED = False
TELNETCONSOLE_ENABLED = False
