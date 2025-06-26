import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from general_utils.settings import *

BOT_NAME = "crawler_mets"

SPIDER_MODULES = ["crawler_mets.spiders"]
NEWSPIDER_MODULE = "crawler_mets.spiders"

DOWNLOAD_HANDLERS = {
    "http": "scrapy_playwright.handler.ScrapyPlaywrightDownloadHandler",
    "https": "scrapy_playwright.handler.ScrapyPlaywrightDownloadHandler",
}
