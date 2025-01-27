import logging
from bs4 import BeautifulSoup as BS

logger = logging.getLogger(__name__)


class OrgCompany:

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

    def double_quote_into_arrow(self, text):
        """replace this quotes (" ") to that ( '«')  """
        org = text
        first_position = org.find('"')
        last_position = org.rfind('"')
        replace_quote = ''.join(list(org[:first_position])) + '«' + ''.join(
            list(org[first_position + 1:last_position])) + '»'
        return replace_quote
