from .lot_page import LotPage


class Combo:
    def __init__(self, response_):
        self.response = response_
        self.lot = LotPage(self.response)
