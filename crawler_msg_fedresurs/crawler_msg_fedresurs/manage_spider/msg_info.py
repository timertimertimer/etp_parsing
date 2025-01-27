from bs4 import BeautifulSoup as BS
import logging
import re
from ..utils.work_with_text_and_number_cookies import dedent_func, return_complex_cookies
from ..utils.working_with_url import UrlConfig
from ..locators.serp_list_locator import SerpListLocator
from ..utils.msg_types import msg_types as mt

logger = logging.getLogger(__name__)


class MsgInfo:

    def __init__(self, response_):
        self.response = response_
        self.url = UrlConfig()
        self.loc = SerpListLocator
        self.soup = BS(str(self.response.body.decode('utf-8')).replace('&lt;', '<').replace('&gt;', '>'),
                       features='lxml')

    @staticmethod
    def return_msg_types_set():
        new_set = set([y for x in list(mt.values()) for y in x])
        return new_set

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

    @staticmethod
    def complex_cookie(cookies: list, text, type_, date_from, date_to) -> str:
        return return_complex_cookies(cookies, text, type_, date_from, date_to)

    @property
    def count_visible_pagination(self):
        """check how many pagination pages are on the main page"""
        try:
            tags_link_pagination = self.response.css('a[href *= "Page$"]').getall()
            return tags_link_pagination
        except:
            logger.error(f'{self.response.url} pagination error')
            return list()

    def link_to_msg_page(self):
        """finding and returning links to message page"""
        try:
            links = self.soup.find_all(href=re.compile('MessageWindow\.aspx'))
            return links
        except:
            return list()

    def get_link_text(self, link):
        """:return text of link that follow to msg_page"""
        try:
            if link:
                text = BS(str(link), features='lxml').find('a').get_text()
                return dedent_func(text.strip())
        except Exception as e:
            logger.error(f'{self.response.url} :: Error Getting Link Text With Type Of Msg\n{e}')

    @staticmethod
    def get_only_href(tag_a: str):
        """get tag <a> and return only value of 'href' """
        try:
            if tag_a:
                return ''.join(BS(str(tag_a), features='lxml').find('a').get('href'))
        except Exception as e:
            print(tag_a)
            logger.error(f'{e}', exc_info=True)

    def get_EVENTTARGET_from_tag(self, tag_a: str):
        """get tag <a> from class pager(pagination)"""
        try:
            if tag_a:
                a = BS(str(tag_a), features='lxml').find('a')
                _event = self.url.make_url_unquote(''.join(re.findall(r'ctl.+ges', str(a))))
                return _event
        except Exception as e:
            logger.error(f'{e}', exc_info=True)

    @staticmethod
    def get_EVENTARGUMENT_from_tag(tag_a: str):
        """get tag <a> from class pager(pagination) return page number as param (Page$...)"""
        try:
            if tag_a:
                a = BS(str(tag_a), features='lxml').find('a')
                page_number = a.get_text()
                return f'Page${page_number}'
        except Exception as e:
            logger.error(f'{e}', exc_info=True)

    # WORKING WITH PAGINATION
    def pagination_tag_with_text(self):
        """return tag with text? how many message are shown"""
        try:
            tag_tr = self.soup.find('table', id=self.loc.id_text_num_msg).find('tr').findNext('td')
            return tag_tr
        except:
            return None

    def get_text_about_msg_number(self):
        """get text under table with msg with text example (Показано с 1 по 6 (Всего: 6))"""
        try:
            tag_ = self.pagination_tag_with_text()
            if tag_ and len(tag_) > 0:
                tag = BS(str(tag_), features='lxml').get_text()
                return dedent_func(tag)
            else:
                return None
        except Exception as e:
            logger.error(f'{tag_}\n{e}')

    def get_total_msg(self):
        """:return number of total msg in one period"""
        try:
            text = self.get_text_about_msg_number()
            if text and len(text) > 0:
                match1 = ''.join(re.findall(r'\d+\)$', text))
                if match1:
                    match2 = ''.join(re.findall(r'\d+', match1))
                    if match2 and len(match2) > 0:
                        return match2
        except:
            return None

    # END WORKING WITH PAGINATION

    @staticmethod
    def get_page_number(td, current_page: int) -> int or None:
        """get tag td(with tag <a>) and check if next page bigger than current"""
        if td and current_page:
            a = BS(str(td), features='lxml').find('a')
            page_number = a.get_text()
            try:
                if isinstance(int(page_number), int):
                    if current_page < int(page_number):
                        return int(page_number)
                    else:
                        return None
            except ValueError as e:
                logger.error(f'{e}', exc_info=True)

    @property
    def get_current_page(self):
        """return current page of pagination"""
        try:
            current_page = self.soup.find('tr', class_="pager").find_next('span').get_text()
            if re.match(r'\d+', ''.join(current_page)):
                return int(current_page)
            else:
                return None
        except:
            return 0

    @property
    def get_next_page(self):
        """return next page of pagination"""
        try:
            next_page = self.return_tag_a_pagination
            if next_page:
                a = BS(str(next_page), features='lxml').find('a')
                next_page = a.get_text()
                if re.match(r'\d+', next_page):
                    return int(next_page)
                else:
                    return None
        except Exception as e:
            logger.error(f'{e}', exc_info=True)
        # else:
        #     if self.get_current_page:
        #         return self.get_current_page
        #     else:
        #         raise Exception

    @property
    def return_tag_a_pagination(self):
        try:
            a = self.soup.find('tr', class_="pager").find_next('span').find_next('td').find_next('a')
            return a
        except:
            return None
