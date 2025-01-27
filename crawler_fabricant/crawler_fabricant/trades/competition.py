from bs4 import BeautifulSoup as BS
from ..locators.locator_competition import LocatorCompetition
from ..utils.work_with_text_and_number import *
from ..utils.working_with_time import get_time_data
from ..utils.check_inn_email_phone import *
from ..utils.config import data_origin_url
import re
import logging

logger = logging.getLogger(__name__)


class Competition:

    def __init__(self, response_):
        self.response = response_
        self.loc = LocatorCompetition
        self.check = CheckIfCorrectContactInfo()

    @property
    def trading_form_compet(self):
        """check and return type/form (if auction)"""
        try:
            trading_type = dedent_func(''.join(self.response.xpath(self.loc.trade_form).get()))
            return trading_type
        except:
            logger.error(f'{self.response.url}::INVALID DATA TRADING TYPE')
            return None

    @property
    def get_trading_org_link(self):
        try:
            all_td_info = self.response.xpath(self.loc.trading_org_td_loc).get()
            link_org = BS(str(all_td_info), features='lxml').find('a').get('href')
            return data_origin_url + ''.join(link_org)
        except:
            logger.error(f'{self.response.url} :: INVALID DATA LINK TRADING ORG INFO')

    @property
    def trading_org(self):
        try:
            all_td_info = self.response.xpath(self.loc.trading_org_td_loc).get()
            link_org = BS(str(all_td_info), features='lxml').find('a').get_text()
            return ''.join(link_org)
        except:
            logger.error(f'{self.response.url} :: INVALID DATA  TRADING ORG  NAME', exc_info=True)

    def msg_number(self, url):
        """get and clean message number"""
        td_msg = self.response.xpath(self.loc.msg_num_loc).get()
        try:
            if td_msg:
                td_msg = ''.join(BS(str(td_msg), features='lxml').get_text()).replace(',', ' ').replace('№',
                                                                                                        '').replace(';',
                                                                                                                    '').replace(
                    ':', '').strip()
                match = ''.join(re.findall(r'\d{1,2}\.\d{1,2}\.\d{2,4}', td_msg))
                if match:
                    return ''.join(td_msg).replace(match, '').replace('от', '').replace('-', '').strip()
                else:
                    msg = dedent_func(re.sub(r'\s+', ' ', td_msg))
                    msg = ' '.join([n if int(n) or n == ' ' else '' for n in (re.split(r'\s', msg))])
                    return msg
            else:
                return None
        except:
            logger.error(f'{url}:: INVALID DATA MSG_NUMBER AUCTION')
            return None

    def case_number(self, url):
        """get and clean case number"""
        case_ = self.response.xpath(self.loc.case_number_loc).get()
        try:
            case_ = ''.join(BS(str(case_), features='lxml').get_text()).replace('№', '').replace('\\', '/').replace(' ',
                                                                                                                    '').strip()
            if len(case_) < 42:
                return dedent_func(case_.replace(' ', ''))
        except:
            logger.warning(f'{url}:: INVALID CASE_NUMBER  COMPETITION')
            return None


        # __DEBITOR__INN__

    def debitor_inn(self, url):
        """get debitor personal inn"""
        try:
            inn_ = self.response.xpath(self.loc.debtor_inn_loc).get()
            inn_ = ''.join(re.findall(r"ИНН.+?\d{10,12}|ИНН.+?\d{12}", inn_))
            if inn_:
                return self.check.check_inn(inn=inn_)
            else:
                return None
        except:
            logger.warning(f'{url}:: INVALID DEBITOR INN VALUE  AUCTION')
            return None

        # __ARBITR__INFO__

    def arbitr_manager(self, url):
        """get arbitr name"""
        try:
            manager = dedent_func(self.response.xpath(self.loc.arbitr_manager_loc).get())
            manager = BS(str(manager), features='lxml').get_text()
            pattern = re.compile(r'[^0-9:()]')
            manager_lst = re.split(r'\s', manager, maxsplit=3)
            if manager_lst:
                manager_ = ' '.join([''.join(pattern.findall(x)) for x in manager_lst[:3]])
                return manager_
            else:
                return None
        except:
            logger.warning(f'{url}:: INVALID DATA ARBITR MANAGER  AUCTION')
            return None

    def arbitr_manag_inn(self, url):
        """get arbitr personal inn"""
        try:
            inn_ = self.response.xpath(self.loc.arbitr_manager_loc).get()
            inn_ = BS(str(inn_), features='lxml').get_text()
            inn_ = ''.join(re.findall(r"ИНН.+?\d{10,12}|ИНН.+?\d{12}", inn_))
            if inn_:
                return self.check.check_inn(inn=inn_)
            else:
                return None
        except:
            logger.warning(f'{url}:: INVALID ARBITR INN VALUE  AUCTION')
            return None

    @property
    def arbitr_org(self):
        """get arbitr company"""
        try:
            company = self.response.xpath(self.loc.arbitr_org_loc).get()
            company = BS(str(company), features='lxml').get_text()
            company_ = ''.join([x if len(company) > 0 else None for x in re.split(r'\(', company, maxsplit=1)[0]])
            return company_
        except:
            logger.error(f'{self.response.url} :: INVALID DATA ARBITR COMPANY')

    def start_date_request(self, url):
        """get date and convert format"""
        start_date_request = self.response.xpath(self.loc.start_date_requests).get()
        try:
            start_date_request = BS(str(start_date_request), features='lxml').get_text()
            start_date_request = get_time_data(BS(start_date_request, features="lxml").get_text(), 0, url)
            return start_date_request
        except:
            logger.error(f'{url}:: INVALID DATA START DATE REQUEST AUCTION')
            return None

    def end_date_request(self, url):
        """get date and convert format"""
        end_date_request = self.response.xpath(self.loc.end_date_requests).get()
        try:
            end_date_request = BS(str(end_date_request), features='lxml').get_text()
            end_date_request = get_time_data(BS(end_date_request, features="lxml").get_text(), 0, url)
            return end_date_request
        except:
            logger.error(f'{url}:: INVALID DATA START DATE REQUEST AUCTION')
            return None

    def start_date_trading(self, url):
        """get date and convert format"""
        start_date_trading = self.response.xpath(self.loc.start_date_trading).get()
        try:
            start_date_trading = BS(str(start_date_trading), features='lxml').get_text()
            start_date_trading = get_time_data(BS(start_date_trading, features="lxml").get_text(), 0, url)
            return start_date_trading
        except:
            logger.warning(f'{url}:: INVALID DATA START DATE REQUEST AUCTION')
            return None

    # __LOT__INFO__####
    @property
    def full_text_lot_number(self):
        """get lot number with word 'Лот'"""
        try:
            lots_desc = dedent_func(self.response.xpath(self.loc.short_name_loc).get())
            lots_desc = re.sub(r'<b>(.*?)</?b>', '', lots_desc).strip()
            pattern = re.compile(r'Лот.?№?\s?\d+', re.IGNORECASE)
            # lot_desc = dedent_func(self.response.xpath(self.loc.short_name_loc).get())
            lots_num = list(filter(lambda x: len(x) > 0, list(map(lambda y: y, pattern.findall(lots_desc)))))
            return lots_num
        except:
            logger.error(f'{self.response.url}:: INVALID DATA LOT NUMBER TENDER - FIELD SHORT NAME')
            return None

    @property
    def short_name_lots_compet(self):
        """:return short name of lot description"""
        try:
            desc = dedent_func(self.response.xpath(self.loc.short_name_loc).get())
            desc_lst = [x if len(desc) > 0 and '<b>' in desc else \
                            None for x in re.findall(r'<b>(.*?)</?b>', desc)]

            return desc_lst
        except:
            logger.error(f'{self.response.url}:: INVALID DATA SHORT NAME LOT')
            return None

    @property
    def start_price_compet(self):
        """get list of start prices competition lots"""
        try:
            td_prices = dedent_func(self.response.xpath(self.loc.start_price_comp_loc).get())
            lst_prices = list(map(lambda y: re.sub(r'\s*', '', y),
                                  list(map(lambda x: x, re.findall(r'Лот.?№?\s?\d+(.*?)руб',
                                                                   td_prices)))))
            return lst_prices

        except:
            logger.error(f'{self.response.url}:: INVALID DATA LOT START PRICES')
            return None

    @property
    def start_price_compet_2(self):
        """get list of start prices competition lots"""
        try:
            td_prices = dedent_func(self.response.xpath(self.loc.start_price_comp_loc).get())
            lst_prices = list(map(lambda y: re.sub(r'\s*', '', y),
                                  list(map(lambda x: x, re.findall(r'Лот.?№?\s?\d+(.*?)\(',
                                                                   td_prices)))))
            return lst_prices

        except:
            logger.error(f'{self.response.url}:: INVALID DATA LOT START PRICES')
            return None

    @property
    def property_info(self):
        """get property information of lot"""
        pro_info = self.response.xpath(self.loc.property_information_loc).get()
        if pro_info:
            pro_info = dedent_func(BS(pro_info, features="lxml").get_text())
            return pro_info
        else:
            return None
