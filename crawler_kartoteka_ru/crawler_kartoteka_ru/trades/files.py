import pathlib
from random import randint

from bs4 import BeautifulSoup as BS
from ..utils.work_with_path_and_dir import GeneralFilesDir
import re
from ..utils.config import _doc_page_link, path_relative, path_absolute, lst_exeption, _lot_link_part, lst_exet, \
    lst_exet_archive
from ..utils.work_with_text_and_number import dedent_func
from ..utils.working_with_url import UrlConfig
from ..utils.download import DownloadFiles


class General:

    def __init__(self, response_):
        self.response = response_
        self.url = UrlConfig()
        self._dir = GeneralFilesDir(path_absolute=path_absolute['kartoteka'], path_relative=path_relative['kartoteka'])
        self.soup = BS(str(self.response.text), features='lxml')


    def get_cache_number(self):
        """ return cache number for concatenation with document's page url if error then return random number """
        cache_number = self.soup.find(href=re.compile(r'/StylesCMS/kartotek.css\?cache=\d{11,16}'))
        if cache_number:
            cache_number = ''.join(re.findall(r'\d{11,16}', str(cache_number)))
            if len(cache_number) >= 11:
                return cache_number
        # RANDOM 13 NUMBERS
        return str(randint(162220000000, 162229999999))

    def get_full_doc_link(self, _id):
        """ return full link to document page """
        part_of_link = _doc_page_link['kartoteka_doc']
        return f'{part_of_link + str(_id) + "&&id=" + str(_id) + "&_=" + str(self.get_cache_number())}'

    def get_list_of_documents(self):
        """ retun list with full documents info """
        find_all_files = self.soup.find_all('a', href=re.compile(r'/files/download'))
        if len(find_all_files) > 0:
            return find_all_files

    def get_origin_name_and_link(self):
        """ if documents - return list with original name and link in unique tuple """
        general_lst = list()
        if files := self.get_list_of_documents():
            for file in files:
                name = file.get_text()
                if not any(exp in name for exp in lst_exeption):
                    link = self.url.url_join(_lot_link_part['kartoteka_lot'], file.get('href'))
                    general_lst.append((dedent_func(name.strip()), link))
        if len(general_lst) > 0:
            return general_lst

    def download_files_general(self, _id):
        """ itterate throught list with file info(name and link) """
        if lst := self.get_origin_name_and_link():
            download = DownloadFiles()
            general_lst = list()
            general_dict = dict()
            _path_relative = ''
            for f in lst:
                if pathlib.Path(f[0]).suffix in lst_exet:
                    if len(f[0]) > 75:
                        file_name_server = f[0][:30] + '_' + f[0][-35::1]
                    else:
                        file_name_server = f[0]
                    name_on_server = self._dir.name_file_on_server(_id=_id, original_name=file_name_server)
                    _path_absolute_to_write_file = self._dir.return_absolute_path(name_on_server)
                    self._dir.create_dir()
                    download.request_to_download_general(url=f[1], referer=self.response.url,
                                                         _abs_path=_path_absolute_to_write_file)
                    _path_relative = self._dir.name_in_column_files(name_on_server)
                    general_lst.append(
                        {'original_name': f[0], 'link': _path_relative,
                         'link_etp': self.url.parse_url(f[1])})
                elif pathlib.Path(f[0]).suffix in lst_exet_archive:
                    if len(f[0]) > 75:
                        file_name_server = f[0][:30] + '_' + f[0][-35::1]
                    else:
                        file_name_server = f[0]
                    name_on_server = self._dir.name_file_on_server(_id=_id, original_name=file_name_server)
                    _path_absolute = self._dir.return_absolute_path(name_on_server)
                    self._dir.create_dir()
                    lst_files = download.request_to_download_general(url=f[1],
                                                                     referer=self.response.url,
                                                                     _abs_path=_path_absolute,
                                                                     _id=_id,
                                                                     _relative_path=self._dir.return_download_dir_etp())
                    general_lst.extend(lst_files)
                else:
                    general_lst.append(
                        {'original_name': f[0], 'link': _path_relative,
                         'link_etp': self.url.parse_url(f[1])})

            general_dict['general'] = general_lst
            return general_dict
        else:
            return {'general': dict()}


class LotFiles:

    def __init__(self, response_):
        self.response = response_
        self.url = UrlConfig()
        self._dir = GeneralFilesDir(path_absolute=path_absolute['kartoteka'], path_relative=path_relative['kartoteka'])
        self.soup = BS(str(self.response.text), features='lxml')

    def get_list_of_documents(self, table):
        """ retun list with full documents info """
        find_all_files = table.find_all('a', href=re.compile(r'/files/download'))
        if len(find_all_files) > 0:
            return find_all_files

    def get_origin_name_and_link(self, table):
        """ if documents - return list with original name and link in unique tuple """
        lot_lst = list()
        if files := self.get_list_of_documents(table):
            for file in files:
                name = file.get_text()
                if not any(exp in name for exp in lst_exeption):
                    link = self.url.url_join(_lot_link_part['kartoteka_lot'], file.get('href'))
                    lot_lst.append((dedent_func(name.strip()), link))
        if len(lot_lst) > 0:
            return lot_lst

    def download_files_lot(self, _id, table, lot_number):
        """ itterate throught list with file info(name and link) """
        if lst := self.get_origin_name_and_link(table):
            download = DownloadFiles()
            lot_lst = list()
            lot_dict = dict()
            _path_relative = ''
            if lot_number is not None:
                lot_number = ''.join(lot_number)
            else:
                lot_number = ''
            for f in lst:
                if pathlib.Path(f[0]).suffix in lst_exet:
                    if len(f[0]) > 75:
                        file_name_server = f[0][:30] + '_' + f[0][-35::1]
                    else:
                        file_name_server = f[0]
                    name_on_server = self._dir.name_file_lot_on_server(_id=_id, lot_num=''.join(lot_number), original_name=file_name_server)
                    _path_absolute_to_write_file = self._dir.return_absolute_path(name_on_server)
                    self._dir.create_dir()
                    download.request_to_download_general(url=f[1], referer=self.response.url,
                                                         _abs_path=_path_absolute_to_write_file)
                    _path_relative = self._dir.name_in_column_files(name_on_server)
                    lot_lst.append(
                        {'original_name': f[0], 'link': _path_relative,
                         'link_etp': self.url.parse_url(f[1])})
                elif pathlib.Path(f[0]).suffix in lst_exet_archive:
                    if len(f[0]) > 75:
                        file_name_server = f[0][:30] + '_' + f[0][-35::1]
                    else:
                        file_name_server = f[0]
                    name_on_server = self._dir.name_file_lot_on_server(_id=_id, lot_num=''.join(lot_number), original_name=file_name_server)
                    _path_absolute = self._dir.return_absolute_path(name_on_server)
                    self._dir.create_dir()
                    lst_files = download.request_to_download_general(url=f[1],
                                                                     referer=self.response.url,
                                                                     _abs_path=_path_absolute,
                                                                     _id=_id,
                                                                     lot_num=lot_number,
                                                                     _relative_path=self._dir.return_download_dir_etp())
                    lot_lst.extend(lst_files)
                else:
                    lot_lst.append(
                        {'original_name': f[0], 'link': _path_relative,
                         'link_etp': self.url.parse_url(f[1])})

            lot_dict['lot'] = lot_lst
            return lot_dict
        else:
            return {'lot': dict()}




