from bs4 import BeautifulSoup as BS
import logging
import re

from general_utils import dedent_func

logger = logging.getLogger(__name__)


class LotAuctionPage:

    def __init__(self, _response, soup):
        self.response = _response
        self.soup = soup

    def get_lot_status(self):
        """ return lot status """
        active = ('идет прием заявок', 'идет приём заявок')
        pending = ('торги объявлены',)
        ended = ('заявки рассмотрены', 'идёт аукцион', 'подведение итогов', 'приём заявок завершен',
                 'рассмотрение заявок', 'торги аннулированы', 'торги не состоялись', 'торги отменены',
                 'торги приостановлены', 'торги проведены')
        try:
            status = self.soup.find('div', class_='header-block-state')
            if status:
                status = dedent_func(status.get_text()).lower()
                if status in active:
                    return 'active'
                elif status in pending:
                    return 'pending'
                elif status in ended:
                    return 'ended'
        except Exception as ex:
            logger.error(f'{self.response.url} :: INVALID DATA STATUS {ex}')

    def get_short_name(self, lot_number):
        """ :return short name of lot
            :arg lot_number
        """
        try:
            short_name = self.soup.find('label', string=re.compile(f'Лот\s?.+{lot_number}.?:', re.IGNORECASE)).parent
            short_name = short_name.get_text().strip().split(':', maxsplit=1)[-1].strip()
            return dedent_func(short_name)
        except Exception as e:
            logger.error(f'{self.response.url} :: INVALID DATA SHORT NAME {e}')

    def get_lot_info(self):
        """ return lot info field """
        try:
            lot_info = self.soup.find('label', string=re.compile('Предмет торгов', re.IGNORECASE))
            if lot_info:
                lot_info = lot_info.parent
                lot_info = lot_info.get_text().strip().split(':', maxsplit=1)[-1].strip()
                return dedent_func(lot_info)

        except Exception as e:
            logger.error(f'{self.response.url} :: INVALID DATA LOT INFO {e}')

    def get_property_info(self):
        """ :return property info """
        try:
            property_info = self.soup.find('label',
                                           string=re.compile('Порядок ознакомления с имуществом', re.IGNORECASE))
            if property_info:
                property_info = property_info.parent
                property_info = property_info.get_text().strip().split(':', maxsplit=1)[-1].strip()
                return dedent_func(property_info)

        except Exception as e:
            logger.error(f'{self.response.url} :: INVALID DATA PROPERTY INFORMATION {e}')
