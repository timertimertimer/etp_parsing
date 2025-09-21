import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from app.utils.config import write_log_to_file
from app.crawlers.settings import *

BOT_NAME = "crawler_moi_tender"

SPIDER_MODULES = ["crawler_moi_tender.spiders"]
NEWSPIDER_MODULE = "crawler_moi_tender.spiders"

LOG_FILE = "moi_tender.log" if write_log_to_file else None
ROTATING_PROXY_LIST_PATH = None
