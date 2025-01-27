import logging
import pathlib
import re

from bs4 import BeautifulSoup

from general_utils import DownloadFiles, FilesDir, UrlConfig, dedent_func, format_time
from general_utils.check_inn_email_phone import CheckIfCorrectContactInfo
from general_utils.models import RequestData
from ..config import data_origin, path_absolute, path_relative
from ..trades.auc import Auc
from ..trades.offer import Offer
from ..locators.locator_trade import LocatorTrade
from general_utils.location import get_region
from general_utils.config import lst_exeption, lst_exet, lst_exet_archive

logger = logging.getLogger(__name__)


class Combo:
    addresses = dict()

    def __init__(self, response):
        self.response = response
        self.loc = LocatorTrade()
        self.auc = Auc(response)
        self.offer = Offer(response)
        self.soup = BeautifulSoup(response.text, 'lxml')

    def get_lots(self):
        lots = self.response.xpath(self.loc.lots_loc).getall()
        lots_data = []
        for lot in lots:
            soup = BeautifulSoup(lot, 'lxml')
            lot_link = soup.find('a', target="_blank").get('href')
            status_and_number = soup.find_all("div", class_='light grey-text p5')[:2]
            lot_number = status_and_number[0].find('span').get_text().strip()
            status = status_and_number[1].find('span').get_text().strip().lower()
            status = self.get_status(status)
            lots_data.append((lot_link, lot_number, status))
        return lots_data

    def get_status(self, status):
        active = ('идёт приём заявок', 'идет прием заявок')
        pending = ('объявлены', 'объявлен', 'на утверждении')
        ended = ('приём заявок завершен', 'в стадии проведения', 'подводятся итоги',
                 'торги завершены', 'торги отменены', 'прием заявок завершен',
                 'идёт приём заявок (приостановлены)', 'торги приостановлены', 'торги по лоту отменены')
        if status in active:
            return 'active'
        elif status in pending:
            return 'pending'
        elif status in ended:
            return 'ended'

    def get_paths(self, data_origin_url: str):
        current_path_absolute = None
        current_path_relative = None
        for k, v in data_origin.items():
            if v == data_origin_url:
                current_path_absolute = path_absolute[k]
                current_path_relative = path_relative[k]
        return current_path_relative, current_path_absolute

    def download_general(self, data_origin_url: str):
        current_path_relative, current_path_absolute = self.get_paths(data_origin_url)
        files_dir = FilesDir(current_path_relative, current_path_absolute)
        load = DownloadFiles()
        lst_general = list()
        for file in self.response.xpath(self.loc.files_loc).getall():
            link_ = BeautifulSoup(str(file), features='lxml').find('a', target="_blank")
            link = link_.get('href')
            name = link_.get_text()
            if len(name) > 75:
                name = name[:30] + '_' + name[-35::1]
            name_on_server = files_dir.name_file_on_server(self.id_, name)
            absolute_path = files_dir.return_absolute_path(name_on_server)
            relative_path = files_dir.return_relative_path(name_on_server)
            if not any(ele in name for ele in lst_exeption):
                files_dir.create_dir()
                request_data = RequestData(url=link, referer=self.response.url)
                if pathlib.Path(name).suffix in lst_exet:
                    load.request_to_download_general(
                        request_data=request_data,
                        absolute_path=absolute_path, relative_path=relative_path,
                        trading_id=self.id_,
                    )
                    lst_general.append(
                        {
                            'original_name': name,
                            'link': relative_path.as_posix(),
                            'link_etp': UrlConfig.parse_url(link)
                        }
                    )
                elif pathlib.Path(name).suffix in lst_exet_archive:
                    archive_lst = load.request_to_download_general(
                        request_data=request_data,
                        absolute_path=absolute_path, relative_path=relative_path,
                        trading_id=self.id_
                    )
                    lst_general.extend(archive_lst)
                else:
                    lst_general.append(
                        {'original_name': name, 'link': '', 'link_etp': UrlConfig.url_join(data_origin_url, link)}
                    )
        return lst_general

    def download_lot(self, lot_number, data_origin_url):
        current_path_relative, current_path_absolute = self.get_paths(data_origin_url)
        files_dir = FilesDir(current_path_relative, current_path_absolute)
        load = DownloadFiles()
        lot_list = list()
        try:
            for link in self.response.xpath(self.loc.files_loc).getall():
                link = BeautifulSoup(str(link), features='lxml').find('a', target="_blank")
                name = link.get_text()
                link = link.get('href')
                if len(name) > 75:
                    name = name[:30] + '_' + name[-35::1]
                name_on_server = files_dir.name_file_lot_on_server(self.id_, lot_number, name)
                absolute_path = files_dir.return_absolute_path(name_on_server)
                relative_path = files_dir.return_relative_path(name_on_server)
                if not any(ele in name for ele in lst_exeption):
                    files_dir.create_dir()
                    request_data = RequestData(url=link, referer=self.response.url)
                    if pathlib.Path(name).suffix in lst_exet:
                        load.request_to_download_general(
                            request_data=request_data,
                            absolute_path=absolute_path, relative_path=relative_path,
                            trading_id=self.id_, lot_number=lot_number
                        )
                        lot_list.append(
                            {
                                'original_name': name,
                                'link': relative_path.as_posix(),
                                'link_etp': UrlConfig.parse_url(link)
                            }
                        )
                    elif pathlib.Path(name).suffix in lst_exet_archive:
                        archive_lst = load.request_to_download_general(
                            request_data=request_data,
                            absolute_path=absolute_path, relative_path=relative_path,
                            trading_id=self.id_, lot_number=lot_number
                        )
                        lot_list.extend(archive_lst)
                    else:
                        lot_list.append(
                            {'original_name': name, 'link': '', 'link_etp': UrlConfig.url_join(data_origin_url, link)}
                        )
            return lot_list
        except Exception as e:
            return []

    @property
    def id_(self):
        _id = re.findall(r'\d+$', str(self.response.url))
        return ''.join(_id)

    @property
    def trading_type_and_form(self):
        type_and_form = self.response.xpath(self.loc.trading_type_and_form_loc).get().strip()
        offer = ['ОТПП', 'ЗТПП']
        auction = ['ОАОФ', 'ОАЗФ', 'ЗАОФ', 'ЗАОЗ']
        competition = ['ОКОФ', 'ОКЗФ', 'ЗКОФ', 'ЗКОЗ']
        open_form = ['ОТПП', 'ОАОФ', 'ОАЗФ', 'ОКОФ', 'ОКЗФ']
        close_form = ['ЗТПП', 'ЗАОФ', 'ЗАОЗ', 'ЗКОФ', 'ЗКОЗ']
        trading_type = re.findall(r'\d+–[А-ЯA-Z]+', type_and_form)
        if len(trading_type) == 1:
            trading_type = re.findall(r'[А-ЯA-Z]+', trading_type[0].replace('-', '').strip())
            trading_type = trading_type[0].strip()
            if trading_type in offer and trading_type in open_form:
                return 'offer', 'open'
            if trading_type in offer and trading_type in close_form:
                return 'offer', 'closed'
            if trading_type in auction and trading_type in open_form:
                return 'auction', 'open'
            if trading_type in auction and trading_type in close_form:
                return 'auction', 'closed'
            if trading_type in competition and trading_type in open_form:
                return 'competition', 'open'
            if trading_type in competition and trading_type in close_form:
                return 'competition', 'closed'
        logger.error(f'{self.response.url} :: ERROR function {self.trading_type_and_form.__name__}')
        return None

    @property
    def trading_org(self):
        try:
            td_org = dedent_func(self.response.xpath(self.loc.trading_org_loc).get()).strip()
            return ''.join(re.sub(r'\s+', ' ', td_org))
        except:
            logger.warning(f'{self.response.url} :: INVALID DATA ORGANIZER', exc_info=True)
            return None

    @property
    def trading_org_inn(self):
        try:
            td_org_inn = self.response.xpath(self.loc.trading_org_inn_loc).get()
            if td_org_inn:
                return CheckIfCorrectContactInfo.check_inn(dedent_func(td_org_inn.strip()))
        except:
            logger.warning(f'{self.response.url} :: INVALID DATA ORGANIZER INN', exc_info=True)

    @property
    def trading_org_contacts(self):
        if self.get_phone_number():
            phone = self.get_phone_number()
        else:
            phone = None
        if self.get_email():
            email = self.get_email()
        else:
            email = None
        return {'email': email, 'phone': phone}

    def get_phone_number(self):
        """get phone number of organizer"""
        try:
            phone = dedent_func(self.response.xpath(self.loc.phone_org_loc).get()).replace(';', '').strip()
            return CheckIfCorrectContactInfo.check_phone(phone)
        except:
            return None

    def get_email(self):
        """get email of organizer"""
        try:
            email = dedent_func(self.response.xpath(self.loc.email_org_loc).get()).replace(';', '').strip()
            return CheckIfCorrectContactInfo.check_email(email)
        except:
            return None

    @property
    def msg_number(self):
        msg = self.response.xpath(self.loc.msg_number_loc).get()
        if msg:
            return ' '.join(re.findall(r'\d{6,8}', dedent_func(msg)))

    @property
    def case_number(self):
        return CheckIfCorrectContactInfo.check_case_number(
            dedent_func(self.response.xpath(self.loc.case_number_loc).get()))

    @property
    def debtor_inn(self):
        try:
            inn = self.response.xpath(self.loc.debitor_inn_loc).get()
            if not inn:
                return
            trade_inn = dedent_func(inn)
            pattern = re.compile(r'\d{10,12}')
            if pattern:
                return ''.join(pattern.findall(trade_inn))
        except:
            return None

    @property
    def address(self):
        try:
            address = dedent_func(self.response.xpath(self.loc.region_loc).get())
            if address not in self.addresses:
                self.addresses[address] = get_region(address)
            return address, self.addresses[address]
        except:
            pass

    @property
    def arbit_manager(self):
        try:
            arbit_manager = self.response.xpath(self.loc.arbit_manager_loc).get()
            if arbit_manager is None:
                return
            arbit_manager = dedent_func(arbit_manager).strip()
            return ''.join(re.sub(r'\s+', ' ', arbit_manager))
        except:
            logger.warning(f'{self.response.url} :: INVALID DATA ARBITR NAME')

    @property
    def arbit_manager_inn(self):
        try:
            arbitr_inn = dedent_func(self.response.xpath(self.loc.arbit_manager_inn_loc).get())
            pattern = re.compile(r'\d{10,12}')
            if pattern:
                return ''.join(pattern.findall(arbitr_inn))
        except:
            pass

    @property
    def arbit_manager_org(self):
        try:
            td_company = dedent_func(self.response.xpath(self.loc.arbit_manager_org_loc).get())
            if td_company != 'None':
                if '(' in td_company:
                    td_company = ''.join(
                        [x if len(td_company) > 0 else None for x in re.split(r'\(', td_company, maxsplit=1)[0]])
                return ''.join(dedent_func(td_company))
        except:
            logger.warning(f'{self.response.url} :: INVALID DATA ARBITR COMPANY')

    @property
    def short_name(self):
        try:
            short_name = dedent_func(self.response.xpath(self.loc.short_name_loc).get())
            if short_name != 'None':
                return short_name
        except:
            logger.warning(f'{self.response.url} :: LOT INVALID DATA - SHORT NAME')
            return None

    @property
    def lot_info(self):
        try:
            return dedent_func(self.response.xpath(self.loc.lot_info_loc).get())
        except:
            logger.warning(f'{self.response.url} :: LOT INVALID DATA - LOT INFO')

    @property
    def property_information(self):
        try:
            property_info = dedent_func(self.response.xpath(self.loc.property_information_loc).get())
            if property_info != 'None':
                return property_info
        except:
            logger.warning(f'{self.response.url} :: INVALID DATA - PROPERTY INFO')

    @property
    def start_date_requests(self):
        date = self.response.xpath(self.loc.start_date_requests_loc).get()
        if date:
            return format_time(date)

    @property
    def end_date_requests(self):
        date = self.response.xpath(self.loc.end_date_requests_loc).get()
        if date:
            return format_time(date)

    @property
    def start_price(self):
        prices = self.response.xpath(self.loc.start_price_auc_loc).getall()
        for p in prices:
            try:
                if p:
                    p = re.sub(r'\s', '', dedent_func(p.strip()).replace(',', '.').rstrip('.'))
                    p = ''.join([x for x in p if x.isdigit() or x == '.'])
                    if len(p) > 0:
                        return round(float(p), 2)
            except Exception as e:
                logger.warning(f'{self.response.url} :: INVALID DATA START PRICE\n{e}')

    @property
    def step_price(self):
        """return start price"""
        try:
            p = self.response.xpath(self.loc.step_price_auc_loc).get()
            if p:
                p = re.sub(r'\s', '', dedent_func(p.strip()).replace(',', '.').rstrip('.'))
                p = ''.join([x for x in p if x.isdigit() or x == '.'])
                if len(p) > 0:
                    return round(float(p), 2)
        except ValueError as e:
            logger.error(f'{self.response.url} :: INVALID DATA STEP PRICE\n{e}')
