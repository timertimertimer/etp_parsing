import re
import logging
from bs4 import BeautifulSoup as BS
from icecream import ic

from crawler_be_two_be.utils.work_with_text_and_number import dedent_func

logger = logging.getLogger(__name__)


class OrgPage:
    def __init__(self, response_):
        self.response = response_
        self.soup = BS(str(self.response.body.decode('utf-8')).replace('&lt;', '<').replace('&gt;', '>'),
                       features='lxml')

    def get_name(self):
        """ :return full name of organizer or company name if not a person """
        try:
            org_name_company = self.soup.find('td', string=re.compile('олное наименование', re.IGNORECASE))
            org_name_fio = self.soup.find('td', string=re.compile('Ф.И.О.', re.IGNORECASE))
            if org_name_fio:
                name = org_name_fio.findNext('td').get_text().strip()
                name = name.replace('ИП', '').strip()
                name = name.replace('Индивидуальный предприниматель', '').strip()
            elif org_name_company:
                name = org_name_company.findNext('td').get_text().strip()
                name = name
            else:
                name = ''
            return dedent_func(name).replace('Индивидуальный предприниматель', '').strip()
        except Exception as ex:
            logger.error(f'{self.response.url} :: ERROR ORGANIZER NAME {ex}', exc_info=True)
            return None

    def get_inn(self, arbitr_name, arbitr_inn):
        """ :return inn  """
        try:
            _inn = self.soup.find('td', string=re.compile('ИНН', re.IGNORECASE))
            if _inn:
                _inn = _inn.findNext('td').get_text().strip()
                if re.match(r'\d{10,12}', _inn):
                    return _inn
            else:
                if self.compare_arb_name_and_org_name(arbitr_name):
                    return arbitr_inn
        except Exception as ex:
            logger.error(f'{self.response.url} :: INVALID DATA INN ORG {ex}')

    def compare_arb_name_and_org_name(self, arb_name):
        """ check if arbitr and organizer are the same persone """
        try:
            arb = arb_name.lower().replace("индивидуальный предприниматель", "").title().strip()
            org = self.get_name().lower().replace("индивидуальный предприниматель", "").title().strip()
            if org == arb:
                return True
            else:
                return None
        except Exception as e:
            logger.error(f'{self.response.url} :: ERROR COMPARE ARB NAME AND ORG NAMES {e}')