from general_utils.settings import *

BOT_NAME = "crawler_heveya"

SPIDER_MODULES = ["crawler_heveya.spiders"]
NEWSPIDER_MODULE = "crawler_heveya.spiders"
# LOG_FILE = 'heveya.log'
UNIQUE_CO = ['trading_id', 'lot_number', 'lot_id']
