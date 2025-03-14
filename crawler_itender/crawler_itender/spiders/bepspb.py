import logging

from general_utils import headers
from .base import ItenderBaseSpider

logger = logging.getLogger(__name__)


class BepspbSpider(ItenderBaseSpider):
    name = 'bepspb'
    custom_settings = {
        # 'LOG_FILE': f'{name}.log',
        'DEFAULT_REQUEST_HEADERS': headers | {'Accept-Encoding': 'gzip, deflate'}
    }
