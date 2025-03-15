from general_utils.config import write_log_to_file
from general_utils.settings import *

BOT_NAME = 'crawler_sberbank'

SPIDER_MODULES = ['crawler_sberbank.spiders']
NEWSPIDER_MODULE = 'crawler_sberbank.spiders'

DOWNLOAD_HANDLERS = {
    "http": "scrapy_playwright.handler.ScrapyPlaywrightDownloadHandler",
    "https": "scrapy_playwright.handler.ScrapyPlaywrightDownloadHandler",
}
LOG_FILE = 'sberbank.log' if write_log_to_file else None
# CONCURRENT_REQUESTS = 1
# DOWNLOAD_DELAY = 3
