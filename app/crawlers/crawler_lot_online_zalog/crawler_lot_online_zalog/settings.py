import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from app.crawlers.settings import *

BOT_NAME = "crawler_lot_online_zalog"

SPIDER_MODULES = ["crawler_lot_online_zalog.spiders"]
NEWSPIDER_MODULE = "crawler_lot_online_zalog.spiders"

DUPEFILTER_CLASS = "scrapy_splash.SplashAwareDupeFilter"
DOWNLOADER_MIDDLEWARES = DOWNLOADER_MIDDLEWARES | {
    "scrapy_splash.SplashCookiesMiddleware": 723,
    "scrapy_splash.SplashMiddleware": 725,
}
DEFAULT_REQUEST_HEADERS["Accept-Encoding"] = "*/*"
ROTATING_PROXY_LIST_PATH = None
