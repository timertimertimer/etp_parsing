from .base import ItenderBaseSpider

import logging

logger = logging.getLogger(__name__)


class CenterrSpider(ItenderBaseSpider):
    name = 'centerr'
