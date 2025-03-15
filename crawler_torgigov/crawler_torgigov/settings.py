from general_utils.config import write_log_to_file
from general_utils.settings import *

BOT_NAME = 'crawler_torgigov'

SPIDER_MODULES = ['crawler_torgigov.spiders']
NEWSPIDER_MODULE = 'crawler_torgigov.spiders'
UNIQUE_CO = ['trading_id', 'trading_type', 'lot_number']
LOT_FILE = 'torgigov.log' if write_log_to_file else None
ITEM_PIPELINES = {
    'general_utils.pipelines.ETPNonBankruptPipeline': 300,
}
