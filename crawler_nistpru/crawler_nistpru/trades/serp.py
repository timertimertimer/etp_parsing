from bs4 import BeautifulSoup as BS
from ..utils.working_with_url import UrlConfig
import logging
import re
from ..utils.config import _trade_link

logger = logging.getLogger(__name__)


class SerpParse:
    def __init__(self, resposne_):
        self.response = resposne_
        self._url = UrlConfig()
        self.soup = BS(str(self.response.body.decode('utf-8')).replace('&lt;', '<').replace('&gt;', '>'),
                       features='lxml')

    def get_current_page(self):
        """ return current page of pagination """
        try:
            pag_ul = self.soup.find("ul", class_="pagination")
            if pag_ul:
                active_page = pag_ul.find("li", class_="active").get_text()
                if re.match(r'\d+', active_page):
                    return int(active_page)
                else:
                    logger.error(f'{self.response.url} :: ACTIVE PAGE NOT AN INTEGER')
                    return 0
            else:
                logger.error(f'{self.response.url} :: PAGINATION TAG NOT FOUND')
                return 0
        except Exception as e:
            logger.error(f'{self.response.url} :: INVALID DATA CURRENT PAGE {e}')
            return 1

    def get_next_page(self):
        """ return next page """
        try:
            pag_ul = self.soup.find("ul", class_="pagination")
            if pag_ul:
                active_page = pag_ul.find("li", class_="active")
                next_page = active_page.findNext('li')
                if next_page:
                    next_page = next_page.get_text()
                    if re.match(r'\d+', next_page):
                        return int(next_page)
                    else:
                        return 0
            else:
                return 0
        except Exception as e:
            logger.error(f'{self.response.url} :: INVALID DATA NEXT PAGE {e}')

    def links_to_trade(self) -> list:
        """ return list with trading list """
        set_links = set()
        set_number = set()
        try:
            tbody = self.soup.find('table', class_='data').find('tbody')
            tr_list = tbody.find_all('tr')
            if tr_list:
                for tr in tr_list:
                    td = tr.find_all('td')[0].get_text()
                    link = re.findall(r'/trade_view.php\?trade_nid=\d+', str(tr))[0]
                    set_links.add(((_trade_link['nistp'] + link), td))

                return list(set_links)
        except Exception as e:
            logger.error(f'{self.response.url} :: INVALID DATA DURING GETTING LINKS TO TRADE {e}')
            return list()
