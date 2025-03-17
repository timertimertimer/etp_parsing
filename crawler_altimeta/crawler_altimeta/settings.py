import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from general_utils.settings import *

BOT_NAME = 'crawler_altimeta'

SPIDER_MODULES = ['crawler_altimeta.spiders']
NEWSPIDER_MODULE = 'crawler_altimeta.spiders'
