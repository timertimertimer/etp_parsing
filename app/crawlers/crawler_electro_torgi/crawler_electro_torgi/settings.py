import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from app.crawlers.settings import *

BOT_NAME = "crawler_electro_torgi"
SPIDER_MODULES = ["crawler_electro_torgi.spiders"]
NEWSPIDER_MODULE = "crawler_electro_torgi.spiders"

ROTATING_PROXY_LIST_PATH = None
