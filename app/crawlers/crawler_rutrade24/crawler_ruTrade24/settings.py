import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from app.crawlers.settings import *

BOT_NAME = "crawler_ruTrade24"

SPIDER_MODULES = ["crawler_ruTrade24.spiders"]
NEWSPIDER_MODULE = "crawler_ruTrade24.spiders"
