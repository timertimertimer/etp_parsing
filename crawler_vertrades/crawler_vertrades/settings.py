from general_utils.settings import *

BOT_NAME = "crawler_vertrades"

SPIDER_MODULES = ["crawler_vertrades.spiders"]
NEWSPIDER_MODULE = "crawler_vertrades.spiders"
CONCURRENT_REQUESTS = 1
# LOG_FILE = 'vertrades.log'
UNIQUE_CO = ['trading_id', 'trading_type', 'lot_number']
