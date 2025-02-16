from general_utils.settings import *

BOT_NAME = 'crawler_zalog_lot_online'

SPIDER_MODULES = ['crawler_zalog_lot_online.spiders']
NEWSPIDER_MODULE = 'crawler_zalog_lot_online.spiders'
UNIQUE_CO = ['trading_id', 'trading_type', 'lot_number']

DUPEFILTER_CLASS = 'scrapy_splash.SplashAwareDupeFilter'
DOWNLOADER_MIDDLEWARES = DOWNLOADER_MIDDLEWARES | {
    'scrapy_splash.SplashCookiesMiddleware': 723,
    'scrapy_splash.SplashMiddleware': 725,
}
DEFAULT_REQUEST_HEADERS['Accept-Encoding'] = '*/*'
ITEM_PIPELINES = {
    'general_utils.pipelines.ETPNonBankruptPipeline': 300,
}
