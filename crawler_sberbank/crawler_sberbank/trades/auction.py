import re
import logging
from ..locators.locator_trades import LoacatorAuction
from ..utils.manage_spider import deep_get_dict, sort_trading_type, get_trading_form
from ..utils.working_with_time import format_time
from ..utils.work_with_text_and_number import *
from ..utils.check_inn_email_phone import CheckIfCorrectContactInfo
from bs4 import BeautifulSoup as BS

logger = logging.getLogger(__name__)


class AuctionParse:
    def __init__(self, data, url):
        self.url = url
        self.data = data
        self.loc = LoacatorAuction
        self.check = CheckIfCorrectContactInfo()

    @property
    def trading_id(self):
        """return trading id - last numbers of url"""
        try:
            pattern = re.compile('\d+$')
            return ''.join(pattern.findall(self.url))
        except:
            logger.error(f'{self.url} :: INVALID DATA TRADING ID')
            return None

    @property
    def trading_link_auc(self):
        return self.url

    @property
    def trading_number_auc(self):
        try:
            trading_number = deep_get_dict(self.data, 'Purchase.PurchaseinfoPanel.PurchaseInfo.PurchaseCode')
            return dedent_func(BS(str(trading_number), features='lxml').get_text()).strip()
        except:
            logger.error(f'{self.url} th:: WITHOUT TRADING NUMBER')
            return None

    @property
    def trading_type_auc(self):
        try:
            trading_type = sort_trading_type(deep_get_dict(
                self.data, 'Purchase.PurchaseinfoPanel.PurchaseInfo.PurchaseTypeInfo.PurchaseTypeName'
            ))
            return dedent_func(BS(str(trading_type), features='lxml').get_text()).strip()
        except:
            logger.error(f'{self.url} :: INVALID DATA TRADING TYPE', exc_info=True)
            return None

    @property
    def trading_form_auc(self):
        try:
            trading_type = get_trading_form(deep_get_dict(
                self.data, 'Purchase.PurchaseinfoPanel.PurchaseInfo.PurchaseTypeInfo.PurchaseTypeName'
            ))
            return dedent_func(BS(str(trading_type), features='lxml').get_text()).strip()
        except:
            logger.error(f'{self.url} :: INVALID DATA TRADING TYPE', exc_info=True)
            return None

    @property
    def trading_org_auc(self):
        """return name or company name of trading organizer"""
        try:
            td_org = deep_get_dict(self.data, 'Purchase.PurchaseinfoPanel.OrganizatorInfo.orgname')
            td_org = dedent_func(BS(str(td_org), features='lxml').get_text()).strip()
            return ''.join(re.sub(r'\s+', ' ', td_org))
        except:
            logger.warning(f'{self.url} :: INVALID DATA ORGANIZER')

    @property
    def trading_org_inn(self):
        """check and return trading organizer inn"""
        try:
            td_inn = deep_get_dict(
                self.data, 'Purchase.PurchaseinfoPanel.OrganizatorInfo.orginn'
            )
            text_inn = dedent_func(BS(str(td_inn), features='lxml').get_text()).strip()
            return self.check.check_inn(text_inn)
        except:
            return None

    def get_phone_number(self):
        """get phone number of organizer"""
        try:
            phone = deep_get_dict(self.data, 'Purchase.PurchaseinfoPanel.OrganizatorInfo.orgphone', default='')
            phone = dedent_func(BS(str(phone), features='lxml').get_text()).replace(';', '').strip()
            return self.check.check_phone(phone)
        except:
            return None

    def get_email(self):
        """get email of organizer"""
        try:
            email = deep_get_dict(self.data, 'Purchase.PurchaseinfoPanel.OrganizatorInfo.orgemail', default='')
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

    @property
    def get_msg_number(self):
        try:
            msg_number = deep_get_dict(self.data, 'Purchase.PurchaseinfoPanel.PurchaseInfo.IDEFRSB')
            return dedent_func(BS(str(msg_number), features='lxml').get_text()).strip()
        except:
            return None

    @property
    def get_case_number(self):
        """return case number of judgement"""
        try:
            case_number = deep_get_dict(self.data, 'Purchase.DebtorInfo.BusinesInfo.businessno')
            case_number = dedent_func(BS(str(case_number), features='lxml').get_text()).replace(';', '').replace('№',
                                                                                                                 '').strip()
            if len(case_number) < 38:
                return case_number.replace('\\', '/').replace(' ', '').strip()
        except:
            return None

    @property
    def get_debitor_inn(self):
        """return INN of debitor"""
        try:
            td_inn = deep_get_dict(self.data, 'Purchase.DebtorInfo.DebtorInfo.DebtorINN')
            text_inn = dedent_func(BS(str(td_inn), features='lxml').get_text()).strip()
            return self.check.check_inn(text_inn)
        except:
            return None

    @property
    def get_arbitr_manager(self):
        """return name of arbitr manager"""
        try:
            td_arbitr = deep_get_dict(
                self.data, 'Purchase.DebtorInfo.CrisicManagerInfo.crisicmanagerfullname'
            )
            td_arbitr = dedent_func(BS(str(td_arbitr), features='lxml').get_text()).strip()
            return ''.join(re.sub(r'\s+', ' ', td_arbitr))
        except:
            logger.warning(f'{self.url} :: INVALID DATA ARBITR MANAGER NAME')

    @property
    def get_arbitr_manager_inn(self):
        """return INN of arbitr"""
        try:
            td_inn = deep_get_dict(
                self.data, 'Purchase.DebtorInfo.CrisicManagerInfo.crisismanagerinn'
            )
            text_inn = dedent_func(BS(str(td_inn), features='lxml').get_text()).strip()
            return self.check.check_inn(text_inn)
        except:
            return None

    @property
    def get_arbitr_manager_org(self):
        """return arbitr manager org"""
        try:
            td_company = deep_get_dict(
                self.data,
                'Purchase.DebtorInfo.CrisicManagerInfo.arbitrageorganizationpanel.arbitrageorganizationname'
            )
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
    def get_start_date_requests(self):
        try:
            return format_time(deep_get_dict(self.data, 'Purchase.Step6.RequestInfo.RequestStartDate'))
        except:
            logger.error(f'{self.url} :: INVALID DATA START DATE REQUEST AUCTION')

    @property
    def get_end_date_requests(self):
        try:
            return format_time(deep_get_dict(self.data, 'Purchase.Step6.RequestInfo.RequestStopDate'))
        except:
            logger.error(f'{self.url} :: INVALID DATA END DATE REQUEST AUCTION')

    @property
    def get_start_date_trading(self):
        try:
            return format_time(deep_get_dict(self.data, 'Purchase.Step6.Terms.PurchaseAuctionStartDate'))
        except:
            logger.error(f'{self.url} :: INVALID START DATE TRADING AUCTION')

    @property
    def get_end_date_trading(self):
        try:
            return format_time(deep_get_dict(self.data, 'Purchase.Step6.ResultInfo.AuctionResultDate'))
        except:
            logger.error(f'{self.url} :: INVALID END DATE TRADING AUCTION')

    @property
    def get_lot_id(self):
        pattern = re.compile(r'\d+$')
        return ''.join(pattern.findall(self.url))

    @property
    def get_lot_link(self):
        return ''.join(self.url)

    @property
    def get_lot_number(self):
        lot_number = deep_get_dict(self.data, 'BidView.Bids.BidInfo.BidNo')
        try:
            lot_number = dedent_func(BS(str(lot_number), features='lxml').get_text()).strip()
            if int(lot_number):
                return lot_number
        except:
            logger.warning(f'{self.url} :: INVALID DATA LOT NUMBER')
            return '1'

    @property
    def get_short_name(self):
        short_name = deep_get_dict(self.data, 'BidView.Bids.BidInfo.BidName')
        try:
            short_name = dedent_func(BS(str(short_name), features='lxml').get_text()).strip()
            if short_name:
                return short_name
        except:
            return None

    @property
    def get_lot_info(self):
        lot_info = deep_get_dict(self.data, 'BidView.Bids.BidDebtorInfo.DebtorBidName')
        try:
            lot_info = dedent_func(BS(str(lot_info), features='lxml').get_text()).strip()
            if lot_info:
                return lot_info
        except:
            return None

    @property
    def get_property_info(self):
        property_info = deep_get_dict(self.data, 'BidView.Bids.BidDebtorInfo.BidInventoryResearchType')
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
        start_price = deep_get_dict(self.data, 'BidView.Bids.BidTenderInfo.BidPrice')
        start_price = re.sub(r'\s', '', start_price)
        pattern = re.compile(r'\d+\.\d{1,2}')
        try:
            start_price = dedent_func(BS(str(start_price), features='lxml').get_text()).strip()
            if start_price:
                return round(float(''.join(pattern.findall(start_price)[0])), 2)
        except:
            logger.error(f'{self.url} :: INVALID DATA START PRICE AUCTION')
            return None

    @property
    def get_step_price(self):
        step_price = deep_get_dict(self.data, 'BidView.Bids.BidTenderInfo.AuctionStepRub')
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
