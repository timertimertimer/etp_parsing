from general_utils.config import write_log_to_file
from general_utils.settings import *

BOT_NAME = "crawler_moi_tender"

SPIDER_MODULES = ["crawler_moi_tender.spiders"]
NEWSPIDER_MODULE = "crawler_moi_tender.spiders"

LOG_FILE = 'moi_tender.log' if write_log_to_file else None
