from .utils.config import Referer
from general_utils.settings import *

BOT_NAME = 'crawler_lot_online_zalog'

SPIDER_MODULES = ['crawler_lot_online_zalog.spiders']
NEWSPIDER_MODULE = 'crawler_lot_online_zalog.spiders'

AJAXCRAWL_ENABLED = True
CONCURRENT_REQUESTS = 1
COOKIES_ENABLED = False
# LOG_FILE = 'lot_online.log'
UNIQUE_CO = ['trading_id', 'trading_type', 'lot_number']
DOWNLOADER_MIDDLEWARES = DOWNLOADER_MIDDLEWARES | {
    'scrapy_splash.SplashCookiesMiddleware': 723,
    'scrapy_splash.SplashMiddleware': 725,
}
DUPEFILTER_CLASS = 'scrapy_splash.SplashAwareDupeFilter'
ITEM_PIPELINES = {
    'general_utils.pipelines.ETPNonBankruptPipeline': 300,
}
DEFAULT_REQUEST_HEADERS['Accept-Encoding'] = '*/*'
DEFAULT_REQUESTS_HEADERS = {

    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,'
              '*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
    'Accept-Encoding': 'gzip, deflate, br',
    'Accept-Language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7',
    'Cache-Control': 'no-cache',
    'Connection': 'keep-alive',
    'Host': 'sales.lot-online.ru',
    'Pragma': 'no-cache',
    'Referer': Referer,
    'Sec-Fetch-Dest': 'document',
    'Sec-Fetch-Mode': 'navigate',
    'Sec-Fetch-Site': 'none',
    'Upgrade-Insecure-Requests': '1',
    'User-Agent': USER_AGENT,
}