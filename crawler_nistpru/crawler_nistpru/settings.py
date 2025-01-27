from general_utils.settings import *

BOT_NAME = 'crawler_nistpru'

SPIDER_MODULES = ['crawler_nistpru.spiders']
NEWSPIDER_MODULE = 'crawler_nistpru.spiders'
# LOG_FILE = 'nistp.log'
UNIQUE_CO = ['trading_id', 'trading_type', 'lot_number']
