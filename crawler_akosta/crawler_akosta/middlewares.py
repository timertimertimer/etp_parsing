import logging

from general_utils.middlewares import ETPDownloaderMiddleware

logger = logging.getLogger(__name__)


class CrawlerAkostaDownloaderMiddleware(ETPDownloaderMiddleware):
    def process_response(self, request, response, spider):
        if response.url == 'https://www.akosta.info/akosta/sessionExpired.xhtml':
            logger.debug(f'{response.url} :: SESSION EXPIRED')
            request.headers.pop(b'Cookie')
            new_request = request.replace(cookies={}, dont_filter=True)
            return new_request
        return response
