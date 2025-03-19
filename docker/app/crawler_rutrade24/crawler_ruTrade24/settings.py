import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from .config import host
from general_utils.settings import *

BOT_NAME = 'crawler_ruTrade24'

SPIDER_MODULES = ['crawler_ruTrade24.spiders']
NEWSPIDER_MODULE = 'crawler_ruTrade24.spiders'

DEFAULT_REQUEST_HEADERS['Host'] = host
