import logging
import pathlib
import re

from bs4 import BeautifulSoup

from .auction import AuctionParse
from .offer import OfferParse
from .serp import SerpParse
from ..locators.locator_trade import LocatorTrade
from ..utils.check_inn_email_phone import CheckIfCorrectContactInfo
from ..utils.config import lst_exeption, lst_exet, lst_exet_archive, main_url
from ..utils.download import DownloadFiles
from ..utils.work_with_path_and_dir import GeneralFilesDir, LotFilesDir
from ..utils.work_with_text_and_number import dedent_func, contains
from ..utils.working_with_time import format_time
from ..utils.working_with_url import UrlConfig

logger = logging.getLogger(__name__)


class Combo:

    def __init__(self, response_):
        self.response = response_
        self.url = UrlConfig()
        self.serp = SerpParse(self.response)
        self.auc = AuctionParse(self.response)
        self.offer = OfferParse(self.response)
        self.check = CheckIfCorrectContactInfo()
        self.loc = LocatorTrade()
        self.general_dir = GeneralFilesDir()
        self.lot_dir = LotFilesDir()

    @property
    def trading_type(self):
        type_ = self.response.xpath(self.loc.trading_type_loc).get()
        type_ = BeautifulSoup(str(type_), features='lxml').get_text().strip()
        d = dict(
            offer=[
                'Открытые торги посредством публичного предложения',
                'Закрытые торги посредством публичного предложения',
                'Открытые торги (конкурс) посредством публичного предложения',
                'Открытые торги (конкурс) посредством публичного предложения'
            ],
            auction=[
                'Открытый аукцион с открытой формой представления предложений о цене',
                'Открытый аукцион с закрытой формой представления предложений о цене',
                'Закрытый аукцион с открытой формой представления предложений о цене',
                'Закрытый аукцион с закрытой формой представления предложений о цене'
            ],
            competition=[
                'ОКОФ',
                'ОКЗФ',
                'ЗКОФ',
                'ЗКЗФ'
            ]
        )
        for k, v in d.items():
            if type_ in v:
                return k
        return None

    @property
    def trading_form(self):
        type_ = self.response.xpath(self.loc.trading_type_loc).get()
        type_ = BeautifulSoup(str(type_), features='lxml').get_text().strip()
        d = dict(
            opened=[
                'Открытые торги посредством публичного предложения',
                'Открытые торги (конкурс) посредством публичного предложения',
                'Открытый аукцион с открытой формой представления предложений о цене',
                'Открытый аукцион с закрытой формой представления предложений о цене',
                'ОКОФ',
                'ОКЗФ'
            ],
            closed=[
                'Закрытые торги посредством публичного предложения',
                'Закрытые торги (конкурс) посредством публичного предложения',
                'Закрытый аукцион с открытой формой представления предложений о цене',
                'Закрытый аукцион с закрытой формой представления предложений о цене'
                'ЗКОФ',
                'ЗКЗФ'
            ]
        )
        for k, v in d.items():
            if type_ in v:
                return k
        return None

    @property
    def status(self):
        active = ('Торги в стадии приема заявок', 'Прием заявок',)
        pending = ('Объявленые торги', 'Объявленные торги')
        ended = ('Прием заявок завершен', 'Проведение аукциона', 'Торги завершены', 'Торги отменены',
                 'Торги приостановлены', 'Торги по лоту отменены', 'Торги по лоту приостановлены')
        status = self.response.xpath(self.loc.status_loc).get()
        status = BeautifulSoup(str(status), features='lxml').get_text().strip()
        try:
            if status in active:
                return 'active'
            elif status in pending:
                return 'pending'
            elif status in ended:
                return 'ended'
            else:
                return None
        except:
            return None

    @property
    def trading_id(self):
        _id = re.findall(r'\d+', str(self.trading_link))
        return ''.join(_id)

    @property
    def trading_link(self):
        return self.response.url

    @property
    def trading_number(self):
        h1 = self.response.xpath(self.loc.trading_number_loc).get()
        div = BeautifulSoup(str(h1), features='lxml').get_text()
        match = ''.join(re.findall(r'\d+\-\w+', str(div)))
        if len(match) < 0:
            logger.error(f'{self.response.url} :: INVALID DATA TRADING NUMBER')
        else:
            return match

    @property
    def trading_org(self):
        try:
            td_org = self.response.xpath(self.loc.trading_org_loc).get()
            td_org = dedent_func(BeautifulSoup(str(td_org), features='lxml').get_text()).strip()
            return ''.join(re.sub(r'\s+', ' ', td_org))
        except:
            logger.warning(
                f'{self.response.url} :: INVALID DATA ORGANIZER', exc_info=True)
            return None

    def get_phone_number(self):
        """get phone number of organizer"""
        try:
            phone = self.response.xpath(self.loc.phone_org_loc).get()
            phone = dedent_func(BeautifulSoup(str(phone), features='lxml').get_text()).replace(';', '').strip()
            return self.check.check_phone(phone)
        except:
            return None

    def get_email(self):
        """get email of organizer"""
        try:
            email = self.response.xpath(self.loc.email_org_loc).get()
            email = dedent_func(BeautifulSoup(str(email), features='lxml').get_text()).replace(';', '').strip()
            return self.check.check_email(email)
        except:
            return None

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

    @property
    def msg_number(self):
        msg = self.response.xpath(self.loc.msg_number_loc).get()
        if msg:
            msg = BeautifulSoup(str(msg), features='lxml').get_text()
            return ' '.join(re.findall(r'\d{6,8}', dedent_func(msg)))

    @property
    def case_number(self):
        case = BeautifulSoup(str(self.response.xpath(self.loc.case_number_loc).get()), 'lxml').get_text()
        return self.check.check_case_number(dedent_func(case))

    @property
    def debitor_inn(self):
        try:
            inn = self.response.xpath(self.loc.debitor_inn_loc).get() or self.response.xpath(
                self.loc.debitor_inn_loc_2).get()
            trade_inn = dedent_func(BeautifulSoup(inn, features='lxml').get_text())
            pattern = re.compile(r'\d{10,12}')
            if pattern:
                return ''.join(pattern.findall(trade_inn))
        except:
            return None

    @property
    def arbitr_manager(self):
        try:
            td_org = self.response.xpath(self.loc.arbitr_manag_loc).get()
            if td_org is None:
                td_org = self.response.xpath(self.loc.finance_manag_loc).get()
            td_org = dedent_func(BeautifulSoup(str(td_org), features='lxml').get_text()).strip()
            if td_org != 'None':
                return ''.join(re.sub(r'\s+', ' ', td_org))
        except:
            logger.warning(f'{self.response.url} :: INVALID DATA ARBITR NAME')

    @property
    def arbitr_inn(self):
        try:
            arbitr_inn = self.response.xpath(self.loc.arbitr_inn_loc).get()
            if arbitr_inn is None:
                arbitr_inn = self.response.xpath(self.loc.finance_inn_loc).get()
            arbitr_inn = dedent_func(BeautifulSoup(str(arbitr_inn), features='lxml').get_text())
            pattern = re.compile(r'\d{10,12}')
            if pattern:
                return ''.join(pattern.findall(arbitr_inn))
        except:
            return None

    @property
    def arbitr_manager_org(self):
        try:
            td_company = self.response.xpath(self.loc.arbitr_org_loc).get()
            if td_company is None:
                td_company = self.response.xpath(self.loc.finance_org_loc).get()
            td_company = dedent_func(BeautifulSoup(str(td_company), features='lxml').get_text())
            if td_company != 'None':
                if '(' in td_company:
                    td_company = ''.join(
                        [x if len(td_company) > 0 else None for x in re.split(r'\(', td_company, maxsplit=1)[0]])
                return ''.join(dedent_func(td_company))
        except:
            logger.warning(
                f'{self.response.url} :: INVALID DATA ARBITR COMPANY')

    @property
    def start_date_requests(self):
        date = self.response.xpath(self.loc.start_date_requests_loc).get()
        return format_time(BeautifulSoup(str(date), features='lxml').get_text())

    @property
    def end_date_requests(self):
        date = self.response.xpath(self.loc.end_date_requests_loc).get()
        return format_time(BeautifulSoup(str(date), features='lxml').get_text())

    def get_lots(self):
        return self.response.xpath(self.loc.lots_loc).getall()

    def download_general(self):
        dir = self.general_dir
        download = DownloadFiles()
        general_lst = list()
        lst_files = self.response.xpath(self.loc.general_files_loc).getall()
        for file in lst_files:
            link_ = BeautifulSoup(str(file), features='lxml').find('a')
            link = link_.get('href')
            name = link_.get_text()
            if not any(ele in name for ele in lst_exeption):
                if pathlib.Path(name).suffix in lst_exet:
                    dir.create_dir()
                    if len(name) > 75:
                        file_name_server = name[0][:30] + '_' + name[0][-35::1]
                    else:
                        file_name_server = name[0]
                    name_on_server = dir.name_file_on_server(self.trading_id, file_name_server)
                    _path_absolute = dir.return_absolute_path(name_on_server)
                    download.request_to_download_general(url=link,
                                                         referer=self.response.url,
                                                         _abs_path=_path_absolute)
                    _path_relative = dir.name_in_column_files(name_on_server, )
                    general_lst.append(
                        {'original_name': name, 'link': _path_relative,
                         'link_etp': self.url.parse_url(link)})
                    # FILES INSIDE ARCHIVE
                elif pathlib.Path(name).suffix in lst_exet_archive:
                    if len(name) > 75:
                        file_name_server = name[:30] + '_' + name[-35::1]
                    else:
                        file_name_server = name
                    name_on_server = dir.name_file_on_server(self.trading_id, file_name_server)
                    _path_absolute = dir.return_absolute_path(name_on_server)
                    self.general_dir.create_dir()
                    lst_files = download.request_to_download_general(url=link,
                                                                     referer=self.response.url,
                                                                     _abs_path=_path_absolute,
                                                                     _id=self.trading_id,
                                                                     _relative_path=dir.return_download_dir_etp())
                    general_lst.extend(lst_files)
                else:
                    general_lst.append(
                        {'original_name': name, 'link': '', 'link_etp': self.url.url_join(main_url, link)})
        return general_lst

    def download_lot(self, lot):
        dir = self.lot_dir
        download = DownloadFiles()
        lot_list = list()
        _path_relative = ''
        lot_files = BeautifulSoup(str(lot), 'lxml').find_all('a', attrs={'target': '_blank'})
        if not lot_files:
            return []
        for link in lot_files:
            name = link.get_text()
            link = link.get('href')
            if not any(ele in name for ele in lst_exeption):
                if pathlib.Path(name).suffix in lst_exet:
                    dir.create_dir()
                    if len(name) > 75:
                        file_name_server = name[:30] + '_' + name[-35::1]
                    else:
                        file_name_server = name
                    name_on_server = dir.name_file_lot_on_server(_id=self.trading_id,
                                                                 lot_num=self.lot_number(lot),
                                                                 original_name=file_name_server)
                    _path_absolute = dir.return_absolute_path(name_on_server)
                    download.request_to_download_general(url=link,
                                                         referer=self.response.url,
                                                         _abs_path=_path_absolute)
                    _path_relative = dir.name_in_column_files(name_on_server)
                    lot_list.append(
                        {'original_name': name, 'link': _path_relative,
                         'link_etp': self.url.parse_url(link)})
                # FILES INSIDE ARCHIVE
                elif pathlib.Path(name).suffix in lst_exet_archive:
                    lot_file = pathlib.Path(name).stem
                    if len(name) > 75:
                        file_name_server = name[:30] + '_' + name[-35::1]
                    else:
                        file_name_server = name
                    name_on_server = dir.name_file_lot_on_server(_id=self.trading_id,
                                                                 lot_num=self.lot_number(lot),
                                                                 original_name=file_name_server)
                    _path_absolute = dir.return_absolute_path(name_on_server)
                    dir.create_dir()
                    lst_files = download.request_to_download_general(url=link,
                                                                     referer=self.response.url,
                                                                     _abs_path=_path_absolute,
                                                                     _id=self.trading_id,
                                                                     _relative_path=dir.return_download_dir_etp())
                    lot_list.extend(lst_files)
                else:
                    lot_list.append({'original_name': name, 'link': '', 'link_etp': self.url.url_join(main_url, link)})
        return lot_list

    def lot_number(self, lot):
        title = BeautifulSoup(lot, 'lxml').find('th').get_text().strip()
        match = re.findall(r'\d+$', title)
        try:
            return ''.join(match)
        except:
            logger.warning(f'{self.response.url} :: LOT WITHOUT NUMBER')
            return None

    def short_name(self, lot):
        try:
            short_name = dedent_func(
                BeautifulSoup(lot, 'lxml').find('td', text=contains("Наименование лота")).find_next_sibling(
                    'td').get_text())
            if short_name != 'None':
                return short_name
        except:
            logger.warning(f'{self.response.url} :: LOT INVALID DATA - SHORT NAME')
            return None

    def lot_info(self, lot):
        try:
            lot_info = BeautifulSoup(str(lot), 'lxml').find('td', text=contains('Cведения об имуществе должника'))
            if not lot_info:
                return
            return dedent_func(lot_info.find_next_sibling('td').get_text())
        except:
            logger.warning(f'{self.response.url} :: LOT INVALID DATA - LOT INFO')

    def property_information(self, lot):
        try:
            property_info = dedent_func(BeautifulSoup(str(lot), 'lxml').find(
                'td', text=contains('Порядок ознакомления')).find_next_sibling('td').get_text())
            if property_info != 'None':
                return property_info
        except:
            logger.warning(
                f'{self.response.url} :: INVALID DATA - PROPERTY INFO')

    def start_price(self, lot):
        try:
            p = BeautifulSoup(str(lot), 'lxml').find('td', text=contains('Начальная цена')).find_next_sibling('td')
            if p:
                p = re.sub(r'\s', '', dedent_func(p.get_text().strip()).replace(',', '.'))
                p = ''.join([x for x in p if x.isdigit() or x == '.'])
                if len(p) > 0:
                    return round(float(p), 2)
        except Exception as e:
            logger.error(f'{self.response.url} :: INVALID DATA START PRICE\n{e}')
