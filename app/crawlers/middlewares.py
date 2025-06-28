from scrapy import signals


__all__ = [
    "UserAgentMiddleware",
    "ETPDownloaderMiddleware",
    "ETPSpiderMiddleware",
]


class UserAgentMiddleware:
    def __init__(self, user_agent="Scrapy"):
        self.user_agent = user_agent

    @classmethod
    def from_crawler(cls, crawler):
        o = cls(crawler.settings["USER_AGENT"])
        crawler.signals.connect(o.spider_opened, signal=signals.spider_opened)
        return o

    def spider_opened(self, spider):
        self.user_agent = getattr(spider, "user_agent", self.user_agent)

    def process_request(self, request, spider):
        if self.user_agent:
            request.headers.setdefault(b"User-Agent", self.user_agent)


class ETPSpiderMiddleware:
    # Not all methods need to be defined. If a method is not defined,
    # scrapy acts as if the spider middleware does not modify the
    # passed objects.

    @classmethod
    def from_crawler(cls, crawler):
        # This method is used by Scrapy to create your spiders.
        s = cls()
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        return s

    def process_spider_output(self, response, result, spider):
        # Called with the results returned from the Spider, after
        # it has processed the response.

        # Must return an iterable of Request, or item objects.
        for i in result:
            yield i

    def process_start_requests(self, start_requests, spider):
        # Called with the start requests of the spider, and works
        # similarly to the process_spider_output() method, except
        # that it doesn’t have a response associated.

        # Must return only requests (not items).
        for r in start_requests:
            yield r

    def spider_opened(self, spider):
        spider.logger.info("Spider opened: %s" % spider.name)


class ETPDownloaderMiddleware:
    def process_response(self, request, response, spider):
        if not hasattr(spider, "status_active"):
            spider.status_active = response.status in range(200, 400)
        return response
