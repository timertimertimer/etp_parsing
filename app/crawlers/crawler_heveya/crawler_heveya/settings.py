import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from general_utils.config import write_log_to_file
from general_utils.settings import *

BOT_NAME = "crawler_heveya"

SPIDER_MODULES = ["crawler_heveya.spiders"]
NEWSPIDER_MODULE = "crawler_heveya.spiders"
LOG_FILE = "heveya.log" if write_log_to_file else None
