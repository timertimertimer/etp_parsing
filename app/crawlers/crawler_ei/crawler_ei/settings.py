import sys
import os

from app.utils.config import write_log_to_file

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from app.crawlers.settings import *

BOT_NAME = "crawler_ei"

SPIDER_MODULES = ["crawler_ei.spiders"]
NEWSPIDER_MODULE = "crawler_ei.spiders"

LOG_FILE = "ei.log" if write_log_to_file else None