from typing import Iterable
from scrapy import Request
from app.utils.config import trash_resources, write_log_to_file
from .base import ItenderBaseSpider


class AlfalotSpider(ItenderBaseSpider):
    name = "alfalot"
    custom_settings = {
        "LOG_FILE": f"{name}.log" if write_log_to_file else None,
        "PLAYWRIGHT_ABORT_REQUEST": lambda request: request.resource_type
        in trash_resources,
        "DOWNLOAD_HANDLERS": {
            "http": "scrapy_playwright.handler.ScrapyPlaywrightDownloadHandler",
            "https": "scrapy_playwright.handler.ScrapyPlaywrightDownloadHandler",
        },
    }

    def start_requests(self) -> Iterable[Request]:
        yield Request(
            self.data_origin, callback=self.choose_datatype, meta=dict(playwright=True)
        )
