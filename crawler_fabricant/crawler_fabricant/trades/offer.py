from icecream import ic

from ..utils.config import data_origin_url
from ..utils.work_with_text_and_number import *
from ..utils.working_with_time import get_time_data, format_time
from ..utils.check_inn_email_phone import *
from ..utils.work_with_path_and_dir import GeneralFilesDir
from ..locators.locator_offer import LocatorOffer
from ..spiders.fabricant import pd
from ..utils.working_with_url import UrlConfig
from ..utils.config import *
import pathlib
import re
import logging
from ..utils.download import DownloadFiles
from bs4 import BeautifulSoup as BS

logger = logging.getLogger(__name__)


class OfferParse:

    def __init__(self, response_):
        self.response = response_
        self.loc = LocatorOffer
        self.check = CheckIfCorrectContactInfo()
        self.url_ = UrlConfig()
        self.dir = GeneralFilesDir()
        self.load = DownloadFiles()

    def count_pagination_lot(self):
        """ check pagination  lot page """
        number = None
        ul = self.response.xpath(self.loc.pagination_lot_page).get()
        if ul:
            number = BS(str(ul), features='lxml')
            if len(number) > 0:
                return number.find_all('a')[-1].get_text()
        return number

    @property
    def data_origin_offer(self):
        """main url"""
        return data_origin_url

    @staticmethod
    def trading_id(url):
        """gettitng the last symbols of response.url withou backslash"""
        return ''.join(re.findall(r'http.+view/(.*)/?', url)).replace('/', '').strip()

    def count_lots(self):
        """count how many <div> with lot info (if len > 1 it mean that trading page has few lots) in this case it's
        just in case. return list of table(s)"""
        return self.response.xpath(self.loc.div_info_lot_offer).getall()

    @property
    def trading_number(self):
        """get trading number from title of trading info, offer page"""
        number = self.response.xpath(self.loc.offer_trading_number_loc2).get()
        number1 = self.response.xpath(self.loc.offer_trading_number_loc).get()
        if number is None:
            number = number1
        if number:
            number = BS(str(number), features='lxml').get_text()
            number = ''.join(re.findall(r'\d+', number))

        return number

    @property
    def trading_type(self):
        """get trading type using various selectors"""
        try:
            first_loc = dedent_func(
                BS(str(self.response.xpath(self.loc.offer_trading_type_loc1).get()), features='lxml').get_text())
            second_loc = dedent_func(
                BS(''.join(self.response.xpath(self.loc.offer_trading_type_loc2).get()), features='lxml').get_text())
            third_loc = dedent_func(
                BS(str(self.response.xpath(self.loc.offer_trading_type_loc3).get()), features='lxml').get_text())
            if first_loc != 'None':
                return str(first_loc).strip()
            elif second_loc != 'None':
                return str(second_loc).strip()
            elif third_loc != 'None':
                return str(third_loc).strip()
            else:
                return None

        except:
            logger.error(f'{self.response.url} :: INVALID DATA OFFER TRADING TYPE')

    def check_trading_type(self, response):
        """ check if trading type not a auction """
        soup = BS(str(response.text), features='lxml')
        check_type = soup.find('div', string=re.compile('Способ проведения процедуры'))
        if check_type:
            check_type = check_type.find_next('div')
            if check_type:
                c = check_type.get_text().strip()
                return dedent_func(c)
        return 'offer'

    # trading_organizer_info
    @property
    def trading_org(self):
        """get name or company name of trading org using various selectors"""
        try:
            first_loc = dedent_func(self.response.xpath(self.loc.offer_org_name_loc1).get())
            second_loc = dedent_func(
                BS(str(self.response.xpath(self.loc.offer_org_name_loc2).get()), features='lxml').get_text())
            if first_loc:
                return first_loc
            elif second_loc:
                return second_loc
            else:
                return None
        except:
            logger.warning(f'{self.response.url} :: INVALID DATA TRADING ORG - OFFER ')

    @property
    def trading_org_inn(self):
        try:
            trade_inn = BS(self.response.xpath(self.loc.offer_org_inn_loc).get(), features='lxml').get_text()
            pattern = re.compile(r'\d{10,12}')
            if pattern:
                return ''.join(pattern.findall(trade_inn))
        except:
            return None

    @property
    def get_phone_org(self):
        try:
            org_phone = BS(self.response.xpath(self.loc.offer_org_phone_loc).get(), features='lxml').get_text()
            org_phone = self.check.check_phone(org_phone)
            return org_phone
        except:
            return ''

    @property
    def trading_org_email(self):
        try:
            org_email = BS(self.response.xpath(self.loc.offer_org_email_loc).get(), features='lxml').get_text()
            org_email = self.check.check_email(org_email)
            return org_email
        except:
            return ''

    ####__MSG__NUMBER__&__CASE__NUMBER__####
    def msg_number(self, url):
        """get and clean message number"""
        td_msg = BS(self.response.text, features='lxml').find('div', string=re.compile('сообщения .* ЕФРСБ', re.IGNORECASE))
        if td_msg:
            td_msg = dedent_func(td_msg.find_next('div').get_text().strip())
        try:
            if td_msg:
                match = re.findall(r'\d{7,9}', td_msg)
                return ' '.join(match)
            else:
                return None
        except:
            logger.error(f'{url}:: INVALID DATA MSG_NUMBER OFFER', exc_info=True)
            return None

    def case_number(self, url):
        """get and clean case number"""
        case_ = self.response.xpath(self.loc.offer_case_number).get()
        try:
            case_ = ''.join(BS(str(case_), features='lxml').get_text()).replace('№', '').replace('\\', '/').replace(' ',
                                                                                                                    '').strip()
            if len(case_) < 42:
                return dedent_func(case_)
        except:
            logger.warning(f'{url}:: INVALID CASE_NUMBER  OFFER')
            return None

    # _DEBITOR_INFO
    @property
    def debitor_inn(self):
        try:
            debitor_inn = BS(self.response.xpath(self.loc.deb_inn_loc).get(), features='lxml').get_text()
            pattern = re.compile(r'\d{10,12}')
            if pattern:
                return ''.join(pattern.findall(debitor_inn))
        except:
            return None

    # _Arbitr_info
    @property
    def arbitr_name(self):
        try:
            last_name = dedent_func(
                BS(str(self.response.xpath(self.loc.arbitr_last_name).get()), features='lxml').get_text())
            name = dedent_func(BS(str(self.response.xpath(self.loc.arbitr_name).get()), features='lxml').get_text())
            middle_name = dedent_func(
                BS(str(self.response.xpath(self.loc.arbitr_mid_name).get()), features='lxml').get_text())
            return ' '.join(list(filter(lambda x: x != 'None', [last_name, name, middle_name])))
        except:
            pass

    @property
    def arbitr_inn(self):
        try:
            arb_inn = BS(self.response.xpath(self.loc.arbitr_inn).get(), features='lxml').get_text()
            pattern = re.compile(r'\d{10,12}')
            if pattern:
                return ''.join(pattern.findall(dedent_func(arb_inn)))
        except:
            return None

    @property
    def arbitr_org(self):
        """get arbitr company name"""
        try:
            td_company = BS(str(self.response.xpath(self.loc.arbitr_org).get()), features='lxml').get_text()
            if td_company != 'None':
                if '(' in td_company:
                    td_company = ''.join(
                        [x if len(td_company) > 0 else None for x in re.split(r'\(', td_company, maxsplit=1)[0]])
                return ''.join(dedent_func(td_company))

        except:
            logger.warning(f'{self.response.url} :: INVALID DATA TRADING ORG - OFFER ')

    # _ working with lot info
    @get_lot_number
    def get_lot_number(self, *args):
        """return lot number"""
        lot_desc = self.response.xpath(self.loc.lot_number_loc.format(self.get_table_id(args))).get()
        lot_desc = BS(str(lot_desc), features='lxml').get_text()
        return lot_desc.strip()

    def get_short_name(self, *args):
        """:return short name from lot html div sector"""
        try:
            short_name = self.response.xpath(self.loc.short_name_loc.format(self.get_table_id(args))).get()
            if short_name:
                short_name = short_name
            else:
                short_name = self.response.xpath(self.loc.short_name_loc2.format(self.get_table_id(args))).get()
            short_name = BS(str(short_name), features='lxml').get_text()
            return dedent_func(short_name)
        except:
            return None

    def property_info(self, *args):
        """:return property info from lot html div sector"""
        prop_info = self.response.xpath(self.loc.property_info_loc.format(self.get_table_id(args))).get()
        prop_info = BS(str(prop_info), features='lxml').get_text()
        return dedent_func(prop_info)

    # _Working with dates and Periods lot

    def get_table_id(self, *args):
        """:return div id related to lot table"""
        try:
            table_id = BS(str(args), features='lxml').find('div', class_='panel-heading').get('id')
            return table_id

        except (ValueError, TypeError, Exception) as e:
            logger.critical(f'{self.response.url} :: LOT NOT FOUND', exc_info=True)

    def get_periods_table(self, *args):
        """return list of periods tables"""
        try:
            periods = self.response.xpath(self.loc.period_tables_loc.format(self.get_table_id(args))).getall()
            return periods
        except:
            logger.error(f'{self.response.url} :: PERIODS NOT FOUND', exc_info=True)

    def start_date_request(self, *args):
        """:arg html div with lot info"""
        lst_periods = self.get_all_periods(args)
        try:
            return lst_periods[0].get('start_date_requests')
        except:
            return None

    def end_date_request(self, *args):
        """:arg html div with lot info"""
        lst_periods = self.get_all_periods(args)
        try:
            return lst_periods[-1].get('end_date_requests')
        except:
            return None

    def start_date_trading(self, *args):
        """return function start date request"""
        return self.start_date_request(args)

    def end_date_trading(self, *args):
        """:return function end_date_request"""
        return self.end_date_request(args)

    def start_price(self, *args):
        """get start price offer lot"""
        lst_periods = self.get_all_periods(args)
        try:
            return lst_periods[0].get('current_price')
        except:
            logger.warning(f'{self.response.url} :: INVALID DATA START PRICE OFFER')
            return None

    def get_all_periods(self, *args):
        """
        :arg html div with lot info
        :return list with dict values of offer periods"""
        try:
            periods = list()
            for table in self.get_periods_table(args):
                soup = BS(table, features='lxml')
                try:
                    table_ = pd.read_html(str(soup.table))
                except:
                    pass
                try:
                    if len(table_[0]) < 7 and len(table_[0]) > 2:
                        start = table_[0][1][1]
                        end = table_[0][1][2]
                        price = table_[0][1][3]
                        period = {
                            'start_date_requests': get_time_data(start, 0, url=self.response.url),
                            'end_date_requests': get_time_data(end, 0, url=self.response.url),
                            'end_date_trading': get_time_data(end, 0, url=self.response.url),
                            'current_price': get_price(price)
                        }
                        periods.append(period)
                except:
                    continue
            return periods
        except:
            logger.error(f'{self.response.url} :: INVALID DATA PERIODS OFFER', exc_info=True)

    # WORKING WITH DOCUMENTS
    def link_doc_page(self, url):
        """get link follow to documentation page"""
        try:
            link_to_document = BS(self.response.css(self.loc.doc_link_loc).get(), features='lxml').a['href']
            if data_origin_url not in link_to_document:
                return self.url_.url_join(data_origin_url, link_to_document)
            else:
                return link_to_document
        except:
            logger.error(f'{url}:: INVALID DATA REFERENCE TO DOC PAGE')
            return None

    # document procedure
    def table_doc_proc(self, id_):
        """ :return structure of table with trading documentation"""
        try:
            table_old = self.response.xpath(self.loc.old_table_doc_general.format(id_)).getall()
            table = self.response.xpath(self.loc.doc_proc_table).getall()
            if len(table) == 0:
                table = table_old
                return table
            else:
                return table
        except:
            logger.error(f'{self.response.url} :: INVALID DATA DOC TABLE')

    # document procedure
    def get_amount_of_proc_doc(self):
        """ :return amaunt of documents if table if table has counter """
        amount = self.response.xpath(self.loc.doc_proc_num_loc).get()
        if amount:
            return amount
        else:
            return None

    # document procedure
    def iteration_throughout_table_tr(self, id_, url_):
        """:return list of files values"""
        referer = self.response.url
        general = list()
        try:
            # _first check if doc table new structure
            amount = self.get_amount_of_proc_doc()
            if amount and dedent_func(amount).isdigit():
                if int(amount) > 0:
                    for tr in self.table_doc_proc(id_):
                        relative_path_f = ''
                        file_name_odj = BS(str(tr), features='lxml').find('td', class_='procedure-document-file').find(
                            'b').get_text()
                        original_name = dedent_func(file_name_odj)
                        link_etp_obj = BS(str(tr), features='lxml').find('td', class_='action'). \
                            find('div').findChild('a')['href']
                        link_etp = self.url_.url_join(data_origin_url, link_etp_obj)
                        if pathlib.Path(''.join(original_name)).suffix in lst_exet:
                            self.dir.create_dir()
                            relative_path_f = self.dir.name_in_column_files(
                                self.trading_id(url_)[:5], original_name)
                            name_on_server = self.dir.name_file_on_server(self.trading_id(url_)[:5], original_name, )
                            self.load.request_to_download(url=link_etp, referer=referer, original_name=name_on_server)
                        general.append({'original_name': original_name,
                                        'link': relative_path_f,
                                        'link_etp': self.url_.parse_url(url=link_etp)})
                return general
            else:
                table = self.table_doc_proc(id_)
                if table:
                    for tr in self.table_doc_proc(id_):
                        relative_path_f = ''
                        file_name_odj = BS(str(tr), features='lxml').find('td').find_next('td').find(
                            'b').get_text()
                        original_name = dedent_func(file_name_odj)
                        link_etp_obj = BS(str(tr), features='lxml').find('td').find_next('td').find_next('td'). \
                            find_next('td').find_next('td').findChild('a')['href']
                        link_etp = self.url_.url_join(data_origin_url, link_etp_obj)
                        if pathlib.Path(''.join(original_name)).suffix in lst_exet:
                            self.dir.create_dir()
                            relative_path_f = self.dir.name_in_column_files(
                                self.trading_id(url_)[:5], original_name)
                            name_on_server = self.dir.name_file_on_server(self.trading_id(url_)[:5],
                                                                          original_name, )
                            self.load.request_to_download(url=link_etp, referer=referer, original_name=name_on_server)
                        general.append({'original_name': original_name,
                                        'link': relative_path_f,
                                        'link_etp': self.url_.parse_url(url=link_etp)})
                return general
        except:
            logger.warning(f'{self.response.url}', exc_info=True)
            return list()

    # _ lot documents
    def get_lot_doc_table(self, id_, url):
        """get table with lots documents"""
        try:
            table = self.response.xpath(self.loc.lot_doc_table.format(id_)).getall()
            return table
        except:
            logger.warning(f'{url}:: INVALID DATA OR WITHOUT LOT TABLE ')
            return None

    def get_amount_of_lot_doc(self):
        """ :return amaunt of documents if table  has counter """
        amount = self.response.xpath(self.loc.doc_lot_amount_loc).get()
        if amount:
            return amount
        else:
            return None

    def iteration_throughout_lot_table_tr(self, id_, url_):
        """fetching lot documents"""
        try:
            lot = list()
            referer = self.response.url
            check_lot_tab = self.response.xpath(self.loc.count_lot_doc_loc).get()
            table = self.get_lot_doc_table(id_, url_)
            amount = self.get_amount_of_lot_doc()
            if table:
                if amount and dedent_func(amount).isdigit():
                    if int(amount) > 0:
                        for tr in table:
                            relative_path_f = ''
                            file_name_odj = BS(str(tr), features='lxml').find('td', class_='lot-document-file').find(
                                'b').get_text()
                            original_name = dedent_func(file_name_odj)
                            link_etp_obj = BS(str(tr), features='lxml').find('td', class_='action'). \
                                find('div').findChild('a')['href']
                            link_etp = self.url_.url_join(data_origin_url, link_etp_obj)
                            if pathlib.Path(''.join(original_name)).suffix in lst_exet:
                                self.dir.create_dir()
                                relative_path_f = self.dir.name_in_column_files(
                                    self.trading_id(url_)[:5], original_name)
                                name_on_server = self.dir.name_file_on_server(self.trading_id(url_)[:5],
                                                                              original_name, )
                                self.load.request_to_download(url=link_etp, referer=referer,
                                                              original_name=name_on_server)
                            lot.append({'original_name': original_name,
                                        'link': relative_path_f,
                                        'link_etp': self.url_.parse_url(url=link_etp)})
                    return lot
                else:
                    if table and amount is None and check_lot_tab is None:
                        for tr in table:
                            relative_path_f = ''
                            file_name_odj = BS(str(tr), features='lxml').find('td').find_next('td').find(
                                'b').get_text()
                            original_name = dedent_func(file_name_odj)
                            link_etp_obj = BS(str(tr), features='lxml').find('td').find_next('td').find_next('td'). \
                                find_next('td').find_next('td').findChild('a')['href']
                            link_etp = self.url_.url_join(data_origin_url, link_etp_obj)
                            if pathlib.Path(''.join(original_name)).suffix in lst_exet:
                                self.dir.create_dir()
                                relative_path_f = self.dir.name_in_column_files(
                                    self.trading_id(url_)[:5], original_name)
                                name_on_server = self.dir.name_file_on_server(self.trading_id(url_)[:5],
                                                                              original_name, )
                                self.load.request_to_download(url=link_etp, referer=referer,
                                                              original_name=name_on_server)
                            lot.append({'original_name': original_name,
                                        'link': relative_path_f,
                                        'link_etp': self.url_.parse_url(url=link_etp)})
                    return lot
        except:
            logger.warning(f'{self.response.url}', exc_info=True)
            return list()

    # AUCTION
    def start_req_auc(self, *args):
        _div_start = self.response.xpath(self.loc.start_request_auction.format(self.get_table_id(args))).get()
        text_time = BS(_div_start, features='lxml').get_text().strip()
        try:
            return format_time(text_time)
        except Exception as e:
            print(e)
            return None

    def end_req_auc(self, *args):
        _div_end = self.response.xpath(self.loc.end_request_auction.format(self.get_table_id(args))).get()
        text_time = BS(_div_end, features='lxml').get_text().strip()
        try:
            return format_time(text_time)
        except Exception as e:
            print(e)
            return None

    def start_trading_auc(self, *args):
        _div_start = self.response.xpath(self.loc.start_trading_auction.format(self.get_table_id(args))).get()
        text_time = BS(_div_start, features='lxml').get_text().strip()
        try:
            return format_time(text_time)
        except Exception as e:
            print(e)
            return None

    def end_trading_auc(self, *args):
        _div_end = self.response.xpath(self.loc.end_date_trading_auc.format(self.get_table_id(args))).get()
        text_time = BS(_div_end, features='lxml').get_text().strip()
        try:
            return format_time(text_time)
        except Exception as e:
            print(e)
            return None

    def start_price_auc(self, *args):
        _div_end = self.response.xpath(self.loc.start_price_auc.format(self.get_table_id(args))).get()
        price = BS(_div_end, features='lxml').get_text().strip().replace('\xa0', '').replace(',', '.')
        price = re.search(r'\d+\.\d{1,2}', price)
        try:
            if price:
                return float(price.group())
        except (ValueError, TypeError) as e:
            print(e)
            return None

    def step_price_auc(self, *args):
        _div_step = self.response.xpath(self.loc.step_price_auc.format(self.get_table_id(args))).get()
        if _div_step:
            step = BS(_div_step, features='lxml').get_text().strip().replace('\xa0', '').replace(',', '.')
            step = ''.join(re.findall(r'^\d+%', step)).replace('%', '')
            start_price = self.start_price_auc(args)

            try:
                step = float(step)
                return round(start_price * step / 100, 2)
            except (ValueError, TypeError):
                return None

