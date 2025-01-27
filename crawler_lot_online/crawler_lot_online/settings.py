from general_utils.settings import *

BOT_NAME = "crawler_lot_online"

SPIDER_MODULES = ["crawler_lot_online.spiders"]
NEWSPIDER_MODULE = "crawler_lot_online.spiders"
UNIQUE_CO = ['trading_id', 'trading_type', 'lot_number']
# LOG_FILE = 'lot_online.log'