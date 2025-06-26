import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from general_utils.config import write_log_to_file
from general_utils.settings import *

BOT_NAME = "crawler_fabricant"
SPIDER_MODULES = ["crawler_fabricant.spiders"]
NEWSPIDER_MODULE = "crawler_fabricant.spiders"
LOG_FILE = "fabricant.log" if write_log_to_file else None
