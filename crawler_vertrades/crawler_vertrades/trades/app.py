from .serp import SerpParse


class Combo:

    def __init__(self, response_):
        self.response = response_
        self.serp = SerpParse(self.response)
