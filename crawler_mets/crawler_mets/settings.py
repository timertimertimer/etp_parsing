from general_utils.settings import *

BOT_NAME = 'crawler_mets'

SPIDER_MODULES = ['crawler_mets.spiders']
NEWSPIDER_MODULE = 'crawler_mets.spiders'

DOWNLOAD_HANDLERS = {
    "http": "scrapy_playwright.handler.ScrapyPlaywrightDownloadHandler",
    "https": "scrapy_playwright.handler.ScrapyPlaywrightDownloadHandler",
}
# LOG_FILE = 'mets.log'
