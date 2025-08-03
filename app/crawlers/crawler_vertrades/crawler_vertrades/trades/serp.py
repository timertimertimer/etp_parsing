from bs4 import BeautifulSoup as BS

from app.utils import logger


class SerpParse:
    def __init__(self, response_):
        self.response = response_
        self.soup = BS(self.response.text, "lxml")

    def get_trading_links(self):
        try:
            links = self.soup.find_all("a", class_="row-link")
            links = set([l.get("href") for l in links])
            return links
        except Exception as e:
            logger.warning(
                f"{self.response.url} :: INVALID DATA DURING FETCHING TRADING LINKS {e}",
                exc_info=True,
            )
            return None
