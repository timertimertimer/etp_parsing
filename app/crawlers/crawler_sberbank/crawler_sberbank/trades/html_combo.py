from bs4 import BeautifulSoup


class HTMLCombo:
    def __init__(self, response):
        self.response = response
        self.soup = BeautifulSoup(response.text, "lxml")
