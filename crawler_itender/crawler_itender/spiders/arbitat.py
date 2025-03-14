from .base import ItenderBaseSpider

import logging

logger = logging.getLogger(__name__)


class ArbitatSpider(ItenderBaseSpider):
    name = 'arbitat'
    custom_settings = {
        # 'LOG_FILE': f'{name}.log',
    }
