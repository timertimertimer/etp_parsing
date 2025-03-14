from general_utils.settings import *

BOT_NAME = 'crawler_tenderstandartru'

SPIDER_MODULES = ['crawler_tenderstandartru.spiders']
NEWSPIDER_MODULE = 'crawler_tenderstandartru.spiders'
DEFAULT_REQUEST_HEADERS['x-requested-with'] = 'XMLHttpRequest'
