from general_utils.settings import *

BOT_NAME = 'crawler_sistematorg'

SPIDER_MODULES = ['crawler_sistematorg.spiders']
NEWSPIDER_MODULE = 'crawler_sistematorg.spiders'
UNIQUE_CO = ['trading_id', 'trading_number', 'lot_number']
# LOG_FILE = 'sistematorg.log'
