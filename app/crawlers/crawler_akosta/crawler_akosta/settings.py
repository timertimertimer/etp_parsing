import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from app.crawlers.settings import *
from app.utils.config import write_log_to_file
from .utils.config import host

BOT_NAME = "crawler_akosta"
SPIDER_MODULES = ["crawler_akosta.spiders"]
NEWSPIDER_MODULE = "crawler_akosta.spiders"
CONCURRENT_REQUESTS = 1
DEFAULT_REQUEST_HEADERS["Host"] = host
DOWNLOADER_MIDDLEWARES[
    "crawler_akosta.middlewares.CrawlerAkostaDownloaderMiddleware"
] = 543
LOG_FILE = "akosta.log" if write_log_to_file else None
ROTATING_PROXY_LIST_PATH = None
