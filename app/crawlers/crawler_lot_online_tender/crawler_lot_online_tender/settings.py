import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from app.utils.config import write_log_to_file
from app.crawlers.settings import *

BOT_NAME = "crawler_lot_online_tender"

SPIDER_MODULES = ["crawler_lot_online_tender.spiders"]
NEWSPIDER_MODULE = "crawler_lot_online_tender.spiders"

LOG_FILE = "lot_online_tender.log" if write_log_to_file else None
