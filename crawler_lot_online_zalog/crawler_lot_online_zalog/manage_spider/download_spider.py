import pathlib
from collections import namedtuple

from bs4 import BeautifulSoup as BS
import re
import logging

from general_utils import dedent_func, FilesDir, DownloadFiles
from general_utils.config import lst_exet, lst_exet_archive
from general_utils.models import RequestData
from ..utils.config import absolute_path, relative_path
from ..utils.post_data.common_data import data_address
from ..utils.work_with_path_and_dir import GeneralFilesDir, LotFilesDir
from ..utils.working_with_time import return_servertime
from ..utils.working_with_url import UrlConfig

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
                if any([True for x in lst_exet if x in f]):
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
        files_dir = FilesDir(relative_path, absolute_path)
        load = DownloadFiles()
        lst_general = list()
        for t in self.sort_data_files_general(body):
            files_dir.create_dir()
            a_id, origin_name, server_name = t
            name_on_server = files_dir.name_file_on_server(trading_id=trade_id, original_name=server_name)
            path_relative = files_dir.return_relative_path(name_on_server)
            path_absolute = files_dir.return_absolute_path(name_on_server)
            request_data = RequestData(
                url=url, referer=self.response.url, cookies=cookies, method='POST',
                data=self.post_data_download(view_state=view, a_id=a_id, body_=body)
            )
            if pathlib.Path(name_on_server).suffix not in lst_exet_archive:
                load.request_to_download_general(
                    request_data=request_data, absolute_path=path_absolute, relative_path=path_relative,
                    trading_id=trade_id
                )
                lst_general.append({'original_name': origin_name, 'link': path_relative.as_posix(), 'link_etp': url})
            elif pathlib.Path(name_on_server).suffix in lst_exet_archive:
                archive_lst = load.request_to_download_general(
                    request_data=request_data, absolute_path=path_absolute, relative_path=path_relative,
                    trading_id=trade_id
                )
                lst_general.extend(archive_lst)
            else:
                lst_general.append({'original_name': origin_name, 'link': '', 'link_etp': url})
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
        files_dir = FilesDir(relative_path, absolute_path)
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
                    files_dir.create_dir()
                    origin_name = self.url.return_path_name(link)
                    link_etp = dedent_func(''.join(link))
                    if len(origin_name) > 72:
                        origin_name = origin_name[0:15] + '_' + origin_name[-35:-1]
                    name_on_server = files_dir.name_file_lot_on_server(
                        trading_id=url_id, lot_number=lot_num, original_name=origin_name
                    )
                    path_relative = files_dir.return_relative_path(name_on_server)
                    path_absolute = files_dir.return_absolute_path(name_on_server)
                    request_data = RequestData(url=link_etp, referer=self.response.url, cookies=cookie)
                    if self.url.return_file_suffix(origin_name) in lst_exet:
                        load.request_to_download_general(
                            request_data=request_data,
                            absolute_path=path_absolute, relative_path=path_relative,
                            trading_id=url_id, lot_number=lot_num
                        )
                        lot.append({'original_name': origin_name, 'link': path_relative.as_posix(), 'link_etp': link_etp})
                    elif self.url.return_file_suffix(origin_name) in lst_exet_archive:
                        archive_lst = load.request_to_download_general(
                            request_data=request_data, absolute_path=path_absolute, relative_path=path_relative,
                            trading_id=url_id, lot_number=lot_num
                        )
                        lot.extend(archive_lst)
                    else:
                        lot.append({'original_name': origin_name, 'link': '', 'link_etp': link_etp})
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

    def get_region(self, body_):
        """ return d3 -> address """
        try:
            soup = BS(str(body_), features='lxml')
            d3 = soup.find('label', string=re.compile('Регион:')).findNext('div').get_text().strip()
            return dedent_func(d3)
        except Exception as e:
            print(e)
            return None

    def get_address(self, body_):
        """ return d3 -> address """
        try:
            soup = BS(str(body_), features='lxml')
            d4 = soup.find('label', string=re.compile('Адрес:')).findNext('div').get_text().strip()
            return dedent_func(d4)
        except Exception as e:
            print(e)
            return None
