from general_utils.config import write_log_to_file
from general_utils.settings import *

BOT_NAME = 'crawler_eurtp'

SPIDER_MODULES = ['crawler_eurtp.spiders']
NEWSPIDER_MODULE = 'crawler_eurtp.spiders'

LOG_FILE = 'eurtp.log' if write_log_to_file else None
