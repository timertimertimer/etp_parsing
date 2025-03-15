from general_utils.config import write_log_to_file
from general_utils.settings import *

BOT_NAME = "crawler_vertrades"

SPIDER_MODULES = ["crawler_vertrades.spiders"]
NEWSPIDER_MODULE = "crawler_vertrades.spiders"
# CONCURRENT_REQUESTS = 1
LOG_FILE = 'vertrades.log' if write_log_to_file else None
