import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from app.utils.config import write_log_to_file
from app.crawlers.settings import *

BOT_NAME = "crawler_opentp"

SPIDER_MODULES = ["crawler_opentp.spiders"]
NEWSPIDER_MODULE = "crawler_opentp.spiders"
LOG_FILE = "opentp.log" if write_log_to_file else None
