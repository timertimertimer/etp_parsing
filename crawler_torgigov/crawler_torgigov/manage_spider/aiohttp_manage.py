import re

from bs4 import BeautifulSoup as BS
from bs4 import CData
import logging

from .finished_section import MAIN_URL
from ..utils.working_with_url import UrlConfig

logger = logging.getLogger(__name__)


class ChangeLink:

    def __init__(self):
        self.url = UrlConfig()

    def change_sequence_of_query(self, url):
        """ change_sequence_of_query: second param take fisrt place and second vice versa """
        try:
            param_query = self.url.return_query_dict(url)
            if len(param_query.keys()) == 2:
                first = list(param_query.keys())[0]
                second = list(param_query.keys())[1]
                first_param = ''.join(param_query[first])
                second_param = ''.join(param_query[second])
                complete = f'?{second}={second_param}&{first}={first_param}'
                my_param = {'section', 'id'}
                all_param = {first, second}
                if my_param.issubset(all_param):
                    full_url = self.url.return_parsed_url(url)
                    return full_url.scheme + '://' + full_url.netloc + full_url.path + complete

        except Exception as ex:
            logger.error(f'{url} :{ex}: INVALID DATA DURRING CHANGE QUERY SEQUENCE', exc_info=True)

    def return_link(self, res_text):
        soup = BS(str(res_text), features='html.parser')
        for cd in soup.findAll(text=True):
            if isinstance(cd, CData):
                url_ = MAIN_URL + cd
                return url_

    def get_link_to_download(self, res_text):
        soup = BS(str(res_text), features='lxml')
        if _a := soup.find('a', string=re.compile('Сохранить файл', re.IGNORECASE)):
            href = _a.get('href')
            search_str = re.findall(r'resources.+', href)
            href = MAIN_URL + ''.join(search_str)
            return href
