# -*- coding: utf-8 -*-
from .offer_spider import OfferSpider
from .auction_spider import AuctionSpider


class Compose:
    def __init__(self, response_):
        super(Compose, self).__init__()
        self.response = response_
        self.offer = OfferSpider(self.response)
        self.auction = AuctionSpider(self.response)
