from general_utils.settings import *

BOT_NAME = "crawler_moi_tender"

SPIDER_MODULES = ["crawler_moi_tender.spiders"]
NEWSPIDER_MODULE = "crawler_moi_tender.spiders"

# LOG_FILE = 'moi_tender.log'
ITEM_PIPELINES = {
    'general_utils.pipelines.ETPNonBankruptPipeline': 300
}
