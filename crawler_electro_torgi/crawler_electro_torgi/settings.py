from general_utils.settings import *

BOT_NAME = "crawler_electro_torgi"
SPIDER_MODULES = ["crawler_electro_torgi.spiders"]
NEWSPIDER_MODULE = "crawler_electro_torgi.spiders"
UNIQUE_CO = ['trading_id', 'lot_number', 'lot_id']