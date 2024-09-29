from ..locators.locator_oazf_auction import LocatorOazfAuction
from bs4 import BeautifulSoup as BS
from ..utils.config import data_origin_url
from ..utils.check_inn_email_phone import *
from ..utils.work_with_text_and_number import *
from ..utils.working_with_url import UrlConfig
from ..utils.work_with_path_and_dir import LotFilesDir
from ..utils.working_with_time import get_time_data
import logging


logger = logging.getLogger(__name__)


class AuctionOAzfParse:

    def __init__(self, response_):
        self.response = response_
        self.loc = LocatorOazfAuction
        self.url_ = UrlConfig
        self.check = CheckIfCorrectContactInfo()
        self.dir = LotFilesDir()

    def get_trading_num_oazf(self, lot, url):
        try:
            pattern1 = re.compile(r'№?.\d+.?\d+')
            patter2 = re.compile(r'\d+.?\d+')
            title = self.response.xpath(self.loc.trading_number.format(self.get_href_lot(lot))).get()
            title = BS(str(title), features='lxml').get_text()
            title = pattern1.findall(title)
            return ''.join(patter2.findall(''.join(title)))

        except:
            logger.error(f'{self.response.url} :: INVALID DATA LOT THEAD(TRADING_NUMBER)')

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
            logger.error(f'{url}:: INVALID DATA MSG_NUMBER AUCTION OAZF')
            return None

    def case_number(self, url):
        """get and clean case number"""
        case_ = self.response.xpath(self.loc.case_number_loc).get()
        try:
            case_ = ''.join(BS(str(case_), features='lxml').get_text()).replace('№', '').replace('\\', '/').replace(' ',
                                                                                                                    '').strip()
            if len(case_) < 42:
                return dedent_func(case_)
        except:
            logger.warning(f'{url}:: INVALID CASE_NUMBER  AUCTION OAZF')
            return None


    # _trading_organizator
    @property
    def get_link_to_org_info(self):
        """parse and get link to trading organizer info"""
        td_with_link = self.response.xpath(self.loc.trading_org_loc).get()
        link = BS(td_with_link, features='lxml').findChild('a').get('href')
        if data_origin_url not in link:
            return self.url_.url_join(data_origin_url, link)
        else:
            return link

    def trading_org_oazf(self, url):
        try:
            trading_org = BS(self.response.xpath(self.loc.trading_org_loc).get(), features='lxml').get_text()
            lst_text = re.split(r',', trading_org, maxsplit=1)
            check_name = ''.join(map(lambda x: x, filter(lambda y: "@" not in y and y.isalpha() \
                                                                   or y == ' ', ''.join(lst_text[0]))))
            return str(check_name).strip()
        except:
            logger.error(f'{url}:: INVALID DATA TRADING ORGANIZATOR AUCTION')
            return None

    # # __DEBITOR__INN__
    @property
    def debitor_inn(self):
        """get debitor personal inn"""
        try:
            trade_inn = BS(self.response.xpath(self.loc.debitor_inn).get(), features='lxml').get_text()
            pattern = re.compile(r'\d{10,12}')
            if pattern:
                return ''.join(pattern.findall(trade_inn))
        except:
            return None


    # __ARBITR__INFO__
    def arbitr_manager_oazf(self, url):
        """get arbitr name"""
        try:
            manager = self.response.xpath(self.loc.arbitr_manager_loc).get()
            manager = dedent_func(BS(str(manager), features='lxml').get_text())
            pattern = re.compile(r'[^0-9:()]')
            manager_lst = re.split(r'\s', manager, maxsplit=3)
            if manager_lst:
                manager_ = ' '.join([''.join(pattern.findall(x)) for x in manager_lst[:3]])
                return manager_
            else:
                return None
        except:
            logger.warning(f'{url}:: INVALID DATA ARBITR MANAGER  OAZF')
            return None

    @property
    def arbitr_inn_oazf(self):
        """get arbitr inn"""
        inn_ = self.response.xpath(self.loc.arbitr_inn_loc).get()
        if inn_:
            inn_ = dedent_func(BS(str(inn_), features='lxml').get_text())
            return self.check.check_inn(inn_)
        else:
            return None

    def arbitr_org_oazf(self, url):
        """get arbitr company"""
        td_company = self.response.xpath(self.loc.arbitr_org_loc).get()
        if td_company:
            try:
                td_company = dedent_func(BS(str(td_company), features='lxml').get_text())
                if '(' in td_company:
                    td_company = ''.join([x if len(td_company) > 0 else None for x in re.split(r'\(', td_company, maxsplit=1)[0]])
                return td_company
            except:
                logger.error(f'{url}', exc_info=True)
        else:
            logger.warning(f'{url}:: INVALID VALUE ARBITR COMPANY')
            return None

    # __LOT__INFO__####
    def get_href_lot(self, link):
        """:arg lot pseudo link
           :return clean link example: lot_1
        """
        try:
            link = BS(str(link), features='lxml').find('a').get('href')
            return ''.join(re.findall(r'lot_\d+$', link))
        except:
            return None

    def return_loc_short_name(self, lot_number):
        """ return locator with lot number inside"""
        return self.loc.short_name_loc.format(lot_number)

    def return_loc_property_info(self, lot_number):
        """ return locator with lot number inside"""
        return self.loc.property_information_loc.format(lot_number)

    def get_lot_number(self, link, url):
        try:
            if link:
                pattern = re.compile(r'\d+$')
                return ''.join(pattern.findall(self.get_href_lot(link)))
        except:
            logger.error(f'{url} :: INVALID DATA LOT NUMBER')
            return None

    def get_lot_link(self, lot):
        return self.response.url + '#' + self.get_href_lot(lot)

    def short_name_main(self, link, url):
        """:return short name of lot description"""
        try:
            sel_xpath = self.return_loc_short_name(self.get_href_lot(link))
            desc = self.response.xpath(sel_xpath).get()
            desc = dedent_func(BS(str(desc), features='lxml').get_text())
            return desc.strip()
        except:
            logger.warning(f'{url}:: INVALID SHORT NAME LOT')
            return None

    def property_info_lot(self, link, url):
        """:return short name of lot description"""
        try:
            sel_xpath = self.return_loc_property_info(self.get_href_lot(link))
            desc = self.response.xpath(sel_xpath).get()
            desc = dedent_func(BS(str(desc), features='lxml').get_text())
            return desc.strip()
        except:
            logger.warning(f'{url}:: INVALID DATA PROPERTY INFO')
            return None

    def start_date_request_oazf(self, lot, url):
        """get date and convert format"""
        start_date_request = \
            self.response.xpath(self.loc.start_date_request_auc_loc.format(self.get_href_lot(lot))).get()
        try:
            start_date_request = get_time_data(BS(start_date_request, features="lxml").get_text(), 0, url)
            return start_date_request
        except:
            logger.error(f'{url}:: INVALID DATA START DATE REQUEST AUCTION')
            return None

    def end_date_request_oazf(self, lot, url):
        """get date and convert format"""
        end_date_request = \
            self.response.xpath(self.loc.end_date_request_auc_loc.format(self.get_href_lot(lot))).get()
        try:
            end_date_request = get_time_data(BS(end_date_request, features="lxml").get_text(), 0, url)
            return end_date_request
        except:
            logger.error(f'{url}:: INVALID DATA START DATE REQUEST AUCTION')
            return None

    def start_date_trading_oazf(self, lot, url):
        """get date and convert format"""
        start_date_trading = \
            self.response.xpath(self.loc.start_date_trading_loc.format(self.get_href_lot(lot))).get()
        try:
            start_date_trading = get_time_data(BS(start_date_trading, features="lxml").get_text(),0, url)
            return start_date_trading
        except:
            logger.warning(f'{url}:: INVALID DATA START DATE REQUEST AUCTION')
            return None

    def end_date_trading_oazf(self, lot, url):
        """get date and convert format"""
        end_date_trading = \
            self.response.xpath(self.loc.end_date_trading_loc.format(self.get_href_lot(lot))).get()
        try:
            end_date_trading = get_time_data(BS(end_date_trading, features="lxml").get_text(), 0, url)
            return end_date_trading
        except:
            logger.warning(f'{url}:: INVALID DATA START DATE REQUEST AUCTION')
            return None

    def start_price_oazf(self, lot, url):
        """get start price auction lot"""
        try:
            start_price = self.response.xpath(self.loc.start_price_loc.format(self.get_href_lot(lot))).get()
            start_price = get_price(BS(start_price, features="lxml").get_text())
            return start_price
        except:
            logger.warning(f'{url}:: INVALID DATA START PRICE')
            return None

    # _working with lot documentation
    def get_lot_table(self, lot):
        """get lot table using lot number"""
        return self.response.xpath(self.loc.doc_table_oazf_lot_loc.format(self.get_href_lot(lot))).get()

    def table_without_thead(self, *args):
        """ get lot table without title """
        try:
            table = self.get_lot_table(args)
            if table:
                soup = BS(table, features='lxml').find_all('tr', class_=lambda x: x != "thead")
                return list(map(lambda x: x, soup))
        except:
            logger.error(f'{self.response.url}:: INVALID DATA DOCUMENTS {args}', exc_info=True)


    def trading_id_oazf(self, url):
        """return last number or symbols of url"""
        id = ''.join(re.findall(r'\d+$', str(url).strip()))
        return id


    def name_file_in_db_lot(self, url, lot, original_name):
        """generate and return name of downloaded file in data base with relative path"""
        name_ = self.dir.name_in_column_files_lot(self.trading_id_oazf(url), self.get_href_lot(lot), original_name)
        return name_

    def name_file_on_server_lot(self, url, original_name):
        """:return file name on server"""
        name_ = self.dir.name_file_on_server_lot(self.trading_id_oazf(url), self.get_href_lot(lot), original_name)
        return name_

