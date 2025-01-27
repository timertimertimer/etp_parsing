from .auction import AuctionParse
from .auction_oazf import AuctionOAzfParse
from .competition import Competition


class ComboAuctionCompetition(AuctionParse, AuctionOAzfParse, Competition):

    def __init__(self, response_):
        self.response = response_
        self.auc = AuctionParse(self.response)
        self.oazf = AuctionOAzfParse(self.response)
        self.compet = Competition(self.response)
