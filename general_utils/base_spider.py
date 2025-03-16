import logging
import time
import scrapy
from scrapy import signals
from scrapy.exceptions import CloseSpider
from scrapy.spidermiddlewares.httperror import HttpError
from twisted.internet.error import DNSLookupError, TCPTimedOutError

from .db import DBHelper

logger = logging.getLogger(__name__)


class BaseSpider(scrapy.Spider):
    def __init__(self, data_origin, keys=None, *args, **kwargs):
        super(BaseSpider, self).__init__(*args, **kwargs)
        self.previous_trades, self.trading_floor_id = DBHelper.get_latest_lot(self.name, data_origin, keys)
        if self.previous_trades is None:
            raise CloseSpider(f"Stopping the spider, no previous lots or trading floor found for {self.name}.")
        logger.info(f"Previous trades: {len(self.previous_trades)}")

    @classmethod
    def from_crawler(cls, crawler, *args, **kwargs):
        spider = super().from_crawler(crawler, *args, **kwargs)
        crawler.signals.connect(spider.spider_opened, signal=signals.spider_opened)
        crawler.signals.connect(spider.spider_closed, signal=signals.spider_closed)
        return spider

    def spider_opened(self):
        self.counter = 0
        self.time_started = time.time()
        self.logger.info(f"Spider {self.name} started at {self.time_started}")

    def spider_closed(self):
        duration = time.time() - self.time_started
        self.logger.info(f"Spider {self.name} closed. Scraped {self.counter} items in {duration:.2f} seconds.")
        DBHelper.save_counter_and_duration(self.counter, duration, self.name)

    def errback_httpbin(self, failure):
        self.logger.error(repr(failure))
        if failure.check(HttpError):
            response = failure.value.response
            self.logger.error("HttpError occurred on %s", response.url)
        elif failure.check(DNSLookupError):
            request = failure.request
            self.logger.error("DNSLookupError occurred on %s", request.url)
        elif failure.check(TimeoutError, TCPTimedOutError):
            request = failure.request
            self.logger.error("TimeoutError occurred on %s", request.url)
