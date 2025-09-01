import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from app.crawlers.settings import *

BOT_NAME = "crawler_lot_online_old"

SPIDER_MODULES = ["crawler_lot_online_old.spiders"]
NEWSPIDER_MODULE = "crawler_lot_online_old.spiders"
