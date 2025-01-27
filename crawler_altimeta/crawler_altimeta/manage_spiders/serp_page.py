from bs4 import BeautifulSoup as BS
import re

from general_utils import get_region
from ..locators.locators_serp import LocatorSerp
from ..locators.locators_trade_page import LocatorTradePage
from ..utils.check_inn_email_phone import CheckIfCorrectContactInfo
import logging

from ..utils.work_with_text_and_number import dedent_func
from ..utils.working_with_time import format_time_auction

logger = logging.getLogger(__name__)


class SerpPage:
    addresses = dict()

    def __init__(self, response_):
        self.response = response_
        self.soup = BS(str(self.response.text).replace('&lt;', '<').replace('&gt;', '>'), features='lxml')
        self.loc_serp = LocatorSerp
        self.loc_trade = LocatorTradePage
        self.check = CheckIfCorrectContactInfo()

    def retur_page_html(self):
        return self.soup

    def return_current_start_date(self):
        """ return start date request or None for check valid trading """
        _date = self.response.xpath(self.loc_trade.check_date).get()
        if _date:
            _date = BS(str(_date), features='lxml').get_text().strip()
            if re.match(r'\d{1,2}\.\d{1,2}\.\d{2,4}.*?\d{1,2}\:\d{1,2}', _date):
                _date = format_time_auction(_date)
                if _date > '2017-01-01 00:00':
                    return _date
                else:
                    return None
            else:
                logger.error(
                    f'{self.response.url} :: INVALID DATE !!!!!!!!!!!!@@@@@@@@@@@@@############# THE LOT SHOULD LOST')
                return None
        else:
            logger.error(
                f'{self.response.url} :2: INVALID DATE !!!!!!!!!!!!@@@@@@@@@@@@@############# THE LOT SHOULD LOST')
            return None

    def get_one_next_link(self):
        """ :return next link pagination or None """
        next_page = self.response.xpath(self.loc_serp.links_to_the_next_page).get()
        return next_page

    def get_links_to_trade(self):
        """ :return list with links to trading pages using regex """
        tr_with_links = self.response.xpath(self.loc_serp.links_to_trade_page).getall()
        pattern = re.compile(r"window.location.+(\/trade\/view\/purchase\/general\.html\?id=\d+).+")
        links_to_trade = [''.join(pattern.findall(x)) for x in tr_with_links]
        if len(links_to_trade) > 0:
            return links_to_trade
        else:
            return None

    # lot page. Get only info about type
    def get_original_text_type(self):
        """ get original text from td with type and form info """
        try:
            _form = self.response.xpath(self.loc_trade.trading_type_loc).get()
            _form = BS(str(_form), features='lxml').get_text().strip()
            return dedent_func(_form.lower())
        except Exception as e:
            logger.error(f'{self.response.url} :: ERROR WHILE GETTING TRADING TYPE \n{e}', exc_info=True)
            return None

    def get_trading_type(self):
        """ get tradding form on trading page """
        auction = ('открытый аукцион с открытой формой представления предложений о цене',
                   'открытый аукцион с открытой формой представления предложений о цене (банкротство)',

                   'открытый аукцион с закрытой формой представления предложений о цене',
                   'открытый аукцион с закрытой формой представления предложений о цене (банкротство)',

                   'закрытый аукцион с открытой формой представления предложений о цене',
                   'закрытый аукцион с открытой формой представления предложений о цене (банкротство)',

                   'закрытый аукцион с закрытой формой представления предложений о цене',
                   'закрытый аукцион с закрытой формой представления предложений о цене (банкротство)')
        offer = ('открытые торги посредством публичного предложения',
                 'открытые торги посредством публичного предложения (банкротство)',

                 'закрытые торги посредством публичного предложения',
                 'закрытые торги посредством публичного предложения (банкротство)')

        competition = ('открытый конкурс с открытой формой представления предложений о цене',
                       'открытый конкурс с открытой формой представления предложений о цене (банкротство)',

                       'открытый конкурс с закрытой формой представления предложений о цене',
                       'открытый конкурс с закрытой формой представления предложений о цене (банкротство)',

                       'закрытый конкурс с открытой формой представления предложений о цене',
                       'закрытый конкурс с открытой формой представления предложений о цене (банкротство)',

                       'закрытый конкурс с закрытой формой представления предложений о цене',
                       'закрытый конкурс с закрытой формой представления предложений о цене (банкротство)')
        _type = self.get_original_text_type()
        if _type in auction:
            return 'auction'
        if _type in offer:
            return 'offer'
        if _type in competition:
            return 'competition'

    def get_trading_form(self):
        """ get trading form """
        _open = ('открытый аукцион с открытой формой представления предложений о цене',
                 'открытый аукцион с открытой формой представления предложений о цене (банкротство)',

                 'открытые торги посредством публичного предложения (банкротство)',
                 'открытые торги посредством публичного предложения',

                 'открытый конкурс с открытой формой представления предложений о цене',
                 'открытый конкурс с открытой формой представления предложений о цене (банкротство)',

                 'открытый аукцион с закрытой формой представления предложений о цене',
                 'открытый аукцион с закрытой формой представления предложений о цене (банкротство)',

                 'открытый конкурс с закрытой формой представления предложений о цене',
                 'открытый конкурс с закрытой формой представления предложений о цене (банкротство)')

        _closed = ('закрытый аукцион с открытой формой представления предложений о цене',
                   'закрытый аукцион с открытой формой представления предложений о цене (банкротство)',

                   'закрытый конкурс с открытой формой представления предложений о цене',
                   'закрытый конкурс с открытой формой представления предложений о цене (банкротство)',

                   'закрытый аукцион с закрытой формой представления предложений о цене',
                   'закрытый аукцион с закрытой формой представления предложений о цене (банкротство)',

                   'закрытый конкурс с закрытой формой представления предложений о цене',
                   'закрытый конкурс с закрытой формой представления предложений о цене (банкротство)',

                   'закрытые торги посредством публичного предложения',
                   'закрытые торги посредством публичного предложения (банкротство)')
        _form = self.get_original_text_type()
        if _form in _open:
            return 'open'
        elif _form in _closed:
            return 'closed'
        elif 'ГК РФ' in _form:
            return None
        elif 'гк рф' in _form:
            return None
        else:
            logger.warning(f'{self.response.url} :: ERROR FORM, {_form}')
            return None

    @staticmethod
    def get_trading_id(url):
        match = re.findall(r'\d{4,}$', str(url).strip())
        return ''.join(match)

    def get_trading_number_from_serp_page(self):
        tr_with_links = self.response.xpath(self.loc_serp.links_to_trade_page).getall()
        pattern = re.compile(r"window.location.+(\/trade\/view\/purchase\/general\.html\?id=\d+).+")
        links = []
        for link in tr_with_links:
            soup = BS(str(link), features='lxml')
            links.append([''.join(pattern.findall(link)), soup.find('td').get_text(strip=True)])
        return links

    def get_trading_number(self) -> str or None:
        """ trading_number from h1 tag """
        _h1 = self.soup.h1.get_text()
        pattern = re.compile(r'идентификационный номер: (\d+-\D{4})\)')
        match = pattern.findall(_h1)
        if match and len(match) == 1:
            return ''.join(match)
        else:
            logger.error(f'{self.response.url} :: ERROR TRADING NUMBER')
            return None

    def get_trading_org(self):
        """ get trading organizer """
        org_name = self.response.xpath(self.loc_trade.trading_org_name_loc).get()
        org_name = BS(str(org_name), features='lxml').get_text().strip()
        return dedent_func(org_name)

    def get_org_email(self):
        """ return organizer email """
        org_email = self.response.xpath(self.loc_trade.trading_org_email_loc).get()
        org_email = BS(str(org_email), features='lxml').get_text().strip()
        return self.check.check_email(org_email)

    def get_org_phone(self):
        """ :return organizer phone """
        org_phone = self.response.xpath(self.loc_trade.trading_org_phone_loc).get()
        phone = BS(str(org_phone), features='lxml').get_text()
        return self.check.check_phone(phone)

    def get_org_contacts(self):
        return {'email': self.get_org_email(),
                'phone': self.get_org_phone()}

    def get_arbitr_name(self):
        """ :return arbitrator name """
        arb_name = self.response.xpath(self.loc_trade.arbitr_name_loc).get()
        if arb_name:
            arb_name = BS(str(arb_name), features='lxml').get_text().strip()
            return dedent_func(arb_name)
        else:
            comp_man = self.response.xpath(self.loc_trade.competiton_man).get()
            if comp_man:
                comp_man = BS(str(comp_man), features='lxml').get_text().strip()
                return dedent_func(comp_man)

    def get_arb_org(self):
        """ get arbitrator company """
        company = self.response.xpath(self.loc_trade.arbitr_org_loc).get()
        if company:
            company = BS(str(company), features='lxml').get_text().strip()
            return dedent_func(company)

    def get_msg_number(self):
        """ :return message number """
        msg = self.response.xpath(self.loc_trade.msg_number_loc).get()
        if msg and len(msg) > 0:
            msg = BS(str(msg), features='lxml').get_text().strip()
            msg = ' '.join(re.findall(r'\d{7,8}', dedent_func(msg)))
            if len(msg) > 0:
                return msg
            else:
                return None

    def get_case_number(self):
        """ return case number  """
        case = self.response.xpath(self.loc_trade.case_number_loc).get()
        case = BS(str(case), features='lxml').get_text().strip()
        return self.check.check_case_number(case)

    def get_debtor_inn(self):
        """ :return debtor's inn """
        _inn = self.response.xpath(self.loc_trade.debtor_inn_loc).get()
        _inn = BS(str(_inn), features='lxml').get_text().strip()
        return self.check.check_inn(_inn)

    def get_address(self):
        address = self.response.xpath(self.loc_trade.address_loc).get()
        address = BS(str(address), features='lxml').get_text().strip()
        if address not in self.addresses:
            self.addresses[address] = get_region(address)
        return address, self.addresses[address]
