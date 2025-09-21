import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))


from app.crawlers.settings import *
from app.utils.config import write_log_to_file

BOT_NAME = "crawler_bankrot_cdtrf"

SPIDER_MODULES = ["crawler_bankrot_cdtrf.spiders"]
NEWSPIDER_MODULE = "crawler_bankrot_cdtrf.spiders"
# DOWNLOAD_DELAY = 3
LOG_FILE = "bankrot_cdtrf.log" if write_log_to_file else None
# CONCURRENT_REQUESTS_PER_DOMAIN = 1
ROTATING_PROXY_LIST_PATH = None
