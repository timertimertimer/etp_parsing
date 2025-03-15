import sys
import os

# Добавляем путь на две директории выше
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from general_utils.settings import *


BOT_NAME = 'crawler_itender'

SPIDER_MODULES = ['crawler_itender.spiders']
NEWSPIDER_MODULE = 'crawler_itender.spiders'
