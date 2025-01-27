from general_utils.settings import *

BOT_NAME = "crawler_torgidv"

SPIDER_MODULES = ["crawler_torgidv.spiders"]
NEWSPIDER_MODULE = "crawler_torgidv.spiders"
# LOG_FILE = 'torigdv.log'
UNIQUE_CO = ['trading_id', 'trading_type', 'lot_number']
