from ..locators.locator_auction import LocatorAuction
from ..utils.check_inn_email_phone import *
from ..utils.working_with_time import get_time_data
from ..utils.work_with_path_and_dir import LotFilesDir
from ..utils.config import data_origin_url
from ..utils.work_with_text_and_number import *
from ..utils.working_with_url import UrlConfig
from bs4 import BeautifulSoup as BS
import re
import logging

logger = logging.getLogger(__name__)


class AuctionParse:

    def __init__(self, response_):
        self.response = response_
        self.loc = LocatorAuction
        self.check = CheckIfCorrectContactInfo()
        self.url_ = UrlConfig
        self.dir = LotFilesDir()

    @property
    def data_origin_auction(self):
        """return url of site"""
        return data_origin_url

    def trading_id_auction(self, url):
        """return last number or symbols of url"""
        id = ''.join(re.findall(r'\d+$', str(url).strip()))
        return id

    def trading_link_auction(self, url):
        """return link of trading page"""
        return url

    def trading_number_auction(self, value):
        """return special number of current auction"""
        value = ''.join(re.findall(r'\d+$', str(value).strip()))
        return value

    def trading_type_auction(self, url):
        """check and return type (if auction)"""
        url = url
        try:
            trading_type = dedent_func(''.join(self.response.xpath(self.loc.trading_form_loc).get()))
            return trading_type
        except:
            logger.error(f'{url}::INVALID DATA TRADING TYPE')
            return None

    def trading_form_auction(self, url):
        """return form of lot (ended, active, pending, etc."""
        return self.trading_type_auction(url)

    #####___parse_page_with_trading_organizator_info_####
    @property
    def get_link_to_org_info(self):
        """parse and get link to trading organizer info"""
        td_with_link = self.response.xpath(self.loc.trading_org_loc).get()
        link = BS(td_with_link, features='lxml').findChild('a').get('href')
        if data_origin_url not in link:
            return self.url_.url_join(data_origin_url, link)
        else:
            return link

    def trading_org_auction(self, url):
        try:
            trading_org = BS(self.response.xpath(self.loc.trading_org_loc).get(), features='lxml').get_text()
            lst_text = re.split(r',', trading_org, maxsplit=1)
            check_name = ''.join(map(lambda x: x, filter(lambda y: "@" not in y and y.isalpha() \
                                                                   or y == ' ', ''.join(lst_text[0]))))
            return str(check_name).strip()
        except:
            logger.error(f'{url}:: INVALID DATA TRADING ORGANIZATOR AUCTION')
            return None

    @property
    def trading_org_inn(self):
        try:
            trade_inn = BS(self.response.xpath(self.loc.trading_org_inn).get(), features='lxml').get_text()
            pattern = re.compile(r'\d{10,12}')
            if pattern:
                return ''.join(pattern.findall(trade_inn))
        except:
            return None

    def get_phone_org(self):
        try:
            org_phone = BS(self.response.xpath(self.loc.organiz_phone_loc).get(), features='lxml').get_text()
            org_phone = self.check.check_phone(org_phone)
            return org_phone
        except:
            return ''

    def trading_org_email(self):
        return ''

    ####__MSG__NUMBER__&__CASE__NUMBER__####
    def msg_number(self, url):
        """get and clean message number"""
        td_msg = self.response.xpath(self.loc.msg_number_loc).get()
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
            case_ = ''.join(BS(str(case_), features='lxml').get_text()).replace('№', '').replace('\\', '/').replace(' ', '').strip()
            if len(case_) < 42:
                return dedent_func(case_.replace(' ', ''))
        except:
            logger.warning(f'{url}:: INVALID CASE_NUMBER  AUCTION')
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

    def address(self, url):
        try:
            address = self.response.xpath(self.loc.debtor_inn_loc).get()
            address = ''.join(re.findall(r"Адрес", address))
            if address:
                return ' '.join(address.split())
        except:
            logger.warning(f'{url}:: INVALID DEBITOR ADDRESS AUCTION')

    # __ARBITR__INFO__
    def arbitr_manager(self, url):
        """get arbitr name"""
        try:
            manager = dedent_func(self.response.xpath(self.loc.arbitr_manager_loc).get())
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
            inn_ = ''.join(re.findall(r"ИНН.+?\d{10,12}|ИНН.+?\d{12}", inn_))
            if inn_:
                return self.check.check_inn(inn=inn_)
            else:
                return None
        except:
            logger.warning(f'{url}:: INVALID ARBITR INN VALUE  AUCTION')
            return None

    def arbitr_org(self):
        """get arbitr company"""
        company = self.response.xpath(self.loc.arbitr_org_loc).get()
        company_ = ''.join([x if len(company) > 0 else None for x in re.split(r'\(', company, maxsplit=1)[0]])
        return company_

    # __LOT__INFO__####
    def short_name_main(self, url):
        """:return short name of lot description"""
        try:
            desc = dedent_func(self.response.xpath(self.loc.short_name_loc).get())
            desc_lst = ''.join([x if len(desc) > 0 and '<b>' in desc else \
                                    None for x in re.split(r'<b>', desc, maxsplit=1)[1]])
            desc = BS(desc_lst, features='lxml').get_text()
            return desc
        except:
            logger.warning(f'{url}:: INVALID DATA SHORT NAME LOT')
            return None

    @delete_extra_symbols
    @cut_lot_number
    def short_name(self, url):
        """delete lot number at the begining of the string and delete extra symbols at the begining"""
        return self.short_name_main(url)

    @get_lot_number
    def lot_number(self, url):
        """get lot numb from the short name if not exist set lot number equal one(1)"""
        return self.short_name_main(url)

    @property
    def property_info(self):
        """get property information of lot"""
        pro_info = self.response.xpath(self.loc.property_information_loc).get()
        if pro_info:
            pro_info = dedent_func(BS(pro_info, features="lxml").get_text())
            return pro_info
        else:
            return None

    def start_date_request(self, url):
        """get date and convert format"""
        start_date_request = self.response.xpath(self.loc.start_date_request_auc_loc).get()
        try:
            start_date_request = get_time_data(BS(start_date_request, features="lxml").get_text(), 0, url)
            return start_date_request
        except:
            logger.error(f'{url}:: INVALID DATA START DATE REQUEST AUCTION')
            return None

    def end_date_request(self, url):
        """get date and convert format"""
        end_date_request = self.response.xpath(self.loc.end_date_request_auc_loc).get()
        try:
            end_date_request = get_time_data(BS(end_date_request, features="lxml").get_text(), 0, url)
            return end_date_request
        except:
            logger.error(f'{url}:: INVALID DATA START DATE REQUEST AUCTION')
            return None

    def start_date_trading(self, url):
        """get date and convert format"""
        start_date_trading = self.response.xpath(self.loc.start_date_trading_loc).get()
        try:
            start_date_trading = get_time_data(BS(start_date_trading, features="lxml").get_text(), 0, url)
            return start_date_trading
        except:
            logger.warning(f'{url}:: INVALID DATA START DATE REQUEST AUCTION')
            return None

    def end_date_trading(self, url):
        """get date and convert format"""
        end_date_trading = self.response.xpath(self.loc.end_date_trading_loc).get()
        try:
            end_date_trading = get_time_data(BS(end_date_trading, features="lxml").get_text(), 0, url)
            return end_date_trading
        except:
            logger.warning(f'{url}:: INVALID DATA START DATE REQUEST AUCTION')
            return None

    def start_price(self, url):
        """get start price auction lot"""
        try:
            start_price = self.response.xpath(self.loc.start_price_loc).get()
            start_price = get_price(BS(start_price, features="lxml").get_text())
            return start_price
        except:
            logger.warning(f'{url}:: INVALID DATA START PRICE')
            return None

    def step_price(self, url):
        """get start price auction lot"""
        try:
            step_price = self.response.xpath(self.loc.step_price_loc).get()
            step_price = get_price(BS(step_price, features="lxml").get_text())
            return step_price
        except:
            logger.warning(f'{url}:: INVALID DATA STEP PRICE')
            return None

    # _WORK WITH DOCUMENTS DIRECTORY AND DOWNLOAD
    def link_doc_page(self, url):
        """get link follow to documentation page"""
        try:
            link_to_document = BS(self.response.xpath(self.loc.link_to_doc_page_loc).get(), features='lxml').a['href']
            if data_origin_url not in link_to_document:
                return self.url_.url_join(data_origin_url, link_to_document)
            else:
                return link_to_document
        except:
            logger.warning(f'{url}:: INVALID DATA REFERENCE TO DOC PAGE')
            return None

    def get_doc_table(self):
        """get table with documents related to auction"""
        return self.response.xpath(self.loc.doc_table_auc_loc).get()

    # _case when other doc table class. often it happened parsing oazf
    def get_doc_table_2(self):
        """get table with documents related to auction"""
        return self.response.xpath(self.loc.doc_table_auc_loc_2).get()

    @property
    def table_without_thead(self):
        """get table without head(title)"""
        try:
            table = self.get_doc_table()
            table2 = self.get_doc_table_2()
            if table is None:
                table = table2
            soup = BS(table, features='lxml').find_all('tr', class_=lambda x: x != "thead")
            return list(map(lambda x: x, soup))
        except:
            logger.error(f'{self.response.url}:: INVALID DATA DOCUMENTS')

    @staticmethod
    def original_name_file(*args):
        """return original name of file"""
        original_name = dedent_func(BS(str(*args), features='lxml').find('td').find_next('td').find('b').get_text())
        return original_name

    def document_link(self, *args):
        """return full link to download file"""
        doc_link = BS(str(*args), features='lxml').find('td').find_next('td').find('a').get('href')
        if data_origin_url not in doc_link:
            return self.url_.url_join(data_origin_url, doc_link)
        else:
            return doc_link

    def create_dir(self):
        """create dir where files are downloaded"""
        return self.dir.create_dir()

    def name_file_in_db(self, url, original_name):
        """generate and return name of downloaded file in data base with relative path"""
        name_ = self.dir.name_in_column_files(self.trading_id_auction(url), original_name)
        return name_

    def name_file_on_server(self, url, original_name):
        """:return file name on server"""
        name_ = self.dir.name_file_on_server(self.trading_id_auction(url), original_name)
        return name_
