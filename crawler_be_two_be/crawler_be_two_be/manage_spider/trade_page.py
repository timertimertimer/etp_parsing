import re
import logging
from icecream import ic

from ..utils.work_with_text_and_number import dedent_func
from ..utils.working_with_time import format_time_auction
from ..utils.working_with_url import UrlConfig
from ..utils.check_inn_email_etc import CheckIfCorrectContactInfo
from bs4 import BeautifulSoup as BS
from ..utils.config import _data_origin
from ..locators.locator_trading_page import TradingLocators

logger = logging.getLogger(__name__)

class TradePage:
    def __init__(self, response_):
        self.response = response_
        self.url = UrlConfig()
        self.check = CheckIfCorrectContactInfo()
        self.loc = TradingLocators
        self.soup = BS(str(self.response.body.decode('utf-8')).replace('&lt;', '<').replace('&gt;', '>'),
                       features='lxml')

    def get_trading_id(self):
        """ :return trading_id """
        try:
            trading_id = ''.join(re.findall(r'\d+/?$', self.response.url))
            return trading_id.replace('/', '')
        except Exception as ex:
            logger.error(f'{self.response.url} :: INVALID DATA TRADING ID {ex}')

    def get_trading_number(self):
        """ :return trading number """
        try:
            _h1 = self.soup.find("div", class_="s2").previous.strip()
            trading_number = ''.join(re.findall(r'\d+', _h1))
            if len(trading_number) > 0:
                return trading_number
            else:
                logger.error(f'{self.response.url} :: INVALID DATA TRADING NUMBER (else statement)')
                with open(f'{self.get_trading_id()}_error_page.txt', 'w') as f:
                    f.write(self.response.text)

        except Exception as ex:
            logger.error(f'{self.response.url} :: INVALID DATA TRADING NUMBER {ex}')

    def get_trading_form(self):
        """ :return trading form """
        try:
            trading_form = 'open'
            return trading_form
        except Exception as ex:
            logger.error(f'{self.response.url} :: INVALID DATA TRADING FORM {ex}')

    def get_organizer_link(self):
        """ :return link to organizer page """
        try:
            td_org = self.response.xpath(self.loc.organizer_link_loc).get()
            link = BS(str(td_org), features='lxml').find('a').get('href')
            return self.response.urljoin(link)
        except Exception as ex:
            logger.error(f'{self.response.url} :: ERROR link organizer {ex}')

    def get_case_number(self):
        """ :return case number """
        try:
            case = self.response.xpath(self.loc.case_number).get()
            if case:
                case = BS(str(case), features='lxml').get_text()
                return self.check.check_case_number(case)
        except Exception as ex:
            logger.error(f'{self.response.url} :: INVALID DATA CASE NUMBER {ex}')

    def get_msg_number(self):
        """ :return case number """
        try:
            msg = self.response.xpath(self.loc.msg_number).get()
            if msg:
                msg = BS(str(msg), features='lxml').get_text()
                msg = re.findall(r'\d{7,8}', msg)
                return ' '.join(msg)
        except Exception as ex:
            logger.error(f'{self.response.url} :: INVALID DATA MESSAGE NUMBER {ex}')

    def get_debtor_block(self):
        """ :return html debtor info block """
        try:
            block = self.response.xpath(self.loc.debtor_block_loc).get()
            block = BS(str(block), features='lxml')
            return block
        except Exception as ex:
            logger.error(f'{self.response.url} :: INVALID DATA DEBTOR BLOCK {ex}')

    def get_debtor_inn(self):
        """ :return debtor inn """
        try:
            all_div = self.get_debtor_block().find_all('div')
            for i in all_div:
                if re.match(r'ИНН', i.get_text(), re.IGNORECASE):
                    _inn = dedent_func(re.split(r':', i.get_text(), maxsplit=1)[-1].strip())
                    if _inn:
                        return self.check.check_inn(_inn)
        except Exception as ex:
            logger.error(f'{self.response.url} :: INVALID DATA DEBTOR INN {ex}')

    def get_arbitr_block(self):
        """ :return html arbitr info block """
        try:
            block = self.response.xpath(self.loc.arbitr_block_loc).get()
            block = BS(str(block), features='lxml')
            return block
        except Exception as ex:
            logger.error(f'{self.response.url} :: INVALID DATA DEBTOR BLOCK {ex}')
            return None

    def get_arbitr_name(self):
        """ :return arbitr full name """
        try:
            last = ''
            first = ''
            middle = ''
            all_div = self.soup.find_all('div')
            for d in all_div:
                if 'амилия' in d.get_text():
                    last = re.split(r':', d.get_text(), maxsplit=1)[-1].strip()
                if 'Имя' in d.get_text():
                    first = re.split(r':', d.get_text(), maxsplit=1)[-1].strip()
                if 'тчество' in d.get_text():
                    middle = re.split(r':', d.get_text(), maxsplit=1)[-1].strip()
            full_name = ' '.join([last, first, middle])
            return full_name
        except Exception as e:
            logger.error(f'{self.response.url} :: INVALID DATA ARBITR NAME {e}')

    def get_arbitr_inn(self):
        """ :return arbitr INN """
        try:
            all_div = self.get_arbitr_block().find_all('div')
            for i in all_div:
                if re.match(r'ИНН', i.get_text(), re.IGNORECASE):
                    _inn = dedent_func(re.split(r':', i.get_text(), maxsplit=1)[-1].strip())
                    if _inn:
                        return self.check.check_inn(_inn)
        except Exception as ex:
            logger.error(f'{self.response.url} :: INVALID DATA ARBITR INN {ex}')

    def get_arbitr_company(self):
        """ :return arbitr company """
        try:
            all_div = self.get_arbitr_block().find_all('div')
            for i in all_div:
                if re.match(r'Наименование\s', i.get_text(), re.IGNORECASE):
                    sro = dedent_func(re.split(r':', i.get_text(), maxsplit=1)[-1].strip())
                    if sro:
                        return sro
        except Exception as ex:
            logger.error(f'{self.response.url} :: INVALID DATA ARBITR COMPANY {ex}')

    # def get_org_name(self):
    #     return self.get_debtor_block()

    def get_property_info(self):
        """ :return property information about trade """
        try:
            td = self.soup.find('td', string=re.compile(r'ополнительная информация о процедуре', re.IGNORECASE))
            if td:
                td = td.parent
                lot_info = re.split(r':', td.get_text(), maxsplit=1)[-1].strip()
                return dedent_func(lot_info)
        except Exception as e:
            logger.error(f'{self.response.url} :: ERROR LOT INFO {e}')
            return None

    def get_start_date_request_auc(self):
        """ :return start date request auction(competition) """
        try:
            date = self.response.xpath(self.loc.start_date_request_loc).get()
            date = BS(str(date), features='lxml').get_text()
            return format_time_auction(date)
        except Exception as ex:
            logger.error(f'{self.response.url} :: INVALID DATA START DATE REQUEST AUCTION {ex}')

    def get_end_date_request_auc(self):
        """ :return start end request auction(competition) """
        try:
            date = self.response.xpath(self.loc.end_date_request_loc).get()
            date = BS(str(date), features='lxml').get_text()
            return format_time_auction(date)
        except Exception as ex:
            logger.error(f'{self.response.url} :: INVALID DATA END DATE REQUEST AUCTION {ex}')
            return None

    def get_start_date_trading_auc(self):
        """ :return start end request auction(competition) """
        try:
            date = self.response.xpath(self.loc.start_date_trading_loc).get()
            date = BS(str(date), features='lxml').get_text()
            return format_time_auction(date)
        except Exception as ex:
            logger.error(f'{self.response.url} :: INVALID DATA END DATE REQUEST AUCTION {ex}')
            return None

    def get_url_lot_tab(self):
        """ :return url to lot tab AUCTION"""
        try:
            param = {'action': 'lots'}
            _url = str(self.response.url).rsplit('/', maxsplit=1)[0]
            _url_tab = self.url.return_url_param(_url + '/', param)
            return _url_tab
        except Exception as ex:
            logger.error(f'{self.response.url} :: ERROR get url to lot {ex}')
            return None

    def complete_link_to_lot(self, link):
        """ :return complete link with scheme to lot  """
        try:
            url = self.url.url_join(_data_origin['b2b'][:-1], link)
            return url
        except Exception as ex:
            logger.error(f'{self.response.url} :: ERROR complete_link_to_lot {ex}')