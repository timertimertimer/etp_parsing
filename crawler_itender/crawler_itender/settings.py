from general_utils.settings import *

BOT_NAME = 'crawler_itender'

SPIDER_MODULES = ['crawler_itender.spiders']
NEWSPIDER_MODULE = 'crawler_itender.spiders'
UNIQUE_CO = ['trading_id', 'trading_type', 'lot_number']
