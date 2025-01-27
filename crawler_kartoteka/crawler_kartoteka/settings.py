from general_utils.settings import *

BOT_NAME = "crawler_kartoteka"

SPIDER_MODULES = ["crawler_kartoteka.spiders"]
NEWSPIDER_MODULE = "crawler_kartoteka.spiders"

DOWNLOAD_HANDLERS = {
    "http": "scrapy_playwright.handler.ScrapyPlaywrightDownloadHandler",
    "https": "scrapy_playwright.handler.ScrapyPlaywrightDownloadHandler",
}
# LOG_FILE = 'kartoteka.log'
