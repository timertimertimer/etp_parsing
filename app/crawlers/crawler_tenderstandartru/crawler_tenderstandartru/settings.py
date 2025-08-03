import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from app.crawlers.settings import *

BOT_NAME = "crawler_tenderstandartru"

SPIDER_MODULES = ["crawler_tenderstandartru.spiders"]
NEWSPIDER_MODULE = "crawler_tenderstandartru.spiders"
DEFAULT_REQUEST_HEADERS["x-requested-with"] = "XMLHttpRequest"
