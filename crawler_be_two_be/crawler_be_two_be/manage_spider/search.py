import re
import logging
from bs4 import BeautifulSoup as BS

from ..utils.config import main_link_search, _data_origin
from ..utils.work_with_text_and_number import dedent_func
from ..utils.working_with_url import UrlConfig
from ..utils.param_query import extra_param

logger = logging.getLogger(__name__)


class Search:
    def __init__(self, response_):
        self.response = response_
        self.url = UrlConfig()
        self.soup = BS(str(self.response.body.decode('utf-8')).replace('&lt;', '<').replace('&gt;', '>'),
                       features='lxml')

    def get_link_redirect_query(self, start_date, date_end, param_, url_=main_link_search['b2b']):
        """ :return link for GET request with fillowing redirection
            :param url_ url of search page
            :param start_date start date of period for search
            :param date_end end date of period for search
            :param param_ query link param
        """
        try:
            param_['date_start_dmy'] = start_date
            param_['date_end_dmy'] = date_end
            output_url = self.url.return_url_param(url_, param_) + extra_param
            return output_url
        except Exception as e:
            logger.error(f'{self.response.url} :: ERROR WHEN QUERY FOR SEARCH LOTS IN CURRENT PERIOD - '
                         f'{start_date} - {date_end} WAS EXCECUTED\n{e}')

    def get_links_to_trading_page(self):
        """ fetch links from response to trading pages  """
        try:
            main_lst = set()
            list_part_of_url = list()
            all_links = self.soup.find('tbody')
            if all_links:
                links = all_links.find_all('a', href=re.compile('/market/'))
                for i in links:
                    _href = i.get('href')
                    if len(_href) > 65:
                        list_part_of_url.append(_href)
                for l2 in list_part_of_url:
                    main_lst.add(self.url.url_join(_data_origin['b2b'], l2))
                return list(main_lst)
            else:
                return list()
        except Exception as ex:
            logger.error(f'{self.response.url} :: ERROR  -  LINKS TO TRADING PAGE WERE NOT FOUND AND  '
                         f'SAME ERROR IS HAPPEND\n{ex}')
            return list()

    def check_if_pagination(self):
        """ check if pagination exists or only one page """
        try:
            if pagi := self.soup.find('div', class_='pagi'):
                return pagi
            else:
                return None
        except Exception as e:
            logger.error(f'{self.response.url} :: ERROR PAGINATION {e}')

    def next_page(self, pagi_block):
        """ return next page if exists """
        try:
            link_next_page = pagi_block.find('li', class_='pagi-item pagi-item-current').find_next('a')
            if link_next_page and re.match(r'\d+', link_next_page.get_text()):
                return int(dedent_func(link_next_page.get_text()))
            else:
                return 0
        except Exception as e:
            logger.error(f'{self.response.url} :: ERROR NEXT PAGE {e}')
