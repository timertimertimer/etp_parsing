from general_utils.settings import *

BOT_NAME = 'crawler_sales_lot_online'

SPIDER_MODULES = ['crawler_sales_lot_online.spiders']
NEWSPIDER_MODULE = 'crawler_sales_lot_online.spiders'

CONCURRENT_REQUESTS = 2
# LOG_FILE = 'lot_online.log'
UNIQUE_CO = ['trading_id', 'lot_number']
DOWNLOADER_MIDDLEWARES = DOWNLOADER_MIDDLEWARES | {
    'scrapy_splash.SplashCookiesMiddleware': 723,
    'scrapy_splash.SplashMiddleware': 725,
}
DUPEFILTER_CLASS = 'scrapy_splash.SplashAwareDupeFilter'
DEFAULT_REQUEST_HEADERS['Accept-Encoding'] = '*/*'
