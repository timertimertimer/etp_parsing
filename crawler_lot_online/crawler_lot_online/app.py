import logging
import pathlib
import re

from bs4 import BeautifulSoup

from .utils.download import DownloadFiles
from .utils.work_with_path_and_dir import GeneralFilesDir, LotFilesDir
from .utils.working_with_time import format_time
from .utils.working_with_url import UrlConfig
from .utils.config import lst_exeption, lst_exet, lst_exet_archive
from .utils.work_with_text_and_number import dedent_func, contains
from .utils.check_inn_email_phone import CheckIfCorrectContactInfo

logger = logging.getLogger(__name__)


class Combo:
    def __init__(self, response, spider):
        self.response = response
        self.check = CheckIfCorrectContactInfo()
        self.url = UrlConfig()
        self.lot_dir = LotFilesDir(spider)
        self.soup = BeautifulSoup(response.text, 'lxml')

    def download_general(self):
        return []

    def download_lot(self, trading_id, lot_number, data_origin):
        dir = self.lot_dir
        download = DownloadFiles()
        lot_list = list()
        _path_relative = ''
        lst_files = self.soup.find('div', id='lot_documents').find_all('a')
        for link in lst_files:
            name = link.get_text().strip()
            link = link.get('href')
            if not any(ele in name for ele in lst_exeption):
                if pathlib.Path(name).suffix in lst_exet:
                    dir.create_dir()
                    if len(name) > 75:
                        file_name_server = name[:30] + '_' + name[-35::1]
                    else:
                        file_name_server = name
                    name_on_server = dir.name_file_lot_on_server(_id=trading_id,
                                                                 lot_num=lot_number,
                                                                 original_name=file_name_server)
                    _path_absolute = dir.return_absolute_path(name_on_server)
                    download.request_to_download_general(url=self.url.url_join(data_origin, link),
                                                         referer=self.response.url,
                                                         _abs_path=_path_absolute)
                    _path_relative = dir.name_in_column_files(name_on_server)
                    lot_list.append(
                        {'original_name': name, 'link': _path_relative,
                         'link_etp': self.url.url_join(data_origin, link)}
                    )
                # FILES INSIDE ARCHIVE
                elif pathlib.Path(name).suffix in lst_exet_archive:
                    if len(name) > 75:
                        file_name_server = name[:30] + '_' + name[-35::1]
                    else:
                        file_name_server = name
                    name_on_server = dir.name_file_lot_on_server(_id=trading_id,
                                                                 lot_num=lot_number,
                                                                 original_name=file_name_server)
                    _path_absolute = dir.return_absolute_path(name_on_server)
                    dir.create_dir()
                    lst_files = download.request_to_download_general(url=self.url.url_join(data_origin, link),
                                                                     referer=self.response.url,
                                                                     _abs_path=_path_absolute,
                                                                     _id=trading_id,
                                                                     _relative_path=dir.return_download_dir_etp())
                    lot_list.extend(lst_files)
                else:
                    lot_list.append({'original_name': name, 'link': '', 'link_etp': self.url.url_join(data_origin, link)})
        return lot_list

    @property
    def trading_type(self):
        type_ = self.soup.find('strong', text=contains('Вид процедуры:'))
        if type_:
            type_ = type_.find_next('span').text.strip().lower()
            if any([
                    'аукцион' in type_,
                    'сессия' in type_,
            ]):
                return 'auction'
            elif 'конкурс' in type_:
                return 'competition'
            elif 'предложени' in type_:
                return 'offer'
            else:
                pass

    @property
    def trading_org(self):
        org = self.soup.find('strong', text=contains('Организатор'))
        if org:
            org = org.find_next('span').text.strip()
            return dedent_func(org)

    @property
    def status(self):
        status = self.soup.find('p', id='lot-status')
        if status:
            status = status.text.strip()
            if status in (
                    'подача заявок', 'опубликована', 'опубликован проект', 'размещена в еис', 'подача предложений'
            ):
                return 'active'
            elif status in ('рассмотрение заявок', 'ожидает рассмотрения заявок', 'ожидает начала подачи предложений'):
                return 'pending'
            elif status in ('завершена', 'рассмотрение предложений/подведение итогов', 'отменена'):
                return 'ended'
            else:
                pass

    @property
    def category(self):
        category = self.soup.find('strong', text=contains('Категория'))
        if category:
            category = category.find_next('span').text.strip()
            return dedent_func(category)

    @property
    def index(self):
        ...

    @property
    def address(self):
        country = self.soup.find('strong', text=contains('Страна'))
        if country:
            country = country.find_next('span').text.strip()
        address = self.soup.find('strong', text=contains('Адрес'))
        if address:
            address = address.find_next('span').text.strip()
        return dedent_func(f'{country}, {address}')

    @property
    def detailed_address(self):
        ...

    @property
    def encumbrance(self):
        ...

    @property
    def description_encumbrance(self):
        ...

    @property
    def lot_info(self):
        info = self.soup.find('strong', text=contains('Описание лота'))
        if info:
            info = info.find_next('span').text.strip()
            return dedent_func(info)

    @property
    def property_information(self):
        ...

    @property
    def start_date_requests(self):
        return self.get_dates_from_interval('Прием заявок')[0]

    @property
    def end_date_requests(self):
        return self.get_dates_from_interval('Прием заявок')[1]

    @property
    def start_date_trading(self):
        return self.get_dates_from_interval('Подача предложений')[0]

    @property
    def end_date_trading(self):
        return self.get_dates_from_interval('Подача предложений')[1]

    def get_dates_from_interval(self, label):
        date_requests = self.soup.find('strong', text=contains('Прием заявок'))
        if date_requests:
            date_requests = date_requests.find_next('span').text.strip()
            start, end = date_requests.split(' - ')
            return format_time(start), format_time(end)

    @property
    def start_price(self):
        try:
            p = self.get_acitvity_table().find('span', id='priceStart')
            if p:
                p = re.sub(r'\s', '', dedent_func(p.get_text().strip()).replace(',', '.'))
                p = ''.join([x for x in p if x.isdigit() or x == '.'])
                if len(p) > 0:
                    return round(float(p), 2)
        except ValueError as e:
            logger.error(f'{self.response.url} :: INVALID START PRICE\n{e}')

    @property
    def step_price(self):
        try:
            p = self.get_acitvity_table().find('td', id='priceStepUp')
            if p:
                p = re.sub(r'\s', '', dedent_func(p.get_text().strip()).replace(',', '.'))
                p = ''.join([x for x in p if x.isdigit() or x == '.'])
                if len(p) > 0:
                    return round(float(p), 2)
        except ValueError as e:
            logger.error(f'{self.response.url} :: INVALID STEP PRICE\n{e}')

    @property
    def min_price(self):
        try:
            p = self.get_acitvity_table().find('span', id='priceMin')
            if p:
                p = re.sub(r'\s', '', dedent_func(p.get_text().strip()).replace(',', '.'))
                p = ''.join([x for x in p if x.isdigit() or x == '.'])
                if len(p) > 0:
                    return round(float(p), 2)
        except ValueError as e:
            logger.error(f'{self.response.url} :: INVALID START PRICE\n{e}')

    def get_acitvity_table(self):
        return self.soup.find('table', class_='tbl-activity')

    @property
    def deposit(self):
        try:
            p = self.soup.find('strong', text=contains('Сумма задатка'))
            if p:
                p = p.find_next('span').text.strip()
                p = re.sub(r'\s', '', dedent_func(p).replace(',', '.'))
                p = ''.join([x for x in p if x.isdigit() or x == '.'])
                if len(p) > 0:
                    return round(float(p), 2)
        except ValueError as e:
            logger.error(f'{self.response.url} :: INVALID DEPOSIT PRICE\n{e}')

    @property
    def periods(self):
        ...

    @property
    def quantity(self):
        ...

    @property
    def unit(self):
        ...
