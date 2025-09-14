import sys
import os
from random import choice

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from app.utils.config import write_log_to_file, user_agents
from app.crawlers.settings import *

BOT_NAME = "crawler_sberbank"

SPIDER_MODULES = ["crawler_sberbank.spiders"]
NEWSPIDER_MODULE = "crawler_sberbank.spiders"

DOWNLOAD_HANDLERS = {
    "http": "scrapy_playwright.handler.ScrapyPlaywrightDownloadHandler",
    "https": "scrapy_playwright.handler.ScrapyPlaywrightDownloadHandler",
}
LOG_FILE = "sberbank.log" if write_log_to_file else None
# CONCURRENT_REQUESTS = 1
# DOWNLOAD_DELAY = 3
DEFAULT_REQUEST_HEADERS = {
    "Accept": "*/*",
    "Accept-Encoding": "gzip, deflate, br, zstd",
    "Accept-Language": "ru-RU,ru;q=0.9",
    "Sec-Fetch-Dest": "empty",
    "Sec-Fetch-Mode": "cors",
    "Sec-Fetch-Site": "same-origin",
    "Origin": "https://utp.sberbank-ast.ru",
    "Priority": "u=1, i",
    "User-Agent": choice(user_agents),
}
ROTATING_PROXY_LIST_PATH = None
