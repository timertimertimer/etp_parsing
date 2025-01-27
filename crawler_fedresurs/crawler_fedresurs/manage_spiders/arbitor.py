from bs4 import BeautifulSoup as BS
import logging
import re
from ..utils.work_with_text_and_number import dedent_func

logger = logging.getLogger(__name__)

class Arbitor:

    def __init__(self, response_):
        self.response = response_
        self.soup = BS(str(self.response.text).replace('&lt;', '<').replace('&gt;', '>'), features='lxml')


    @property
    def get_EVENTTARGET(self):
        """return value of __EVENTTARGET for post request -> must be empty string"""
        try:
            EVENTTARGET = self.soup.find('input', id='__EVENTTARGET')['value']
            return EVENTTARGET
        except:
            logger.error(f'POST DATA __EVENTTARGET {self.response.url} :: IS ABSENT')
            return None

    @property
    def get_EVENTARGUMENT(self):
        """return value of __EVENTARGUMENT for post request -> must be empty string"""
        try:
            EVENTARGUMENT = self.soup.find('input', id='__EVENTARGUMENT')['value']
            return EVENTARGUMENT
        except:
            logger.error(f'POST DATA __EVENTARGUMENT {self.response.url} :: IS ABSENT')
            return None

    @property
    def get_VIEWSTATE(self):
        """return value of __VIEWSTATE for post request -> must be empty string"""
        try:
            VIEWSTATE = self.soup.find('input', id='__VIEWSTATE')['value']
            return VIEWSTATE
        except:
            logger.error(f'POST DATA __VIEWSTATE {self.response.url} :: IS ABSENT')
            return None

    @property
    def get_VIEWSTATEGENERATOR(self):
        """return value of __VIEWSTATEGENERATOR for post request -> must be empty string"""
        try:
            VIEWSTATEGENERATOR = self.soup.find('input', id='__VIEWSTATEGENERATOR')['value']
            return VIEWSTATEGENERATOR
        except:
            logger.error(f'POST DATA __VIEWSTATEGENERATOR {self.response.url} :: IS ABSENT')
            return None

    @property
    def get_PREVIOUSPAGE(self):
        """return value of __PREVIOUSPAGE for post request -> must be empty string"""
        try:
            PREVIOUSPAGE = self.soup.find('input', id='__PREVIOUSPAGE')['value']
            return PREVIOUSPAGE
        except:
            logger.error(f'POST DATA __PREVIOUSPAGE {self.response.url} :: IS ABSENT')
            return None

    @property
    def get_EVENTVALIDATION(self):
        """return value of __EVENTVALIDATION for post request -> must be empty string"""
        try:
            EVENTVALIDATION = self.soup.find('input', id='__EVENTVALIDATION')['value']
            return EVENTVALIDATION
        except:
            logger.error(f'POST DATA __EVENTVALIDATION {self.response.url} :: IS ABSENT')
            return None

    @property
    def get_link_to_card_arbitr(self):
        """get links to arbitr data(card)"""
        try:
            lst_links = self.soup.find_all(href=re.compile('ArbitrManagerCard'))
            if len(lst_links) > 0:
                return lst_links
            else:
                return None
        except:
            logger.error(f'{self.response.url} :: LINKS TO CARD ARBITR WSA NOT FOUND AND ERROR IS OCCURED')
            return None

    def full_name_return(self, last, first, middle):
        """arg: last, first, middle name"""
        try:
            if last and isinstance(last, str):
                last = dedent_func(last)
            else:
                last = ''
            if first and isinstance(first, str):
                first = dedent_func(first)
            else:
                first = ''
            if middle and isinstance(middle, str):
                middle = dedent_func(middle)
            else:
                middle = ''
            return last + ' ' + first + ' ' + middle

        except:
            return None
