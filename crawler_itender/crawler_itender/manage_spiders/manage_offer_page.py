import re
import pathlib
import pandas as pd
from bs4 import BeautifulSoup as BS

from general_utils import dedent_func, UrlConfig, format_time
from general_utils.work_with_path_and_dir import FilesDir
from ..locators.serp_locator import LocatorSerp
from ..locators.offer_locator import OfferLocator
from ..utils.config import path_absolute, path_relative, lst_exet, lst_exet_archive
import logging
from ..utils.download_img_files.download2 import DownloadFiles

logger = logging.getLogger(__name__)


class OfferPage:
    """ fetch info from serp (infjrmation after request - current page, next page, links to trading page """

    def __init__(self, _response):
        self.response = _response
        self.loc = LocatorSerp
        self.loc_offer = OfferLocator
        self.soup = BS(str(self.response.body.decode('utf-8')).replace('&lt;', '<').replace('&gt;', '>'),
                       features='lxml')

    def get_trading_number_offer(self):
        """ :return trading number for offer"""
        try:
            legend = self.response.xpath(self.loc_offer.trading_num_loc).get()
            if legend:
                legend = BS(str(legend), features='lxml').get_text()
                legend = ''.join(re.findall(r'\d+', legend))
                return legend
        except Exception as e:
            logger.error(f'{self.response.url} :: ERROR TRADING NUMBER\n{e}', exc_info=True)

    def get_lot_link(self, lot_number: str, _data_origin) -> str or None:
        """:return table with lots number and link (str(html))"""
        try:
            legend = self.response.xpath(self.loc_offer.lot_table).get()
            if legend:
                legend = BS(str(legend), features='lxml')
                table = legend.find('legend', string='Лоты публичного предложения').parent
                # choose type of trade
                if table and len(table) > 0:
                    link = table.find('a', string=lot_number)
                    if link:
                        link = link.get('href')
                        return UrlConfig.url_join(_data_origin, link)
        except Exception as e:
            logger.critical(f'{self.response.url} :{e}: INVALID DATA LOT TABLE', exc_info=True)
            return None

    def get_property_info(self):
        """ return short name """
        property_info = self.response.xpath(self.loc_offer.property_info_loc).get()
        if property_info:
            property_info = dedent_func(BS(str(property_info), features='lxml').get_text())
            return property_info.strip()

    @property
    def msg_number(self):
        """ :return message number """
        msg = self.response.xpath(self.loc_offer.msg_number_loc).get()
        if msg:
            msg = BS(str(msg), features='lxml').get_text()
            return ' '.join(re.findall(r'\d{6,8}', dedent_func(msg)))

    def trading_form(self):
        """return trading form"""
        try:
            form = self.response.xpath(self.loc_offer.trading_form_loc).get()
            if form:
                form = BS(str(form), features='lxml').get_text().lower()
                if 'открытая' == form:
                    return 'open'
                elif 'закрытая' == form:
                    return 'closed'
                else:
                    logger.error(f'{self.response.url} :: ERROR TRADING FORM')
        except Exception as e:
            logger.error(f'{self.response.url} :: TRDING TYPE ERROR')

    def get_period_table(self):
        """return pandas table """
        try:
            table = self.response.xpath(self.loc_offer.period_table_loc).get()
            table = BS(str(table), features='lxml')
            table = pd.read_html(str(table).replace(',', '.'))
            return table[0]
        except Exception as e:
            logger.error(f'{self.response.url} :: PERIOD TABLE NOT FOUND\{e}', exc_info=True)

    def return_periods(self):
        """:return table with all intervals"""
        try:
            period_lst = list()
            periods = self.get_period_table()
            col = periods.columns
            # len -1 does because o row it's text
            for p in range(len(periods) - 1):
                try:
                    start = periods.iloc[p + 1][1]
                    end = periods.iloc[p + 1][2]
                    price = re.sub(r'\s', '', periods.iloc[p + 1][len(col) - 2])
                    price = round(float(price.replace('&nbsp;', '')), 2)

                    period = {
                        'start_date_requests': format_time(start),
                        'end_date_requests': format_time(end),
                        'end_date_trading': format_time(end),
                        'current_price': price
                    }
                    period_lst.append(period)
                except:
                    continue
            return period_lst
        except Exception as e:
            logger.critical(f'{self.response.url} :: INVALID DARA PERIOD TABLE\n{e}', exc_info=True)
            return None

    @property
    def start_date_request_offer(self):
        """ return start date request """
        try:
            start = format_time(self.get_period_table().iloc[1][1])
            return start
        except Exception as e:
            logger.error(f'{self.response.url} :: INVALID DATA start date request offer\n{e}')
            return None

    @property
    def end_date_request_offer(self):
        """ :return end date request offer"""
        try:
            end = format_time(self.get_period_table().iloc[-1][2])
            return end
        except Exception as e:
            logger.error(f'{self.response.url} :: INVALID DATA start date request offer\n{e}')
            return None

    @property
    def start_date_trading_offer(self):
        """ return start date trading (the same as start date request """
        return self.start_date_request_offer

    @property
    def end_date_trading_offer(self):
        """ return end date trading (the same as end date request """
        return self.end_date_request_offer

    @property
    def price_offer(self):
        """ return start price offer """
        try:
            periods = self.get_period_table()
            col = periods.columns
            price = re.sub(r'\s', '', periods.iloc[1][len(col) - 2])
            return round(float(price), 2)
        except Exception as e:
            logger.error(f'{self.response.url} :: INVALID DATA START PRICE offer\n{e}')
            return None

    @property
    def get_documents(self):
        """ return files links (general and lots documents have similar selectors) """
        links = self.response.xpath(self.loc_offer.documents).getall()
        return links

    def general_files(self, _id, _data_origin, host, crawler_name):
        """return dictionary with general files"""
        files_dir = FilesDir(path_relative[crawler_name], path_absolute[crawler_name])
        load = DownloadFiles()
        try:
            general_dict = dict()
            general_lst = list()
            if len(self.get_documents) > 0:
                doc = self.get_documents
                for d in doc:
                    d = BS(str(d), features='lxml')
                    link_etp = d.find('a').get('href')
                    link_etp = UrlConfig.url_join(_data_origin, link_etp[1:])
                    file_name = d.find('a').get_text()
                    # on utender parser will frozen when download png pictures
                    if 'utender.ru' not in self.response.url:
                        lst_exet_ = lst_exet
                    else:
                        lst_exet_ = ['.jpeg', '.jpg', '.bmp', '.JPG', '.JPEG', 'jpg', 'jpeg', 'JPG', 'JPEG']
                    files_dir.create_dir()
                    name_on_server = files_dir.name_file_on_server(_id, original_name=file_name)
                    _path_absolute = files_dir.return_absolute_path(name_on_server)
                    _path_relative = files_dir.return_relative_path(name_on_server)
                    if pathlib.Path(file_name.replace(' ', '')).suffix in lst_exet_:
                        # itterate thought dictc and find path according dict key
                        load.request_to_download_general(url=link_etp, referer=self.response.url,
                                                         _abs_path=_path_absolute,
                                                         host=host, _id=_id, _relative_path=_path_relative)
                        general_lst.append({'original_name': file_name, 'link': _path_relative.as_posix(), 'link_etp': link_etp})
                    elif pathlib.Path(file_name).suffix in lst_exet_archive:
                        archive_files = load.request_to_download_general(url=link_etp, referer=self.response.url,
                                                                         _abs_path=_path_absolute,
                                                                         host=host, _id=_id,
                                                                         _relative_path=_path_relative)
                        general_lst.extend(archive_files)
                    else:
                        general_lst.append({'original_name': file_name, 'link': None, 'link_etp': link_etp})
                general_dict['general'] = general_lst
            return general_dict
        except:
            pass

    def lot_files(self, _id, lot_num, _data_origin, host, crawler_name):
        """ return dictionary with lots files"""
        load = DownloadFiles()
        files_dir = FilesDir(path_relative[crawler_name], path_absolute[crawler_name])
        try:
            lot_dict = dict()
            lot_lst = list()
            if len(self.get_documents) > 0:
                doc = self.get_documents
                for d in doc:
                    d = BS(str(d), features='lxml')
                    link_etp = d.find('a').get('href')
                    link_etp = UrlConfig.url_join(_data_origin, link_etp[1:])
                    file_name = d.find('a').get_text()
                    files_dir.create_dir()
                    name_on_server = files_dir.name_file_lot_on_server(_id, lot_num, file_name)
                    _path_absolute = files_dir.return_absolute_path(name_on_server)
                    _path_relative = files_dir.return_relative_path(name_on_server)
                    # if file is picture
                    # on utender parser will frozen when download png pictures
                    if 'utender.ru' not in self.response.url:
                        lst_exet_ = lst_exet
                    else:
                        lst_exet_ = ['.jpeg', '.jpg', '.bmp', '.JPG', '.JPEG', 'jpg', 'jpeg', 'JPG', 'JPEG']
                    if pathlib.Path(file_name.replace(' ', '')).suffix in lst_exet_:
                        # itterate thought dictc and find path according dict key
                        load.request_to_download_general(url=link_etp, referer=self.response.url,
                                                         _abs_path=_path_absolute,
                                                         host=host, _id=_id,
                                                         _relative_path=_path_relative)
                        lot_lst.append({'original_name': file_name, 'link': _path_relative.as_posix(), 'link_etp': link_etp})
                    elif pathlib.Path(file_name).suffix in lst_exet_archive:
                        archive_files = load.request_to_download_general(url=link_etp, referer=self.response.url,
                                                                         _abs_path=_path_absolute,
                                                                         host=host, _id=_id,
                                                                         _relative_path=_path_relative)
                        lot_lst.extend(archive_files)
                    else:
                        lot_lst.append({'original_name': file_name, 'link': _path_relative.as_posix(), 'link_etp': link_etp})
                lot_dict['lot'] = lot_lst
            return lot_dict
        except Exception as e:
            logger.error(f'{self.response.url} :: SOMETHING WENT WRONG\n{e}')

    # EXTRA FUNCTIONS - WHEN PERIODS HAS TWO (2) PAGES
    def concatination_two_list(self):
        """ return full list with periods from first and second pages """
        pass

    def find_error_page(self):
        """ if error text present on page """
        error_text = 'В приложении произошла ошибка'
        if error_text in self.response.text:
            logger.error(f'{self.response.url} :: НЕВОЗМОЖНО ОТОБРАЗИТЬ СТРАНИЦУ')
        else:
            return None
