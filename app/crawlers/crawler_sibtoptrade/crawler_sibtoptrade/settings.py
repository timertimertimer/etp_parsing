import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from app.utils.config import write_log_to_file
from app.crawlers.settings import *

BOT_NAME = "crawler_sibtoptrade"

SPIDER_MODULES = ["crawler_sibtoptrade.spiders"]
NEWSPIDER_MODULE = "crawler_sibtoptrade.spiders"

LOG_FILE = "sibtoptrade.log" if write_log_to_file else None
DEFAULT_REQUEST_HEADERS.pop("Accept-Encoding")
DOWNLOADER_MIDDLEWARES = DOWNLOADER_MIDDLEWARES | {
    "scrapy_splash.SplashCookiesMiddleware": 723,
    "scrapy_splash.SplashMiddleware": 725,
}

HTTPCACHE_ENABLED = True
HTTPCACHE_EXPIRATION_SECS = 120
HTTPCACHE_STORAGE = "scrapy_splash.SplashAwareFSCacheStorage"
ROTATING_PROXY_LIST_PATH = None
