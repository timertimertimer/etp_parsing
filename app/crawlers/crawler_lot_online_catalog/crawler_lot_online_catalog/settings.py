import sys
import os

from app.utils.config import write_log_to_file

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from app.crawlers.settings import *

BOT_NAME = "crawler_lot_online_catalog"

SPIDER_MODULES = ["crawler_lot_online_catalog.spiders"]
NEWSPIDER_MODULE = "crawler_lot_online_catalog.spiders"

LOG_FILE = "lot_online_catalog.log" if write_log_to_file else None
ROTATING_PROXY_LIST_PATH = None
