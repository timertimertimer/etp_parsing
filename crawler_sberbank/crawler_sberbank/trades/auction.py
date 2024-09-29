import re
import logging
from ..locators.locator_trades import LoacatorAuction
from ..utils.working_with_time import format_time
from ..utils.work_with_text_and_number import *
from ..utils.check_inn_email_phone import CheckIfCorrectContactInfo
from bs4 import BeautifulSoup as BS

logger = logging.getLogger(__name__)

class AuctionParse:
    def __init__(self, response_):
        self.response = response_
        self.loc = LoacatorAuction
        self.check = CheckIfCorrectContactInfo()

    @property
    def count_lots(self):
        return self.response.css(self.loc.count_lots).getall()

    def trading_id_auc(self, url):
        """return trading id - last numbers of url"""
        try:
            pattern = re.compile('\d+$')
            return ''.join(pattern.findall(url))
        except:
            logger.error(f'{url} :: INVALID DATA TRADING ID')
            return None

    def trading_link_auc(self, url):
        pass


    @property
    def trading_number_auc(self):
        try:
            td_trading_number = self.response.xpath(self.loc.trading_number_loc).get()
            return dedent_func(BS(str(td_trading_number), features='lxml').get_text()).strip()
        except:
            logger.error(f'{self.response.url} th:: WITHOUT TRADING NUMBER')
            return None

    def trading_type_auc(self):
        pass

    def trading_form_auc(self):
        pass

    @property
    def trading_org_auc(self):
        """return name or company name of trading organizer"""
        try:
            td_org = self.response.xpath(self.loc.trading_organ_loc).get()
            td_org = dedent_func(BS(str(td_org), features='lxml').get_text()).strip()
            return ''.join(re.sub(r'\s+', ' ', td_org))
        except:
            logger.warning(f'{self.response.url} :: INVALID DATA ORGANIZER')

    @property
    def trading_org_inn(self):
        """check and return trading organizer inn"""
        try:
            td_inn = self.response.xpath(self.loc.trading_organ_inn_loc).get()
            text_inn = dedent_func(BS(str(td_inn), features='lxml').get_text()).strip()
            return self.check.check_inn(text_inn)
        except:
            return None

    def get_phone_number(self):
        """get phone number of organizer"""
        try:
            phone = self.response.xpath(self.loc.trading_org_phone_loc).get()
            phone = dedent_func(BS(str(phone), features='lxml').get_text()).replace(';', '').strip()
            return self.check.check_phone(phone)
        except:
            return None

    def get_email(self):
        """get email of organizer"""
        try:
            email = self.response.xpath(self.loc.trading_org_email_loc).get()
            email = dedent_func(BS(str(email), features='lxml').get_text()).replace(';', '').strip()
            return self.check.check_email(email)
        except:
            return None

    @property
    def trading_org_contacts(self):
        """return dict that include email and phone of organizer"""
        if self.get_phone_number():
            phone = self.get_phone_number()
        else:
            phone = None
        if self.get_email():
            email = self.get_email()
        else:
            email = None
        return {'email': email, 'phone': phone}

    def get_msg_number(self):
        return None

    @property
    def get_case_number(self):
        """return case number of judgement"""
        try:
            case_number = self.response.xpath(self.loc.case_number_loc).get()
            case_number = dedent_func(BS(str(case_number), features='lxml').get_text()).replace(';', '').replace('№', '').strip()
            if len(case_number) < 38:
                return case_number.replace('\\', '/').replace(' ', '').strip()
        except:
            return None

    @property
    def get_debitor_inn(self):
        """return INN of debitor"""
        try:
            td_inn = self.response.xpath(self.loc.debitor_inn_loc).get()
            text_inn = dedent_func(BS(str(td_inn), features='lxml').get_text()).strip()
            return self.check.check_inn(text_inn)
        except:
            return None

    @property
    def get_arbitr_manager(self):
        """return name of arbitr manager"""
        try:
            td_arbitr = self.response.xpath(self.loc.arbitr_manager_loc).get()
            td_arbitr = dedent_func(BS(str(td_arbitr), features='lxml').get_text()).strip()
            return ''.join(re.sub(r'\s+', ' ', td_arbitr))
        except:
            logger.warning(f'{self.response.url} :: INVALID DATA ARBITR MANAGER NAME')

    @property
    def get_arbitr_manager_inn(self):
        """return INN of arbitr"""
        try:
            td_inn = self.response.xpath(self.loc.arbitr_inn_loc).get()
            text_inn = dedent_func(BS(str(td_inn), features='lxml').get_text()).strip()
            return self.check.check_inn(text_inn)
        except:
            return None

    @property
    def get_arbitr_manager_org(self):
        """return arbitr manager org"""
        try:
            td_company = self.response.xpath(self.loc.arbitr_org_loc).get()
            td_company = dedent_func(BS(str(td_company), features='lxml').get_text()).strip()
            if '(' in td_company:
                td_company = ''.join(
                    [x if len(td_company) > 0 else None for x in re.split(r'\(', td_company, maxsplit=1)[0]])
                return ''.join(td_company)
            else:
                return td_company
        except:
            return None

    @property
    def get_lot_id(self):
        pattern = re.compile(r'\d+$')
        return ''.join(pattern.findall(self.response.url))

    @property
    def get_lot_link(self):
        return ''.join(self.response.url)

    @property
    def get_lot_number(self):
        lot_number = self.response.xpath(self.loc.lot_number_loc).get()
        try:
            lot_number = dedent_func(BS(str(lot_number), features='lxml').get_text()).strip()
            if int(lot_number):
                return lot_number
        except:
            logger.warning(f'{self.response.url} :: INVALID DATA LOT NUMBER')
            return '1'

    @property
    def get_short_name(self):
        short_name = self.response.xpath(self.loc.short_name_loc).get()
        try:
            short_name = dedent_func(BS(str(short_name), features='lxml').get_text()).strip()
            if short_name:
                return short_name
        except:
            return None

    @property
    def get_lot_info(self):
        lot_info = self.response.xpath(self.loc.lot_info_loc).get()
        try:
            lot_info = dedent_func(BS(str(lot_info), features='lxml').get_text()).strip()
            if lot_info:
                return lot_info
        except:
            return None

    @property
    def get_property_info(self):
        property_info = self.response.xpath(self.loc.property_info).get()
        try:
            property_info = dedent_func(BS(str(property_info), features='lxml').get_text()).strip()
            if property_info:
                return property_info
        except:
            return None

    @property
    def start_date_request(self):
        """return start date request"""
        try:
            td_date = self.response.xpath(self.loc.start_date_request_loc).get()
            td_date = dedent_func(BS(str(td_date), features='lxml').get_text()).strip()
            td_date = ''.join(re.sub(r'\s+', ' ', td_date))
            if td_date:
                return format_time(td_date)
            else:
                logger.error(f'{self.response.url} :: INVALID DATA DATES')
        except:
            logger.error(f'{self.response.url} :: INVALID DATA START DATE REQUEST AUCTION')
            return None

    @property
    def end_date_request(self):
        """return end date request"""
        try:
            td_date = self.response.xpath(self.loc.end_date_request_loc).get()
            td_date = dedent_func(BS(str(td_date), features='lxml').get_text()).strip()
            td_date = ''.join(re.sub(r'\s+', ' ', td_date))
            if td_date:
                return format_time(td_date)
            else:
                logger.error(f'{self.response.url} :: INVALID DATA DATES')
        except:
            logger.error(f'{self.response.url} :: INVALID DATA END DATE REQUEST AUCTION')
            return None

    @property
    def start_date_trading(self):
        """return start date trading"""
        try:
            td_date = self.response.xpath(self.loc.start_date_trading_loc).get()
            td_date = dedent_func(BS(str(td_date), features='lxml').get_text()).strip()
            td_date = ''.join(re.sub(r'\s+', ' ', td_date))
            if td_date:
                return format_time(td_date)
            else:
                logger.error(f'{self.response.url} :: INVALID DATA DATES')
        except:
            logger.error(f'{self.response.url} :: INVALID DATA START DATE TRADING AUCTION')
            return None

    @property
    def end_date_trading(self):
        """return end date trading"""
        try:
            td_date = self.response.xpath(self.loc.end_date_trading_loc).get()
            td_date = dedent_func(BS(str(td_date), features='lxml').get_text()).strip()
            td_date = ''.join(re.sub(r'\s+', ' ', td_date))
            if td_date:
                return format_time(td_date)
            else:
                logger.error(f'{self.response.url} :: INVALID DATA DATES')
        except:
            logger.error(f'{self.response.url} :: INVALID DATA END DATE TRADING AUCTION')
            return None

    @property
    def get_start_price(self):
        start_price = self.response.xpath(self.loc.start_price_loc).get()
        start_price = re.sub(r'\s', '', start_price)
        pattern = re.compile(r'\d+\.\d{1,2}')
        try:
            start_price = dedent_func(BS(str(start_price), features='lxml').get_text()).strip()
            if start_price:
                return round(float(''.join(pattern.findall(start_price)[0])), 2)
        except:
            logger .error(f'{self.response.url} :: INVALID DATA START PRICE AUCTION')
            return None

    @property
    def get_step_price(self):
        step_price = self.response.xpath(self.loc.step_price_loc).get()
        step_price = re.sub(r'\s', '', step_price)
        pattern = re.compile(r'\d+\.\d{1,2}')
        pattern1 = re.compile(r'^\d{1,2}')
        try:
            step_price = dedent_func(BS(str(step_price), features='lxml').get_text()).strip()
            step_price = ''.join(pattern.findall(step_price))
            if step_price:
                step_price = round(float(step_price), 2)
            else:
                step_price = ''.join(pattern1.findall(step_price))
                step_price = round(float(step_price), 2)
            return round(float(self.get_start_price * (step_price / 100)), 2)
        except:
            logger.error(f'{self.response.url} :: INVALID DATA STEP PRICE AUCTION')
            return None

