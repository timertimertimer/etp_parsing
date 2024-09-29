import pathlib
from collections import namedtuple

from bs4 import BeautifulSoup as BS
import re
import logging

from crawler_lot_online_zalog.utils.config import lst_exet, lst_exet_img
from crawler_lot_online_zalog.utils.download import DownloadFiles
from crawler_lot_online_zalog.utils.post_data.common_data import data_address
from crawler_lot_online_zalog.utils.work_with_path_and_dir import GeneralFilesDir, LotFilesDir
from crawler_lot_online_zalog.utils.working_with_text_cookies_num import dedent_func
from crawler_lot_online_zalog.utils.working_with_time import return_servertime
from crawler_lot_online_zalog.utils.working_with_url import UrlConfig

logger = logging.getLogger(__name__)


class DownloadSpider:

    def __init__(self, response_):
        self.response = response_
        self.dir_general = GeneralFilesDir()
        self.dir_lot = LotFilesDir()
        self.url = UrlConfig()

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
        all_files_general = 'span[id*="fileName"]'
        lst_files = self.response.css(all_files_general).getall()
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
                date_file = ''.join(re.findall(r'\d{1,2}:\d{1,2}:\d{1,2}', origin_name)).replace(':', '').replace(
                    '.',
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
                                                                   post_data=self.post_data_download(
                                                                       view_state=view,
                                                                       a_id=a_id, body_=body),
                                                                   trade_id=trade_id)
                    lst_general.extend(archive_lst)
        return lst_general

    # download lot img (using link without post form data)
    @property
    def get_img_files(self):
        """return list with img span that consists picture 's name"""
        try:
            img_lot_locator = '//img//@src[contains(.,"resources/Temp/")]'
            lst_img = self.response.xpath(img_lot_locator).getall()
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
        first_part_url_lot = 'https://sales.lot-online.ru/e-auction/'
        file_param = "?pfdrid_c=true"
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

    def return_addeass_title(self, body_):
        """ preview address """
        soup = BS(str(body_), features='lxml')
        addr = soup.find('a', id='formMain:openAddrCardPreviewId')
        if addr:
            addr = addr.get_text()
            return dedent_func(addr)


    def get_address_block(self, body_, view_value):
        """ return param data for getting address info """
        param = data_address
        addr = self.return_addeass_title(body_)
        if addr:
            param['formMain:addrLatitudeIdView'] = self.get_latitude(body_)
            param['formMain:addrLongitudeIdView'] = self.get_longtitude(body_)
            param['javax.faces.ViewState'] = view_value
            param['formMain:inputServerTime'] = return_servertime()
            param['formMain:addrAddressIdView'] = addr
            return param

    def get_address(self, body_):
        """ return d3 -> address """
        try:
            soup = BS(str(body_), features='lxml')
            d3 = soup.find('label', string=re.compile('Регион:')).findNext('div').get_text().strip()
            return dedent_func(d3)
        except Exception as e:
            print(e)
            return None

    def get_detaled_address(self, body_):
        """ return d3 -> address """
        try:
            soup = BS(str(body_), features='lxml')
            d4 = soup.find('label', string=re.compile('Адрес:')).findNext('div').get_text().strip()
            return dedent_func(d4)
        except Exception as e:
            print(e)
            return None

