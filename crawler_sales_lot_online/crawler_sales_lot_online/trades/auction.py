import logging
import pathlib
import re
from collections import namedtuple

from bs4 import BeautifulSoup as BS

from ..locators.locator_trades import LocatorAuction
from ..utils.check_inn_email_phone import CheckIfCorrectContactInfo
from ..utils.config import lst_exet, first_part_url_lot, file_param, lst_exet_img
from ..utils.download import DownloadFiles
from ..utils.work_with_path_and_dir import GeneralFilesDir, LotFilesDir
from ..utils.work_with_text_and_number import dedent_func, get_lot_number, cut_lot_number, delete_extra_symbols
from ..utils.working_with_time import format_time, return_servertime
from ..utils.working_with_url import UrlConfig

logger = logging.getLogger(__name__)


class AuctionParse:
    def __init__(self, response_):
        self.response = response_
        self.loc = LocatorAuction
        self.check = CheckIfCorrectContactInfo
        self.dir_general = GeneralFilesDir()
        self.dir_lot = LotFilesDir()
        self.url = UrlConfig()

    @property
    def trade_id(self):
        """using regular expression return trading id"""
        url_lot = self.response.url
        match = re.findall(r'\d{11,13}', url_lot)
        if match and len(''.join(match)) > 11:
            return ''.join(match)
        else:
            logger.error(f'{self.response.url} :: ERROR GETTING TRADE ID')
            return None

    def trading_number(self, text):
        """using regular expression fetch trading number from text inside right side bar of the page"""
        pattern = r'Идентификатор лота в ЕФРСБ.*?\s.*?(\d+)\s?'
        match = re.findall(pattern, text)
        if len(match) > 0:
            if 5 < len(''.join(match)) < 20:
                return ''.join(match)
        else:
            logger.error(f'{self.response.url} :: INVALID DATA TRADING NUMBER')
            return None

    @property
    def return_div_org(self):
        """:return block(div) with organizer info"""
        return self.response.xpath(self.loc.organizator_div_loc).get()

    @property
    def trading_organizer(self):
        """return field 'naimenovanie' with person or company name of organizer of trade """
        div_organizer = self.return_div_org
        if div_organizer:
            soup = BS(str(div_organizer), features='lxml')
            try:
                naimenovanie = soup.find("label", text="Наименование").next_sibling.strip()
                return naimenovanie
            except Exception as e:
                logger.error(f'{self.response.url} :: INVALID DATA "NAIMENOVANIE" ORGANIZER INFO')
                return e
        else:
            logger.error(f'{self.response.url} :: INFO ABOUT ORGANIZER IS ABSENT')
            return None

    @property
    def trading_org_inn(self):
        """return inn org !!!!IF EXIST!!!!!!!! """
        div_organizer = self.return_div_org
        if div_organizer:
            soup = BS(str(div_organizer), features='lxml')
            try:
                inn_org = soup.find("label", text="ИНН").next_sibling.strip()
                return self.check.check_inn(inn_org)
            except Exception as e:
                logger.error(f'{self.response.url} :: INVALID DATA INN ORGANIZER INFO\n\n\n{e}')
                return None
        else:
            logger.error(f'{self.response.url} :: INFO ABOUT ORGANIZER IS ABSENT')
            return None

    @property
    def org_email(self):
        """:return organizer email"""
        div_organizer = self.return_div_org
        if div_organizer:
            soup = BS(str(div_organizer), features='lxml')
            try:
                email = soup.find("label", text="Электронная почта").next_sibling.strip()
                return self.check.check_email(email)
            except:
                logger.warning(f'{self.response.url} :: INVALID DATA EMAIL ORGANIZER INFO')
                return ''
        else:
            logger.error(f'{self.response.url} :: INFO ABOUT ORGANIZER IS ABSENT')
            return None

    @property
    def org_phone(self):
        """:return organizer email"""
        div_organizer = self.return_div_org
        if div_organizer:
            soup = BS(str(div_organizer), features='lxml')
            try:
                phone = soup.find("label", text="Телефоны").next_sibling.strip()
                return self.check.check_phone(phone)
            except:
                logger.warning(f'{self.response.url} :: INVALID DATA PHONE ORGANIZER INFO ')
                return ''
        else:
            logger.error(f'{self.response.url} :: INFO ABOUT ORGANIZER IS ABSENT')
            return None

    @property
    def organizer_contacts(self):
        """receive two function with email and phone and return combine dictionary with contacts"""
        try:
            return {'email': self.org_email,
                    'phone': self.org_phone}
        except:
            logger.error(f'{self.response.url} :: INVALID DATA ORG CONTACTS')
            return None

    @property
    def return_debit_field(self):
        """:return block with debitor info"""
        try:
            return self.response.xpath(self.loc.debitor_info_fieldset_loc).get()
        except:
            logger.error(f'{self.response.url} :: DATA WITH DEBITOR INFO DOES NOT DOWNLOAD')
            return None

    @property
    def debitor_inn(self):
        """return debitor inn"""
        fiedset = self.return_debit_field
        if fiedset:
            soup = BS(str(fiedset), features='lxml')
            try:
                return self.check.check_inn(soup.find("label", text="ИНН").next_sibling.strip())
            except:
                logger.error(f'{self.response.url} :: INVALID DATA DEBITOR INN')
        else:
            logger.error(f'{self.response.url} :: HAVE PROBLEMS WITH DOWNLOAD DEBITOR BLOCK')

    @property
    def case_number(self):
        """return debitor inn"""
        fiedset = self.return_debit_field
        if fiedset:
            soup = BS(str(fiedset), features='lxml')
            try:
                case_number = soup.find("label",
                                        text="Полный номер дела о банкротстве").next_sibling.next_sibling.strip()

                return case_number.replace('№', '').replace('\\', '/').replace(' ', '').strip()
            except:
                logger.error(f'{self.response.url} :: INVALID DATA CASE NUMBER')
        else:
            logger.error(f'{self.response.url} :: HAVE PROBLEMS WITH DOWNLOAD DEBITOR BLOCK')

    @property
    def msg_number(self):
        """return debitor inn"""
        fiedset = self.return_debit_field
        if fiedset:
            soup = BS(str(fiedset), features='lxml')
            try:
                msg_number = soup.find("label",
                                       text="Номер объявления о проведении торгов в ЕФРСБ").next_sibling.strip()
                return msg_number
            except:
                logger.error(f'{self.response.url} :: INVALID DATA MSG NUMBER')
        else:
            logger.error(f'{self.response.url} :: HAVE PROBLEMS WITH DOWNLOAD DEBITOR BLOCK')

    # WORKING WITH ARBITR WITHOUT CLICK
    # Working with block arbitr manager/ competition manager
    @property
    def return_arbitr_block(self):
        """return block with arbitr or comp manager info"""
        try:
            bodyy_arbitr = self.response.body.decode('utf-8')
            return bodyy_arbitr
        except:
            return None

    @property
    def return_title_arbitr_block(self):
        """:return title(text) of arbitr info(arbitr or competition manager"""
        try:
            block = self.response.xpath(self.loc.arbitr_fieldset_text_loc).get()
            return dedent_func(block)
        except:
            return None

    def arbitr_name(self, arbitr_title, url):
        """return arbitr or company name according current filed(name-last_name or @naimenovanie)"""
        try:
            arb_block = self.return_arbitr_block
            soup = BS(str(arb_block), features='lxml')
            block_title = dedent_func(arbitr_title)
            if arb_block:
                if block_title == 'Конкурсный управляющий':
                    label = soup.find("label", text="Наименование")
                    return label.next_sibling.strip()
                elif block_title == 'Арбитражный управляющий':
                    name = ''.join(soup.find("label", text="Имя").next_sibling.strip()).replace('&nbsp', '').strip()
                    last = ''.join(soup.find("label", text="Фамилия").next_sibling.strip()).replace('&nbsp', '').strip()
                    middle = ''.join(soup.find("label", text="Отчество").next_sibling.strip()).replace('&nbsp', '').strip()
                    return last + ' ' + name + ' ' + middle

        except Exception as e:
            # logger.error(f'{self.response.url} :: INVALID DATA ARBITR FIELD NAME, {url}\n {e}\n{block_title}')
            return None

    @property
    def arbitr_inn(self):
        """return arbitr inn"""
        try:
            arb_block = self.return_arbitr_block
            soup = BS(str(arb_block), features='lxml')
            label = soup.find("label", text="ИНН").next_sibling.strip()
            return self.check.check_inn(label)
        except:
            with open('error_arbitr.txt', 'w') as f:
                f.write(self.response.text)
            logger.error(f'{self.response.url} :: INVALID DATA ARBITR FIELD INN')
            return None

    def arbitr_org(self, arbitr_title):
        """return arbitr or company name according current filed(name-last_name or @naimenovanie)"""
        try:
            arb_block = self.return_arbitr_block
            soup = BS(str(arb_block), features='lxml')
            block_title = dedent_func(arbitr_title)
            if arb_block:
                if block_title == 'Конкурсный управляющий':
                    return None
                elif block_title == 'Арбитражный управляющий':
                    label = soup.find("label", text="СРО").next_sibling.strip()
                    return label
        except:
            logger.error(f'{self.response.url} :: INVALID DATA ARBITR FIELD ORG')
            return None

    # END WORKING WITH ARBITR WITHOUT CLICK

    # WORKING WITH CLICK TO ARBITR
    @property
    def return_arbitr_block_click(self):
        """return block with arbitr or comp manager info"""
        try:
            return self.response.xpath(self.loc.arbitr_click_fieldset_loc).get()
        except:
            return None

    @property
    def return_title_arbitr_block_click(self):
        """:return title(text) of arbitr info(arbitr or competition manager"""
        try:
            block = self.response.xpath(self.loc.arbitr_click_fieldset_text_loc).get()
            return dedent_func(block)
        except:
            return None

    @property
    def arbitr_name_click(self):
        """return arbitr or company name according current filed(name-last_name or @naimenovanie)"""
        try:
            arb_block = self.return_arbitr_block_click
            soup = BS(str(arb_block), features='lxml')
            block_title = self.return_title_arbitr_block_click
            if arb_block:
                if block_title == 'Конкурсный управляющий':
                    label = soup.find("label", text="Наименование")
                    return label.next_sibling.strip()
                elif block_title == 'Арбитражный управляющий':
                    name = ''.join(soup.find("label", text="Имя").next_sibling.strip())
                    last = ''.join(soup.find("label", text="Фамилия").next_sibling.strip())
                    middle = ''.join(soup.find("label", text="Отчество").next_sibling.strip())
                    return last + ' ' + name + ' ' + middle
                else:
                    return None

        except:
            with open('arbitr.txt', 'w') as f:
                f.write(self.response.text)
            logger.error(f'{self.response.url} :: INVALID DATA ARBITR FIELD NAME')
            return None

    @property
    def arbitr_inn_click(self):
        """return arbitr inn"""
        try:
            arb_block = self.return_arbitr_block_click
            soup = BS(str(arb_block), features='lxml')
            label = soup.find("label", text="ИНН").next_sibling.strip()
            return self.check.check_inn(label)
        except:
            logger.error(f'{self.response.url} :: INVALID DATA ARBITR FIELD INN')
            return None

    @property
    def arbitr_org_click(self):
        """return arbitr or company name according current filed(name-last_name or @naimenovanie)"""
        try:
            arb_block = self.return_arbitr_block_click
            soup = BS(str(arb_block), features='lxml')
            block_title = self.return_title_arbitr_block_click
            if arb_block:
                if block_title == 'Конкурсный управляющий':
                    return None
                elif block_title == 'Арбитражный управляющий':
                    label = soup.find("label", text="СРО").next_sibling.strip()
                    return label
        except:
            logger.error(f'{self.response.url} :: INVALID DATA ARBITR FIELD ORG')
            return None

    # END WORKING WITH CLICK ARBITR

    @property
    def status_lot(self):
        """return text of status. convert in item (loader)"""
        status = self.response.css(self.loc.status_lot_loc_css).get()
        try:
            return dedent_func(BS(str(status), features='lxml').get_text())
        except:
            logger.error(f'{self.response.url} :: INVALID DATA STATUS')
            return None

    @get_lot_number
    def lot_number(self):
        """:return text if exist with lot number, after decorator fetch lot number or asign 1"""
        lot_number = self.response.css(self.loc.lot_number_css_loc).get()
        if lot_number:
            return dedent_func(BS(str(lot_number), features='lxml').get_text())
        else:
            return ''

    @delete_extra_symbols
    @cut_lot_number
    def short_name(self):
        """:return short name(field) of lot"""
        h1 = self.response.xpath(self.loc.short_name_loc).get()
        em = self.response.css(self.loc.extra_check_short_name_loc).getall()
        try:
            soup = BS(str(h1), features='lxml')
            if len(em) == 2:
                match = re.split(',', soup.get_text(), maxsplit=2)
                match = list(map(lambda x: dedent_func(x), match))[-1]
                return ''.join(match)
            elif len(em) == 1:
                match = re.split(',', soup.get_text(), maxsplit=1)
                match = list(map(lambda x: dedent_func(x), match))[-1]
                return ''.join(match)
            else:
                return None
        except:
            logger.error(f'{self.response.url}:: ERROR SHORT NAME')
            return None

    @delete_extra_symbols
    @cut_lot_number
    def lot_info(self):
        """:return short name(field) of lot"""
        p = self.response.xpath(self.loc.lot_info_loc).get()
        try:
            if p:
                lot_info = dedent_func(BS(str(p), features='lxml').get_text())
                return lot_info
            else:
                return None
        except:
            logger.error(f'{self.response.url}:: ERROR LOT INFO')

    @property
    def property_info(self):
        """:return short name(field) of lot"""
        p = self.response.xpath(self.loc.property_info_loc).get()
        try:
            if p:
                property_info = dedent_func(BS(str(p), features='lxml').get_text())
                return property_info
            else:
                return None
        except:
            logger.error(f'{self.response.url}:: ERROR PROPERTY INFO')

    def start_and_end_date_request_auc(self, text):
        """:return list with two dates of request using re pattern, info fetch from right side bar """
        try:
            patter_start_end_request = self.loc.pattern_start_end_request
            match = ''.join(re.findall(patter_start_end_request, text))
            if 31 < len(match) < 35:
                match = re.split(r'\s', match)
                return match
            else:
                print('###########', match)
                logger.error(f'{self.response.url} :: INCORECT LEN OF START AND END DATE REQUEST TEXT')
                return None
        except:
            logger.error(f'{self.response.url} :: INCORECT DATA OF START AND END DATE REQUEST TEXT')
            return None

    def start_date_request_auc(self, text):
        """return start date requests. Get list with two date return first """
        try:
            start = self.start_and_end_date_request_auc(text)
            return format_time(start[0] + ' ' + ' ' + start[1])
        except:
            logger.error(f'{self.response.url} :: INVALID DATA OF START  DATE REQUEST ')
            return None

    def end_date_request_auc(self, text):
        """return start date requests. Get list with two date return first """
        try:
            end = self.start_and_end_date_request_auc(text)
            return format_time(end[-2] + ' ' + ' ' + end[-1])
        except:
            logger.error(f'{self.response.url} :: INVALID DATA OF END  DATE REQUEST ')
            return None

    def start_date_trading_auc(self, text):
        """return start date trading. Data fetch from right side bar"""
        try:
            patter = r'(Время проведения торгов|Время проведения процедуры) (\d{1,2}.\d{1,2}.\d{2,4}) .*? (\d{1,2}:\d{1,2}).*'
            match = re.findall(patter, text)[0]
            return format_time(' '.join(match))

        except:
            logger.warning(f'{self.response.url} :: INVALID DATA OF START DATE TRADING ')
            return self.end_date_trading_auc(text)

    def end_date_trading_auc(self, text):
        """return start date trading. Data fetch from right side bar"""
        try:
            # start_trading = self.start_date_trading_auc(text)
            # if start_trading is None:
            patter = r'Подведение итогов (\d{1,2}.\d{1,2}.\d{2,4}) .*? (\d{1,2}:\d{1,2}).*'
            match = re.findall(patter, text)[0]
            return format_time(' '.join(match))
            # else:
            #     return None
        except:
            return None

    def step_price(self, text):
        """:return step price of auction"""
        try:
            pattern_step = r'Шаг на повышение.*\d+.?\d+,?\d{1,2}?.*р?у?б?.*Сумма'
            pattern1 = r'Шаг на повышение.*\d.*Сумма'
            pattern2 = r'Шаг аукциона.*\d+.?\d+,?\d{1,2}?.*р?у?б?.*Сумма'
            pattern3 = r'Шаг аукциона.*\d.*Сумма'
            pattern4 = r'Шаг.*\d.*Сумма'
            match_price = re.findall(pattern_step, text)
            if len(match_price) == 0:
                match_price = re.findall(pattern1, text)
            if len(match_price) == 0:
                match_price = re.findall(pattern2, text)
            if len(match_price) == 0:
                match_price = re.findall(pattern3, text)
            if len(match_price) == 0:
                match_price = re.findall(pattern4, text)
            match_price = ''.join(filter(lambda x: x.isdigit() or x == ',' or x == '.', match_price[0]))
            match_price = re.sub(r'\D$', '', match_price).strip()
            return round(float(match_price.replace(',', '.')), 2)
        except Exception as e:
            logger.warning(f'{self.response.url} :: INVALID DATA STEP PRICE {e}')

    # working with files
    def get_latitude(self, body_):
        """get addrLatitudeIdView from response body for sending post request with this data for download"""
        try:
            soup = BS(str(body_), features='lxml')
            lat = soup.find('input', id='formMain:addrLatitudeIdView')['value']
            return dedent_func(lat)
        except:
            return None

    def get_longtitude(self, body_):
        """get addrLongitudeIdVie from response body for sending post request with this data for download"""
        try:
            soup = BS(str(body_), features='lxml')
            long = soup.find('input', id='formMain:addrLongitudeIdView')['value']
            return dedent_func(long)
        except:
            return None

    def get_addr_view(self, body_):
        """get formMain:addrAddressIdView from response body for sending post request with this data for download"""
        try:
            soup = BS(str(body_), features='lxml')
            addr = soup.find('input', id='formMain:addrAddressIdView')['value']
            return dedent_func(addr)
        except:
            return None

    @property
    def fetch_all_files_general(self):
        """get and return all files for download but ignore protocol and 'reshenie' """
        lst_files = self.response.css(self.loc.all_files_general).getall()
        # delete all unnecessary files from lst_files
        clean_lst = list()
        if isinstance(lst_files, list) and len(lst_files) > 0:
            for f in lst_files:
                if 'Протокол' in f or 'Решение' in f:
                    continue
                else:
                    clean_lst.append(f)
        return clean_lst

    def sort_data_files_general(self, body):
        """create and return list with tuples that contains span id(for post data), origin name and modify server name(only name without path)"""
        GeneralFiles = namedtuple('GeneralFiles', 'span, original_name, server_name')
        fg = GeneralFiles(None, None, None)
        lst_with_tuples = list()
        lst = self.fetch_all_files_general
        if len(lst) > 0:
            for doc in lst:
                soup = BS(str(doc), features='lxml')
                # span for post data -> getting id of a -> it's parent of span
                span = soup.span.get('id')
                a_id = self.getting_a_id(body_=body, span_id=span)
                origin_name = soup.get_text()
                if len(origin_name) > 72:
                    origin_name = origin_name[0:15] + origin_name[-35:-1]
                server_name_only_name = re.split(r'\(', origin_name, maxsplit=1)[0]
                date_file = ''.join(re.findall(r'\d{1,2}:\d{1,2}:\d{1,2}', origin_name)).replace(':', '').replace('.',
                                                                                                                  '')
                if date_file:
                    date_file = date_file
                else:
                    date_file = '_'
                suffix = list(map(lambda e: e, filter(lambda x: x in origin_name, lst_exet)))
                if len(suffix) > 0:
                    suffix = suffix[0]
                    server_name = re.sub(r'\s+', '_', (server_name_only_name + date_file + '_' + suffix))
                    fg = GeneralFiles(span=a_id, original_name=origin_name, server_name=server_name)
                    lst_with_tuples.append(fg)
        return lst_with_tuples

    def getting_a_id(self, body_, span_id):
        """getting tag a id for post data"""
        try:
            soup = BS(str(body_), features='lxml')
            a_id = soup.find('span', attrs={"id": span_id}).find_parent('a').get('id')
            if a_id:
                return a_id
        except:
            logger.error(f'{self.response.url} :: error in function getting_a_id')
            return None

    def arbitr_data_post(self, view_state, body_):
        """return dict with post form data for download"""
        latitude = self.get_latitude(body_)
        longtitude = self.get_longtitude(body_)
        addres = self.get_addr_view(body_)
        if latitude:
            return {'formMain': 'formMain',
                    'formMain:inputServerTime': return_servertime(),
                    'formMain:commonSearchCriteriaStr': '',
                    'formMain:addrLatitudeIdView': latitude,
                    'formMain:addrLongitudeIdView': longtitude,
                    'formMain:addrAddressIdView': addres,
                    'javax.faces.ViewState': view_state,
                    'javax.faces.source': 'formMain:clDpExpEvent4',
                    'javax.faces.partial.event': 'click',
                    'javax.faces.partial.execute': 'formMain:clDpExpEvent4 formMain:clDpExpEvent4',
                    'javax.faces.partial.render': 'formMain:panelGroupArbitrManager',
                    'javax.faces.behavior.event': 'action',
                    'javax.faces.partial.ajax': 'true'}
        else:
            return {'formMain': 'formMain',
                    'formMain:inputServerTime': return_servertime(),
                    'formMain:commonSearchCriteriaStr': '',
                    'javax.faces.ViewState': view_state,
                    'javax.faces.source': 'formMain:clDpExpEvent4',
                    'javax.faces.partial.event': 'click',
                    'javax.faces.partial.execute': 'formMain:clDpExpEvent4 formMain:clDpExpEvent4',
                    'javax.faces.partial.render': 'formMain:panelGroupArbitrManager',
                    'javax.faces.behavior.event': 'action',
                    'javax.faces.partial.ajax': 'true'}

    def post_data_download(self, view_state, a_id, body_):
        """return dict with post form data for download"""
        latitude = self.get_latitude(body_)
        longtitude = self.get_longtitude(body_)
        addres = self.get_addr_view(body_)
        if latitude:
            return {'formMain': 'formMain',
                    'formMain:inputServerTime': return_servertime(),
                    'formMain:commonSearchCriteriaStr': '',
                    'formMain:addrLatitudeIdView': self.get_latitude(body_),
                    'formMain:addrLongitudeIdView': self.get_longtitude(body_),
                    'formMain:addrAddressIdView': self.get_addr_view(body_),
                    'javax.faces.ViewState': view_state,
                    a_id: a_id}
        else:
            return {'formMain': 'formMain',
                    'formMain:inputServerTime': return_servertime(),
                    'formMain:commonSearchCriteriaStr': '',
                    'javax.faces.ViewState': view_state,
                    a_id: a_id}

    def download_general(self, url, trade_id, cookies, view, body):
        """unpack tupels from function -> sort_data_files_general and download all files
        :arg url -> link for request (url_for_post_download in config.py)
        :arg trade_id
        :arg cookies -> current cookies
        :arg view -> param of post data
        :arg body -> response body"""
        dir_ = self.dir_general
        url = url
        load = DownloadFiles()
        lst_general = list()
        for t in self.sort_data_files_general(body):
            dir_.create_dir()
            a_id, origin_name, server_name = t
            name_on_server = dir_.name_file_on_server(id_=trade_id, original_name=server_name)
            if "Протокол" not in name_on_server or "протокол" not in name_on_server:
                # from icecream import ic
                # ic(origin_name)
                relative_path = dir_.name_in_column_files(id_=trade_id, original_name=server_name)
                if pathlib.Path(name_on_server).suffix not in ['.zip', '.rar', '.7z']:
                    load.request_to_download_general(url=url, referer=self.response.url,
                                                     original_name=name_on_server, cookies=cookies,
                                                     post_data=self.post_data_download(view_state=view, a_id=a_id,
                                                                                       body_=body),
                                                     trade_id=trade_id)
                    lst_general.append({'original_name': origin_name,
                                        'link': relative_path, 'link_etp': relative_path})
                elif pathlib.Path(name_on_server).suffix in ['.zip', '.rar', '.7z']:
                    archive_lst = load.request_to_download_general(url=url, referer=self.response.url,
                                                                   original_name=name_on_server, cookies=cookies,
                                                                   post_data=self.post_data_download(view_state=view,
                                                                                                     a_id=a_id,
                                                                                                     body_=body),
                                                                   trade_id=trade_id)
                    lst_general.extend(archive_lst)
        return lst_general

    # download lot img (using link without post form data)
    @property
    def get_img_files(self):
        """return list with img span that consists picture 's name"""
        try:
            lst_img = self.response.xpath(self.loc.img_lot_locator).getall()
            if len(lst_img) > 0:
                return lst_img
            else:
                return list()
        except:
            logger.error(f'{self.response.url} :: PROBLEMS WITH GETTING IMG (FORM)')
            return list()

    # main download lot img
    def download_lot_img(self, url_id, lot_num, cookie):
        """:arg url_id -> response url
        :arg lot_num
        :arg cookie -> current cookies"""
        dir_ = self.dir_lot
        load = DownloadFiles()
        lot = list()
        link_list = self.get_img_files
        f = first_part_url_lot
        link_set = set()
        if len(link_list) > 0:
            try:
                for img in link_list:
                    img = re.split(';', (f + img.replace('short_', '')), maxsplit=1)[0]
                    link_set.add(img + file_param)
                for link in link_set:
                    origin_name = self.url.return_path_name(link)
                    link_etp = dedent_func(''.join(link))
                    if len(origin_name) > 72:
                        origin_name = origin_name[0:15] + '_' + origin_name[-35:-1]
                    if self.url.return_file_suffix(origin_name) in lst_exet_img:
                        name_on_server = dir_.name_file_on_server_lot(url_id=url_id, lot=lot_num,
                                                                      original_name=origin_name)
                        relative_path = dir_.name_in_column_files_lot(url_id=url_id, lot=lot_num,
                                                                      original_name=origin_name)
                        load.request_to_download_lot(url=link, referer=self.response.url,
                                                     original_name=name_on_server, cookies=cookie)
                        lot.append({'original_name': origin_name,
                                    'link': relative_path, 'link_etp': relative_path})

                return lot

            except:
                logger.error(f'{self.response.url} :: INVALID DATA IMG DOWNLOAD', exc_info=True)
                return None
        else:
            return list()
