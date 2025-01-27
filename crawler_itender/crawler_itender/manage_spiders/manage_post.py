import logging
from bs4 import BeautifulSoup as BS

logger = logging.getLogger(__name__)


class ManagePost:

    def __init__(self, _response):
        self.response = _response
        self.soup = BS(str(self.response.body.decode('utf-8')).replace('&lt;', '<').replace('&gt;', '>'),
                       features='lxml')

    def get_post_data_values(self, tag_html: str, post_argument: str) -> str or None:
        """
        :arg tag_html
        :arg post_argument
        :return value
        P.S. work only with id
         """
        try:
            tag_html = self.soup.find(tag_html, id=post_argument)
            if tag_html:
                tag_html = tag_html['value']
                return tag_html
            else:
                return ''
        except Exception as e:
            logger.error(f' :: Exeption during fetching tag {tag_html} :: {e} ')
            return ''
