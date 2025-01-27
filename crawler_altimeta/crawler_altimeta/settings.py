from general_utils.settings import *

BOT_NAME = 'crawler_altimeta'

SPIDER_MODULES = ['crawler_altimeta.spiders']
NEWSPIDER_MODULE = 'crawler_altimeta.spiders'
UNIQUE_CO = ['trading_id', 'trading_type', 'lot_number']
