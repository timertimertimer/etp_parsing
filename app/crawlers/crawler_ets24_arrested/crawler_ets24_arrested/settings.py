import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from app.utils.config import write_log_to_file
from app.crawlers.settings import *

BOT_NAME = "crawler_ets24_arrested"

SPIDER_MODULES = ["crawler_ets24_arrested.spiders"]
NEWSPIDER_MODULE = "crawler_ets24_arrested.spiders"
LOG_FILE = "ets24_arrested.log" if write_log_to_file else None
