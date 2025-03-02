from .utils.config import host
from general_utils.settings import *

BOT_NAME = 'crawler_akosta'
SPIDER_MODULES = ['crawler_akosta.spiders']
NEWSPIDER_MODULE = 'crawler_akosta.spiders'
CONCURRENT_REQUESTS = 1
DEFAULT_REQUEST_HEADERS['Host'] = host
DOWNLOADER_MIDDLEWARES['crawler_akosta.middlewares.CrawlerAkostaDownloaderMiddleware'] = 543
# LOG_FILE = 'akosta.log'
