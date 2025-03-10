import logging
import pathlib
import re

from bs4 import BeautifulSoup

from general_utils import UrlConfig, dedent_func, CheckIfCorrectContactInfo, format_time
from general_utils.config import lst_exeption, lst_exet, lst_exet_archive
from ..locators.locator_trade import LocatorTrade
from ..utils.config import main_url
from ..utils.download import DownloadFiles
from ..utils.work_with_path_and_dir import GeneralFilesDir, LotFilesDir
from ..utils.work_with_text_and_number import get_org_info

logger = logging.getLogger(__name__)


class Combo:

    def __init__(self, response):
        self.response = response
        self.loc = LocatorTrade()
        self.general_dir = GeneralFilesDir()
        self.lot_dir = LotFilesDir()

    def get_trading_link(self):
        return UrlConfig.url_join(main_url, self.response.xpath(self.loc.trading_link_loc).extract_first())

    def get_lots(self):
        return self.response.xpath(self.loc.lots_loc).getall()

    def download_general(self):
        dir = self.general_dir
        download = DownloadFiles()
        general_lst = list()
        lst_files = self.response.xpath(self.loc.files_loc).getall()
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
                    name_on_server = dir.name_file_on_server(self.id_, file_name_server)
                    _path_absolute = dir.return_absolute_path(name_on_server)
                    download.request_to_download_general(url=link,
                                                         referer=self.response.url,
                                                         _abs_path=_path_absolute)
                    _path_relative = dir.name_in_column_files(name_on_server, )
                    general_lst.append(
                        {'original_name': name, 'link': _path_relative,
                         'link_etp': UrlConfig.parse_url(link)})
                    # FILES INSIDE ARCHIVE
                elif pathlib.Path(name).suffix in lst_exet_archive:
                    if len(name) > 75:
                        file_name_server = name[:30] + '_' + name[-35::1]
                    else:
                        file_name_server = name
                    name_on_server = dir.name_file_on_server(self.id_, file_name_server)
                    _path_absolute = dir.return_absolute_path(name_on_server)
                    self.general_dir.create_dir()
                    lst_files = download.request_to_download_general(url=link,
                                                                     referer=self.response.url,
                                                                     _abs_path=_path_absolute,
                                                                     _id=self.id_,
                                                                     _relative_path=dir.return_download_dir_etp())
                    general_lst.extend(lst_files)
                else:
                    general_lst.append(
                        {'original_name': name, 'link': None, 'link_etp': UrlConfig.url_join(main_url, link)})
        return general_lst

    def download_lot(self):
        dir = self.lot_dir
        download = DownloadFiles()
        lot_list = list()
        _path_relative = ''
        lst_files = self.response.xpath(self.loc.files_loc).getall()
        for link in lst_files:
            name = link.get_text()
            link = link.get('href')
            if not any(ele in name for ele in lst_exeption):
                if pathlib.Path(name).suffix in lst_exet:
                    dir.create_dir()
                    if len(name) > 75:
                        file_name_server = name[:30] + '_' + name[-35::1]
                    else:
                        file_name_server = name
                    name_on_server = dir.name_file_lot_on_server(_id=self.id_,
                                                                 lot_num=self.lot_number,
                                                                 original_name=file_name_server)
                    _path_absolute = dir.return_absolute_path(name_on_server)
                    download.request_to_download_general(url=link,
                                                         referer=self.response.url,
                                                         _abs_path=_path_absolute)
                    _path_relative = dir.name_in_column_files(name_on_server)
                    lot_list.append(
                        {'original_name': name, 'link': _path_relative,
                         'link_etp': UrlConfig.parse_url(link)})
                # FILES INSIDE ARCHIVE
                elif pathlib.Path(name).suffix in lst_exet_archive:
                    if len(name) > 75:
                        file_name_server = name[:30] + '_' + name[-35::1]
                    else:
                        file_name_server = name
                    name_on_server = dir.name_file_lot_on_server(_id=self.id_,
                                                                 lot_num=self.lot_number,
                                                                 original_name=file_name_server)
                    _path_absolute = dir.return_absolute_path(name_on_server)
                    dir.create_dir()
                    lst_files = download.request_to_download_general(url=link,
                                                                     referer=self.response.url,
                                                                     _abs_path=_path_absolute,
                                                                     _id=self.id_,
                                                                     _relative_path=dir.return_download_dir_etp())
                    lot_list.extend(lst_files)
                else:
                    lot_list.append({'original_name': name, 'link': None, 'link_etp': UrlConfig.url_join(main_url, link)})
        return lot_list

    @property
    def id_(self):
        _id = re.findall(r'\d+', str(self.response.url))
        return ''.join(_id)

    @property
    def trading_type(self):
        type_ = self.response.xpath(self.loc.trading_type_loc).get()
        d = {
            'Аукцион': 'auction',
            'Конкурс': 'competition',
            'Предложение': 'offer'
        }
        return d[type_]

    @property
    def trading_form(self):
        text = self.response.xpath(self.loc.trading_form_loc).get()
        if 'Открытая' in text:
            return 'open'
        elif 'Закрытая' in text:
            return 'closed'
        else:
            return None

    @property
    def trading_org(self):
        try:
            td_org = dedent_func(self.response.xpath(self.loc.trading_org_sro_loc).get()).strip()
            if not td_org:
                td_org = dedent_func(self.response.xpath(self.loc.trading_org_fio_loc).get()).strip()
            return ''.join(re.sub(r'\s+', ' ', td_org))
        except:
            logger.warning(f'{self.response.url} :: INVALID DATA ORGANIZER', exc_info=True)
            return None

    @property
    def trading_org_inn(self):
        try:
            td_org_inn = self.response.xpath(self.loc.trading_org_inn_loc).get().split('/')[0].strip()
            if td_org_inn:
                return CheckIfCorrectContactInfo.check_inn(dedent_func(td_org_inn))
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
    def start_date_trading(self):
        date = self.response.xpath(self.loc.start_date_trading_loc).get()
        if date:
            return format_time(date)

    @property
    def end_date_trading(self):
        date = self.response.xpath(self.loc.end_date_trading_loc).get()
        if date:
            return format_time(date)

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
            if not address:
                address = dedent_func(self.response.xpath(self.loc.sud_loc).get())
            return address
        except Exception as e:
            return None

    @property
    def arbit_manager(self):
        try:
            arbit_name = self.response.xpath(self.loc.arbit_first_name_loc).get()
            arbit_surname = self.response.xpath(self.loc.arbit_last_name_loc).get()
            arbit_middle = self.response.xpath(self.loc.arbit_middle_name_loc).get()
            arbit_manager = get_org_info(arbit_surname, arbit_name, arbit_middle, self.response.url)
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
            return None

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
    def status(self):
        status = self.response.xpath(self.loc.status_loc).get().strip()
        if status == 'Открыт прием заявок':
            return 'active'
        elif status in ['Торги не состоялись', 'Завершенные', 'Торги отменены']:
            return 'ended'
        else:
            return None

    @property
    def lot_number(self):
        return self.response.xpath(self.loc.lot_number).get()

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
    def start_price(self):
        try:
            p = self.response.xpath(self.loc.start_price_loc).get()
            if p:
                p = re.sub(r'\s', '', dedent_func(p.strip()).replace(',', '.').rstrip('.'))
                p = ''.join([x for x in p if x.isdigit() or x == '.'])
                if len(p) > 0:
                    return round(float(p), 2)
        except Exception as e:
            logger.error(f'{self.response.url} :: INVALID DATA START PRICE\n{e}')

    @property
    def step_price(self):
        _div_step = self.response.xpath(self.loc.step_price_loc).get()
        if _div_step:
            step = re.sub(r'\s', '', dedent_func(_div_step.strip()).replace(',', '.').rstrip('.'))
            step = ''.join([x for x in step if x.isdigit() or x == '.'])
            try:
                step = float(step)
                return round(self.start_price * step / 100, 2)
            except (ValueError, TypeError):
                return None

    @property
    def periods(self):
        return None
