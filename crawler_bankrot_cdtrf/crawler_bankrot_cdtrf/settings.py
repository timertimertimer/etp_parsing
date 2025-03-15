from general_utils.config import write_log_to_file
from general_utils.settings import *

BOT_NAME = 'crawler_bankrot_cdtrf'

SPIDER_MODULES = ['crawler_bankrot_cdtrf.spiders']
NEWSPIDER_MODULE = 'crawler_bankrot_cdtrf.spiders'
# DOWNLOAD_DELAY = 3
LOG_FILE = 'bankrot_cdtrf.log' if write_log_to_file else None
# CONCURRENT_REQUESTS_PER_DOMAIN = 1
