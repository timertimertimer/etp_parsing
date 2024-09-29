from bs4 import BeautifulSoup as BS

import re
import logging

from crawler_zalog.utils.working_with_url import UrlConfig

logger = logging.getLogger(__name__)


class SerpPages:

    def __init__(self, resposne_):
        self.url = UrlConfig()
        self.response = resposne_
        self.soup = BS(str(self.response.body.decode('utf-8')).replace('&lt;', '<').replace('&gt;', '>'),
                       features='lxml')

    def get_links_lot(self):
        """ fetch links to page with lots info on serp page """
        try:
            _a = self.soup.findAll('a', class_='results-item__title')
            if _a:
                href = [self.response.urljoin(re.sub(r'\s', '%20', a.get('href'))) for a in _a]
                return href
            else:
                return []
        except Exception as e:
            logger.error(f'{self.response.url} :: ERROR GETTING LINKS TO LOT\n{e}')

    def get_first_lot_link(self):
        try:
            return self.get_links_lot()[0]
        except Exception as e:
            print(e)
            return None

    def update_url_lot_param(self, url, new_value):
        """ :arg url -> first url of lots for template
            :arg new_value"""
        param = 'id'
        return self.url.update_param(url, param, new_value)

    def get_org_id(self):
        """ get value of param organizationId for form data """
        try:
            org_id = self.soup.find('input', id='rootProfileId')
            _id = org_id['value']
            return _id
        except Exception as e:
            print(e)
            logger.error(f'{self.response.url} :: ERROR PARAM DATA organizationId')

    def get_priceTo(self):
        """ get value of param organizationId for form data """
        try:
            price = self.soup.find('input', id='priceTo')
            price = price['data-range-input-max']
            return int(float(price))
        except Exception as e:
            print(e)
            logger.error(f'{self.response.url} :: ERROR priceTo param')

    def get_last_page(self) -> int:
        """ return number of last page """
        try:
            last_page = self.soup.find('a', class_='pagination__last-element')
            num = last_page.get_text()
            return int(num)
        except Exception as e:
            print(e)
            logger.error(f'{self.response.url} :: ERORR GETTING LAST PAGE')
            return 0
