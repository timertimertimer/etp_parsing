from general_utils.config import write_log_to_file
from general_utils.settings import *

BOT_NAME = "crawler_opentp"

SPIDER_MODULES = ["crawler_opentp.spiders"]
NEWSPIDER_MODULE = "crawler_opentp.spiders"
LOG_FILE = 'opentp.log' if write_log_to_file else None
