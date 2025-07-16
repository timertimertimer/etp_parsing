import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from app.crawlers.settings import *

BOT_NAME = "crawler_sitesoft"

SPIDER_MODULES = ["crawler_sitesoft.spiders"]
NEWSPIDER_MODULE = "crawler_sitesoft.spiders"
