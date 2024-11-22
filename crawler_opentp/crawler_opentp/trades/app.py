import logging
import pathlib
import re

import pandas as pd
from bs4 import BeautifulSoup

from ..utils.check_inn_email_phone import CheckIfCorrectContactInfo
from ..utils.config import lst_exeption, lst_exet, lst_exet_archive, main_url, data_origin_url
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
        self.check = CheckIfCorrectContactInfo()
        self.general_dir = GeneralFilesDir()
        self.lot_dir = LotFilesDir()
        self.soup = BeautifulSoup(self.response.text, 'lxml')

    def get_trading_links(self):
        links = self.response.xpath('//div[@id="tenders-box-on-index"]//table//td[1]/a/@href').getall()
        if links:
            return [self.url.url_join(data_origin_url, link) for link in links]
        logger.warning(f'{self.response.url} :: NO TRADING LINKS')
        return []

    def get_next_page(self):
        pager_select = self.response.xpath('//span[@class="pager_select"]').get()
        try:
            next_link = BeautifulSoup(pager_select, 'lxml').find('a')
            if next_link:
                return self.url.url_join(data_origin_url, next_link.get('href'))
        except Exception as e:
            logger.error(f'{self.response.url} :: SOMETHING WENT WRONG WITH NEXT PAGE\n{e}', exc_info=True)

    def download_general(self):
        dir = self.general_dir
        download = DownloadFiles()
        general_lst = list()
        docs = self.get_trade_table().find('table', class_='docs-table')
        if not docs:
            return []
        for file in docs.find_all('tr')[1:]:
            link_ = file.find('a', target="_blank")
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

    def download_lot(self):
        dir = self.lot_dir
        download = DownloadFiles()
        lot_list = list()
        _path_relative = ''
        docs = self.get_lot_table().find('table', class_='docs-table')
        if not docs:
            return []
        for file in docs.find_all('tr')[1:]:
            link_ = file.find('a', target="_blank")
            link = link_.get('href')
            name = link_.get_text()
            if not any(ele in name for ele in lst_exeption):
                if pathlib.Path(name).suffix in lst_exet:
                    dir.create_dir()
                    if len(name) > 75:
                        file_name_server = name[:30] + '_' + name[-35::1]
                    else:
                        file_name_server = name
                    name_on_server = dir.name_file_lot_on_server(_id=self.trading_id,
                                                                 lot_num=self.lot_number,
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
                                                                 lot_num=self.lot_number,
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

    def get_trade_table(self):
        return self.soup.find('table', id='tender-info-table')

    def get_lot_table(self):
        return self.soup.find('table', id='lot-info-table')

    def get_lots(self):
        main_table = self.get_trade_table()
        try:
            lots = []
            lots_table = main_table.find('table', class_='lots-table')
            links = lots_table.find_all('a')
            pd_table = pd.read_html(str(lots_table))[0]
            for link, row in zip(links, list(pd_table.iterrows())[1:]):
                data = row[1]
                lot_number = data[0]
                short_name = dedent_func(data[1])
                status = self.get_status(data[2])
                start_price = self.get_start_price(data[4])
                lots.append(
                    [self.url.url_join(data_origin_url, link.get('href')), lot_number, short_name, status, start_price])
            return lots
        except Exception as e:
            logger.error(f'{self.response.url} :: SOMETHING WENT WRONG WITH LOTS\n{e}', exc_info=True)
            return []

    def get_status(self, status):
        d = dict(
            active=('идет прием заявок', 'идет приём заявок', 'прием заявок'),
            pending=(
            'торги объявлены', 'объявленные торги', 'ожидание подведения итогов', 'определение участников торгов'),
            ended=(
                'заявки рассмотрены', 'идёт аукцион', 'подведение итогов', 'приём заявок завершен',
                'рассмотрение заявок', 'торги аннулированы', 'торги не состоялись', 'торги отменены',
                'торги приостановлены', 'торги проведены', 'торги завершены', 'прием заявок завершен',
                'приостановленные торги'
            )
        )
        for k, v in d.items():
            if status.lower() in v:
                return k
        return None

    def get_start_price(self, price):
        try:
            p = re.sub(r'\s', '', dedent_func(price).replace(',', '.'))
            p = ''.join([x for x in p if x.isdigit() or x == '.'])
            if len(p) > 0:
                return round(float(p), 2)
        except Exception as e:
            logger.error(f'{self.response.url} :: INVALID DATA START PRICE\n{e}')

    @property
    def trading_id(self):
        _id = re.search(r'tender\/(\d+)\/', str(self.response.url)).group(1)
        return _id

    def get_main_info(self):
        table = self.get_trade_table()
        main_info = table.find('div', text=re.compile("Основная информация")).get_text()
        trading_number, trading_type_and_form = re.search(r'(\d+)-(\D+)$', main_info).groups()
        if trading_type_and_form[1] == 'А':
            trading_type = 'auction'
        else:
            trading_type = 'offer'
        return trading_number, trading_type

    @property
    def trading_form(self):
        d = {'Открытая': 'open', 'Закрытая': 'closed'}
        form = self.get_trade_table().find('b', text=re.compile('Форма представления предложений о цене'))
        if form:
            form = form.next_sibling.get_text()
            return d.get(form, None)
        return 'closed'

    def get_org(self):
        table = self.get_trade_table()
        return table.find('div', text="Информация об организаторе").find_next('tr')

    @property
    def trading_org(self):
        try:
            org = self.get_org().find('div', text=re.compile(r'Арбитражный управляющий'))
            if org:
                return dedent_func(re.search(r'Арбитражный управляющий \/ (.+)', org.get_text()).group(1))
            org = self.get_org().find('b', text=re.compile('Полное наименование')).next_sibling.get_text()
            return dedent_func(org)
        except Exception as e:
            logger.error(f'{self.response.url} :: SOMETHING WENT WRONG WITH ORGANIZER\n{e}', exc_info=True)

    @property
    def trading_org_inn(self):
        try:
            inn = self.get_org().find('b', text=re.compile('ИНН')).next_sibling.get_text()
            return self.check.check_inn(inn)
        except Exception as e:
            logger.error(f'{self.response.url} :: SOMETHING WENT WRONG WITH ORGANIZER INN\n{e}', exc_info=True)

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
        try:
            phone = self.get_org().find('b', text=re.compile('Телефон')).next_sibling.get_text()
            phone = dedent_func(phone)
            return self.check.check_phone(phone)
        except Exception as e:
            logger.error(f'{self.response.url} :: SOMETHING WENT WRONG WITH PHONE NUMBER\n{e}', exc_info=True)

    def get_email(self):
        try:
            email = self.get_org().find('b', text=re.compile('Адрес электронной почты')).next_sibling.get_text()
            email = dedent_func(email)
            return self.check.check_email(email)
        except Exception as e:
            logger.error(f'{self.response.url} :: SOMETHING WENT WRONG WITH EMAIL\n{e}', exc_info=True)

    @property
    def msg_number(self):
        return None

    def get_debtor(self):
        table = self.get_trade_table()
        return table.find('div', text=re.compile("Информация о продавце")).find_next('tr')

    @property
    def case_number(self):
        try:
            case_number = self.get_debtor().find('b', text=re.compile('Номер дела')).next_sibling.get_text()
            return dedent_func(case_number)
        except Exception as e:
            logger.error(f'{self.response.url} :: SOMETHING WENT WRONG WITH EMAIL\n{e}', exc_info=True)

    @property
    def debitor_inn(self):
        try:
            inn = self.get_debtor().find('b', text=re.compile('ИНН')).next_sibling.get_text()
            return self.check.check_inn(inn)
        except Exception as e:
            logger.error(f'{self.response.url} :: SOMETHING WENT WRONG WITH DEBITOR INN\n{e}', exc_info=True)

    @property
    def arbitr_manager(self):
        return self.trading_org

    @property
    def arbitr_manager_inn(self):
        return self.trading_org_inn

    @property
    def arbitr_manager_org(self):
        try:
            org = self.get_debtor().find('b', text=re.compile(
                'Наименование организации арбитражных управляющих')).next_sibling.get_text()
            return dedent_func(org)
        except Exception as e:
            logger.error(f'{self.response.url} :: SOMETHING WENT WRONG WITH ARBITR MANAGER ORG\n{e}', exc_info=True)

    @property
    def start_date_requests(self):
        try:
            date = self.get_trade_table().find('b', text=re.compile(
                'Дата и время начала представления заявок на участие')).next_sibling.get_text()
            return format_time(date)
        except Exception as e:
            logger.error(f'{self.response.url} :: SOMETHING WENT WRONG WITH START DATE REQUESTS\n{e}', exc_info=True)

    @property
    def end_date_requests(self):
        try:
            date = self.get_trade_table().find('b', text=re.compile(
                'Дата и время окончания представления заявок на участие')).next_sibling.get_text()
            return format_time(date)
        except Exception as e:
            logger.error(f'{self.response.url} :: SOMETHING WENT WRONG WITH END DATE REQUESTS\n{e}', exc_info=True)

    @property
    def property_information(self):
        try:
            return dedent_func(
                self.get_trade_table().find('b', text=re.compile('Порядок ознакомления с имуществом'))
                .next_sibling.get_text()
            )
        except Exception as e:
            logger.error(f'{self.response.url} :: SOMETHING WENT WRONG WITH PROPERTY INFORMATION\n{e}', exc_info=True)

    @property
    def lot_id(self):
        _id = re.search(r'tender\/\d+\/lot\/(\d+)', str(self.response.url)).group(1)
        return _id

    @property
    def lot_info(self):
        try:
            return dedent_func(
                self.get_lot_table().find('b', text=re.compile('Наименование лота')).next_sibling.get_text()
            )
        except Exception as e:
            logger.error(f'{self.response.url} :: SOMETHING WENT WRONG WITH LOT INFO\n{e}', exc_info=True)

    @property
    def step_price(self):
        try:
            p = self.get_lot_table().find('b', text=re.compile('Шаг аукциона, руб.'))
            if p:
                p = p.next_sibling.get_text()
                p = re.sub(r'\s', '', dedent_func(p.strip()).replace(',', '.'))
                p = ''.join([x for x in p if x.isdigit() or x == '.'])
                if len(p) > 0:
                    return round(float(p), 2)
        except ValueError as e:
            logger.error(f'{self.response.url} :: INVALID DATA STEP PRICE\n{e}')

    @property
    def start_date_trading(self):
        return self.start_date_requests

    @property
    def end_date_trading(self):
        try:
            date = self.get_trade_table().find('b', text=re.compile(
                'Дата и время подведения итогов торгов')).next_sibling.get_text()
            return format_time(date)
        except Exception as e:
            logger.error(f'{self.response.url} :: SOMETHING WENT WRONG WITH END DATE TRADING\n{e}', exc_info=True)
