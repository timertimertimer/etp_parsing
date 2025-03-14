from .base import ItenderBaseSpider

import logging

logger = logging.getLogger(__name__)


class ArbbitlotSpider(ItenderBaseSpider):
    name = "arbbitlot"
    custom_settings = {
        # 'LOG_FILE': f'{name}.log',
    }
