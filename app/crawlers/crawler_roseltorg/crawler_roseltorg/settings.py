import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from app.utils.config import write_log_to_file
from app.crawlers.settings import *

BOT_NAME = "crawler_roseltorg"

SPIDER_MODULES = ["crawler_roseltorg.spiders"]
NEWSPIDER_MODULE = "crawler_roseltorg.spiders"
LOG_FILE = "roseltorg.log" if write_log_to_file else None
# ROTATING_PROXY_LIST_PATH = None
