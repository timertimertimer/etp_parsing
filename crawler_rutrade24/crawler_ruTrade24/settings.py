from crawler_rutrade24.crawler_ruTrade24.config import host
from general_utils.settings import *

BOT_NAME = 'crawler_ruTrade24'

SPIDER_MODULES = ['crawler_ruTrade24.spiders']
NEWSPIDER_MODULE = 'crawler_ruTrade24.spiders'

# CONCURRENT_REQUESTS_PER_DOMAIN = 1
# CONCURRENT_REQUESTS_PER_IP = 1
DEFAULT_REQUEST_HEADERS['Host'] = host
