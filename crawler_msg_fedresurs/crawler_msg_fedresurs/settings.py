from general_utils.settings import *

BOT_NAME = 'crawler_msg_fedresurs'

SPIDER_MODULES = ['crawler_msg_fedresurs.spiders']
NEWSPIDER_MODULE = 'crawler_msg_fedresurs.spiders'
COOKIES_ENABLED = False
# LOG_FILE = 'fedres_msg.log'

ITEM_PIPELINES = {
    'crawler_msg_fedresurs.pipelines.CrawlerMsgFedresursPipeline': 300,
    'crawler_msg_fedresurs.pipelines.CrawlerDbConnect': 350,
}
