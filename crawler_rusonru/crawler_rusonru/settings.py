from general_utils.settings import *

BOT_NAME = 'crawler_rusonru'

SPIDER_MODULES = ['crawler_rusonru.spiders']
NEWSPIDER_MODULE = 'crawler_rusonru.spiders'
# LOG_FILE = 'ruson.log'
UNIQUE_CO = ['trading_id', 'trading_type', 'lot_number']