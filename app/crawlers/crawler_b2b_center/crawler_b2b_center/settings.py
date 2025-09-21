import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from app.utils.config import write_log_to_file
from app.crawlers.settings import *

BOT_NAME = "crawler_b2b_center"

SPIDER_MODULES = ["crawler_b2b_center.spiders"]
NEWSPIDER_MODULE = "crawler_b2b_center.spiders"

LOG_FILE = "b2b_center.log" if write_log_to_file else None

DEFAULT_REQUEST_HEADERS["Host"] = "www.b2b-center.ru"
ROTATING_PROXY_LIST_PATH = None
