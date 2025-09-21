import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from app.utils.config import write_log_to_file
from app.crawlers.settings import *

BOT_NAME = "crawler_fabrikant"
SPIDER_MODULES = ["crawler_fabrikant.spiders"]
NEWSPIDER_MODULE = "crawler_fabrikant.spiders"
LOG_FILE = "fabrikant.log" if write_log_to_file else None
ROTATING_PROXY_LIST_PATH = None
