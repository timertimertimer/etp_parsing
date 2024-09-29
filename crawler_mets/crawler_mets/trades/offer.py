# -*- coding: utf-8 -*-
import pathlib
import time
import json
import pandas as pd
from bs4 import BeautifulSoup as BS
from icecream import ic
from random import randint
from ..locators.locator_trades import LocatorOffer
from ..utils.check_inn_email_phone import CheckIfCorrectContactInfo
from ..utils.config import data_origin_url, pattern_without_hash, lst_exet
from ..utils.download import DownloadFiles
from ..utils.work_with_path_and_dir import GeneralFilesDir, LotFilesDir
from ..utils.work_with_text_and_number import dedent_func, make_float, normalize_string
from ..utils.working_with_time import *
from ..utils.working_with_url import UrlConfig

logger = logging.getLogger(__name__)


class OfferParse():
    def __init__(self, response_):
        self.response = response_
        self.loc = LocatorOffer
        self.check = CheckIfCorrectContactInfo()
        self.url = UrlConfig()
        self.dir_gener = GeneralFilesDir()
        self.dir_lot = LotFilesDir()

    @property
    def data_origin(self):
        """return main url"""
        return data_origin_url

    @property
    def trading_id(self):
        """return numbers of the end of the url"""
        _id = re.findall(r'\d+', str(self.trading_link))
        return ''.join(_id)

    @property
    def trading_link(self):
        """return trading link without hash tag"""
        clean_url = re.findall(pattern_without_hash, self.response.url)
        return ''.join(clean_url)

    @property
    def trading_number(self):
        """return trading number"""
        h_3 = self.response.xpath(self.loc.trading_number_loc).get()
        h_3 = BS(str(h_3), features='lxml').get_text()
        match = ''.join(re.findall(r'\d+\-\w+', str(h_3)))
        if len(match) < 0:
            logger.error(f'{self.response.url} :: INVALID DATA TRADING NUMBER')
        else:
            return match

    @property
    def trading_org(self):
        """return name or company name of trading organizer"""
        try:
            td_org = self.response.xpath(self.loc.trading_organ_loc).get()
            td_org = dedent_func(
                BS(str(td_org), features='lxml').get_text()).strip()
            return ''.join(re.sub(r'\s+', ' ', td_org))
        except:
            logger.warning(
                f'{self.response.url} :: INVALID DATA ORGANIZER', exc_info=True)
            return None

    def get_phone_number(self):
        """get phone number of organizer"""
        try:
            phone = self.response.xpath(self.loc.phone_organ_loc).get()
            phone = dedent_func(
                BS(str(phone), features='lxml').get_text()).replace(';', '').strip()
            return self.check.check_phone(phone)
        except:
            return None

    def get_email(self):
        """get email of organizer"""
        try:
            email = self.response.xpath(self.loc.email_organ_loc).get()
            email = dedent_func(
                BS(str(email), features='lxml').get_text()).replace(';', '').strip()
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
    def msg_number(self):
        """return message number FED"""
        td_msg = self.response.xpath(self.loc.msg_number_loc).get()
        try:
            if td_msg:
                td_msg = ''.join(BS(str(td_msg), features='lxml').get_text()).replace(',', ' ').replace('№',
                                                                                                        '').replace(';',
                                                                                                                    '').replace(
                    ':', '').strip()
                match = ''.join(re.findall(
                    r'\d{1,2}\.\d{1,2}\.\d{2,4}', td_msg))
                if match:
                    return ''.join(td_msg).replace(match, '').replace('от', '').replace('-', '').replace('и',
                                                                                                         '').strip()
                else:
                    msg = dedent_func(re.sub(r'\s+', ' ', td_msg))
                    msg = ' '.join(re.findall(r'(\d{7})', msg))
                    msg = ' '.join(
                        [n if int(n) or n == ' ' else '' for n in (re.split(r'\s', msg))])
                    return msg
            else:
                return None
        except:
            logger.warning(f'{self.response.url}:: INVALID DATA MSG_NUMBER')
            return None

    @property
    def case_number(self):
        """get and clean case number"""
        case_ = self.response.xpath(self.loc.case_number_loc).get()
        try:
            case_ = ''.join(BS(str(case_), features='lxml').get_text()).replace('№', '').replace('\\', '/').replace(' ',
                                                                                                                    '').strip()
            if len(case_) < 42:
                return dedent_func(case_)
        except:
            logger.warning(f'{self.response.url}:: INVALID CASE_NUMBER')
            return None

    @property
    def debitor_inn(self):
        """get debitor personal inn"""
        try:
            trade_inn = dedent_func(BS(self.response.xpath(
                self.loc.debitor_inn_loc).get(), features='lxml').get_text())
            pattern = re.compile(r'\d{10,12}')
            if pattern:
                return ''.join(pattern.findall(trade_inn))
        except:
            return None

    @property
    def arbitr_manager_org(self):
        """return name or company name of trading organizer"""
        try:
            td_org = self.response.xpath(self.loc.arbitr_manag_loc).get()
            if td_org is None:
                td_org = self.response.xpath(self.loc.finance_manag_loc).get()
            td_org = dedent_func(
                BS(str(td_org), features='lxml').get_text()).strip()
            if td_org != 'None':
                return ''.join(re.sub(r'\s+', ' ', td_org))
        except:
            logger.warning(f'{self.response.url} :: INVALID DATA ARBITR NAME')

    @property
    def arbitr_inn(self):
        """get debitor personal inn"""
        try:
            arbitr_inn = self.response.xpath(
                self.loc.arbitr_inn_loc).get()
            if arbitr_inn is None:
                arbitr_inn = self.response.xpath(
                    self.loc.finance_inn_loc).get()
            arbitr_inn = dedent_func(BS(str(arbitr_inn), features='lxml').get_text())
            pattern = re.compile(r'\d{10,12}')
            if pattern:
                return ''.join(pattern.findall(arbitr_inn))
        except:
            return None

    @property
    def arbitr_org(self):
        """get arbitr company name"""
        try:
            td_company = self.response.xpath(
                self.loc.arbitr_org_loc).get()
            if td_company is None:
                td_company = self.response.xpath(
                    self.loc.finance_org_loc).get()
            td_company = dedent_func(BS(str(td_company), features='lxml').get_text())
            if td_company != 'None':
                if '(' in td_company:
                    td_company = ''.join(
                        [x if len(td_company) > 0 else None for x in re.split(r'\(', td_company, maxsplit=1)[0]])
                return ''.join(dedent_func(td_company))

        except:
            logger.warning(
                f'{self.response.url} :: INVALID DATA ARBITR COMPANY')

    # count lots
    @property
    def count_lots(self):
        """return list with lot table"""
        return self.response.xpath(self.loc.count_lots_loc).getall()

    def get_lot_title(self, table):
        table = BS(str(table), features='lxml')
        title = table.find('th').get_text()
        return dedent_func(title)

    def status(self, lot_num: str):
        """get lot_number; return status(text representation) of lot"""
        td_stat = self.response.xpath(
            self.loc.status_loc.format(lot_num)).get()
        try:
            td_stat = dedent_func(BS(str(td_stat), features='lxml').get_text())
            return td_stat
        except:
            logger.error(
                f'{self.response.url} :: LOT {lot_num} INVALID DATA - STATUS')

    def lot_number(self, th_lot):
        """return number of lot extract from title"""
        title = th_lot
        match = re.findall(r'\d+$', title)
        try:
            return ''.join(match)
        except:
            logger.warning(
                f'{self.response.url} :: LOT WITHOUT NUMBER - LOT {th_lot}')
            return None

    def short_name(self, lot_num: str):
        """ :arg lot_number
            :return short name of lot
        """
        td_short_name = self.response.xpath(
            self.loc.short_name_loc.format(lot_num)).get()
        try:
            td_short_name = dedent_func(
                BS(str(td_short_name), features='lxml').get_text())
            if td_short_name != 'None':
                return td_short_name
        except:
            logger.warning(
                f'{self.response.url} :: LOT {lot_num} INVALID DATA - SHORT NAME - LOT {lot_num}')
            return None

    def lot_info(self, lot_num: str):
        """:arg lot_number
           :return lot info
        """
        td_lot_info = self.response.xpath(
            self.loc.lot_info_loc.format(lot_num)).get()
        try:
            td_lot_info = dedent_func(
                BS(str(td_lot_info), features='lxml').get_text())
            if td_lot_info != 'None':
                return td_lot_info
        except:
            logger.warning(
                f'{self.response.url} :: LOT {lot_num} INVALID DATA - LOT INFO - LOT {lot_num}')
            return None

    def property_info(self, lot_num: str):
        """:arg lot_number
           :return property_information
        """
        td_property_info = self.response.xpath(
            self.loc.property_info_loc.format(lot_num)).get()
        try:
            td_property_info = dedent_func(
                BS(str(td_property_info), features='lxml').get_text())
            if td_property_info != 'None':
                return td_property_info
        except:
            logger.warning(
                f'{self.response.url} :: LOT {lot_num} INVALID DATA - PROPERTY INFO - LOT {lot_num}')
            return None

    def start_price(self, lot_num: str):
        """:arg lot_number
           :return start price
            """
        td_start_price = self.response.xpath(
            self.loc.start_price_loc.format(lot_num)).get()
        try:
            td_start_price = dedent_func(
                BS(str(td_start_price), features='lxml').get_text())
            td_start_price = normalize_string(td_start_price)
            pattern = r'^\d+\.\d{1,2}'
            clean_price = ''.join(
                filter(lambda x: x.isdigit() or x == ',', td_start_price)).replace(',', '.')
            match = ''.join(re.findall(pattern, clean_price))
            if match:
                return round(float(match), 2)
            else:
                logger.error(
                    f'{self.response.url} :: INVALID DATA START PRICE - LOT {lot_num}')
                return None
        except:
            logger.error(
                f'{self.response.url} :: LOT {lot_num} INVALID DATA - START PRICE - LOT {lot_num}')
            return None

    def period_table(self, lot_num: str):
        """return table(pandas table) with all periods and prices"""
        try:
            table = self.response.xpath(
                self.loc.period_table_loc.format(lot_num)).getall()
            soup = BS(str(table[0]), features='lxml')
            class_shortdate = soup.find_all('span', class_='shortdate')
            if len(class_shortdate) > 0:
                for span in class_shortdate:
                    span.decompose()
            table = pd.read_html(str(soup).replace(',', '.'), header=None)[0]
            return table
        except:
            logger.error(
                f'{self.response.url} :: INVALID DATA PERIOD TABLE - LOT {lot_num}', exc_info=True)

    def get_period(self, lot_num):
        """return dictionary(json object)"""
        periods = list()
        table = self.period_table(lot_num)
        for p in range(len(table)):
            try:
                start = table.iloc[p][1]
                end = table.iloc[p][2]
                price = table.iloc[p][3]
                if isinstance(price, str):
                    price = normalize_string(price)
                    price = round(float(price.replace(' ', '')), 2)
                period = {
                    'start_date_requests': format_time(start),
                    'end_date_requests': format_time(end),
                    'end_date_trading': format_time(end),
                    'current_price': price
                }
                periods.append(period)
            except:
                logger.error(f'{self.response.url}', exc_info=True)
                ic(table)
                continue
        return periods

    def start_date_request(self, lot_num):
        """using period table return start date request according lot number"""
        try:
            table = self.period_table(lot_num)
            return format_time(table.iloc[0][1])
        except:
            logger.error(
                f'{self.response.url} :: INVALID DATA START DATE REQUEST LOT {lot_num}')

    def end_date_request(self, lot_num):
        """using period table return start date request according lot number"""
        try:
            table = self.period_table(lot_num)
            return format_time(table.iloc[-1][2])
        except:
            logger.error(
                f'{self.response.url} :: INVALID DATA END DATE REQUEST LOT {lot_num}')
            return None

    def download_general_files(self, trade_id):
        dir = self.dir_lot
        load = DownloadFiles()
        general = list()
        lst_files = self.response.xpath(self.loc.general_files_loc).getall()
        extra_name = None
        for file in lst_files:
            link = BS(str(file), features='lxml').find('a').get('href')
            name = BS(str(file), features='lxml').find('a').get_text()
            parse_link = self.url.parse_url(self.url.url_join(data_origin_url, link))
            if (len(name) < 3) or (len(name) == 0) or (name is None) or (
                    name == 'None') or '%20' in name or '%25' in name:
                try:
                    _div = BS(str(file), features='lxml').find('a').find('div')
                    url_text = ''.join(re.findall(r'url.\W(download/\d+.+)\?', str(_div))
                                       ).replace('(', '').replace(')', '').replace(' ', '_')
                    name = dedent_func(pathlib.Path(str(url_text)).name)
                except Exception as e:
                    logger.warning(f'{e}')
                    extra_name = ''.join(dedent_func(pathlib.Path(str(link)).name))[0:6]
                    name = extra_name + dedent_func(pathlib.Path(str(link)).suffix)
            else:
                name = re.sub(r'. $', '_.', name)
            if name is not None and 'Протокол' not in name and 'Решение' not in name:
                relative_path_f = ''
                _suffix_name = None
                _suffix_link = None
                if pathlib.Path(name.replace(' ', '')).suffix in lst_exet:
                    _suffix_name = 1
                if pathlib.Path(str(parse_link).replace(' ', '')).suffix in lst_exet:
                    _suffix_link = 2
                if _suffix_name == 1 or _suffix_link == 2:
                    if len(name) > 52:
                        name = name[-1:-21:-1]
                    if _suffix_name != 1 and _suffix_link == 2:
                        name = name + dedent_func(pathlib.Path(str(link)).suffix)
                    dir.create_dir()
                    relative_path_f = dir.name_in_column_files(url=trade_id, original_name=name)
                    name_on_server = dir.name_file_on_server(id=trade_id, original_name=name)
                    # try:
                    #     data_write = {name_on_server: parse_link}
                    #     with open('pictures.json', 'a') as f:
                    #         json.dump(data_write, f, ensure_ascii=False)
                    #         f.write('\n')
                    # except:
                    #     logger.error(f'{name_on_server} -> {parse_link} Data to file pictures does not write')
                    # time.sleep(0.5)
                    load.request_to_download(url=parse_link,
                                             referer=self.response.url, original_name=name_on_server)
                general.append({'original_name': name,
                                'link': relative_path_f,
                                'link_etp': parse_link})
        return general

    def download_lot_files(self, trade_id, lot_num):
        dir_ = self.dir_lot
        load = DownloadFiles()
        lots = list()
        lst_files = self.response.xpath(self.loc.file_lot_link_loc.format(lot_num)).getall()
        extra_name = None
        if len(lst_files) > 0:
            lst_files = lst_files
        else:
            return lots
        for file in lst_files:
            link = BS(str(file), features='lxml').find('a').get('href')
            name = dedent_func(BS(str(file), features='lxml').find('a').get_text())
            ic(name)

            parse_link = self.url.parse_url(self.url.url_join(data_origin_url, link))
            if (len(name) < 3) or (len(name) == 0) or (name is None) or (
                    name == 'None') or '%20' in name or '%25' or '' in name:
                try:
                    name = str(re.sub(r'download/.+/', '', str(link)))
                    name = name.replace('%20', str(randint(1, 256))).replace('%25', str(randint(1, 256))).replace(
                        '-', '_').replace(' ''', '').replace('%', str(randint(1, 9)))
                    name_suf = pathlib.Path(name).suffix
                    name = name.replace(name_suf, '')
                except Exception as e:
                    logger.warning(f'{e }')
                    extra_name = ''.join(dedent_func(pathlib.Path(str(link)).name))[0:6]
                    name = extra_name + dedent_func(pathlib.Path(str(link)).suffix)
            else:
                name = re.sub(r'. $', '_.', name)
            if name is not None and 'Протокол' not in name and 'Решение' not in name:
                relative_path_f = ''
                _suffix_name = None
                _suffix_link = None
                if pathlib.Path(name.replace(' ', '')).suffix in lst_exet:
                    _suffix_name = 1
                if pathlib.Path(str(parse_link).replace(' ', '')).suffix in lst_exet:
                    _suffix_link = 2
                if _suffix_name == 1 or _suffix_link == 2:
                    if len(name) > 52:
                        name = name[-1:-21:-1]
                    if _suffix_name != 1 and _suffix_link == 2:
                        name = name + dedent_func(pathlib.Path(str(link)).suffix)
                    dir_.create_dir()
                    relative_path_f = dir_.name_in_column_files_lot(url=trade_id, lot=lot_num,
                                                                    original_name=dedent_func(name))
                    name_on_server = dir_.name_file_on_server_lot(url=trade_id, lot=lot_num, original_name=name)
                    # try:
                    #     data_write = {name_on_server: parse_link}
                    #     with open('pictures.json', 'a') as f:
                    #         json.dump(data_write, f, ensure_ascii=False)
                    #         f.write('\n')
                    # except:
                    #     logger.error(f'{name_on_server} -> {parse_link} Data to file pictures does not write')
                    time.sleep(0.5)
                    load.request_to_download(url=parse_link,
                                             referer=self.response.url, original_name=name_on_server)
                lots.append({'original_name': name,
                             'link': relative_path_f,
                             'link_etp': parse_link})
        return lots
