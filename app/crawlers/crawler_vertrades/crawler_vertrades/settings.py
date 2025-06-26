import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from app.utils.config import write_log_to_file
from app.crawlers.settings import *

BOT_NAME = "crawler_vertrades"

SPIDER_MODULES = ["crawler_vertrades.spiders"]
NEWSPIDER_MODULE = "crawler_vertrades.spiders"
LOG_FILE = "vertrades.log" if write_log_to_file else None
