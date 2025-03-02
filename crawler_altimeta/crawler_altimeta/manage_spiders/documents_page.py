import pathlib
import re
from bs4 import BeautifulSoup as BS

from general_utils.config import lst_exet, lst_exet_archive
from ..locators.locators_trade_page import LocatorTradePage
from ..utils.work_with_text_and_number import dedent_func
from ..utils.working_with_url import UrlConfig
from ..utils.download import DownloadFiles
from ..utils.work_with_path_and_dir import GeneralFilesDir


class DocPage:

    def __init__(self, response_):
        self.response = response_
        self.soup = BS(str(self.response.text).replace('&lt;', '<').replace('&gt;', '>'), features='lxml')
        self.loc_trade = LocatorTradePage
        self.url = UrlConfig()
        self.download = DownloadFiles()

    def get_all_doc_files(self):
        """ get all  tags <a> and return list of this tag """
        docs = self.response.xpath(self.loc_trade.files_data_loc).getall()
        return docs

    def general_docs(self, full_path, relative_path, main_url, _id):
        """ get all general files and if it will find picture - download it """
        general_dict = dict()
        general_lst = list()
        if len(self.get_all_doc_files()) > 0:
            docs = self.get_all_doc_files()
            for d in docs:
                d = BS(str(d), features='lxml')
                link_etp = d.find('a').get('href')
                # link_etp = re.sub(r'\s', '', link_etp)
                link_etp = self.url.url_join(main_url, link_etp)
                file_name = dedent_func(d.find('a').get_text().replace('. ', '.'))
                _path_relative = None
                _dir = GeneralFilesDir(path_relative=relative_path, path_absolute=full_path)
                if 'Протокол' not in file_name and 'Решение' not in file_name and 'Protocol' not in file_name and 'Reshenie' not in file_name:
                    if pathlib.Path(file_name).suffix in lst_exet:
                        if len(file_name) > 75:
                            file_name_server = file_name[:30] + '_' + file_name[-35::1]
                        else:
                            file_name_server = file_name
                        name_on_server = _dir.name_file_on_server(_id=_id, original_name=file_name_server)
                        _path_absolute = _dir.return_absolute_path(name_on_server)
                        _dir.create_dir()
                        self.download.request_to_download_general(url=link_etp,
                                                                  referer=self.response.url,
                                                                  host=main_url,
                                                                  _abs_path=_path_absolute)
                        _path_relative = _dir.name_in_column_files(name_on_server)
                    general_lst.append(
                        {'original_name': file_name, 'link': _path_relative, 'link_etp': self.url.parse_url(link_etp)})
                    # FILES INSIDE ARCHIVE
                    if pathlib.Path(file_name).suffix in lst_exet_archive:
                        if len(file_name) > 75:
                            file_name_server = file_name[:30] + '_' + file_name[-35::1]
                        else:
                            file_name_server = file_name
                        name_on_server = _dir.name_file_on_server(_id=_id, original_name=file_name_server)
                        _path_absolute = _dir.return_absolute_path(name_on_server)
                        _dir.create_dir()
                        lst_files = self.download.request_to_download_general(url=link_etp,
                                                                              referer=self.response.url,
                                                                              host=main_url,
                                                                              _abs_path=_path_absolute,
                                                                              _id=_id,
                                                                              _relative_path=_dir.return_download_dir_etp())
                        general_lst.extend(lst_files)
            general_dict['general'] = general_lst
            return general_dict
        else:
            return general_dict

    # Documents from lot page
    def get_lot_docs(self, table_, full_path, relative_path, main_url, _id, lot_num):
        """ get all lot files and if it will find picture - download it """
        lot_dict = dict()
        lot_lst = list()
        soup = BS(str(table_), features='lxml')
        all_docs = soup.find_all('a')
        if all_docs and len(all_docs) > 0:
            for d in all_docs:
                d = BS(str(d), features='lxml')
                link_etp = d.find('a').get('href')
                # link_etp = re.sub(r'\s', '', link_etp)
                link_etp = self.url.url_join(main_url, link_etp)
                file_name = dedent_func(d.find('a').get_text().replace('. ', '.'))
                _dir = GeneralFilesDir(path_relative=relative_path, path_absolute=full_path)
                _path_relative = None
                if 'Протокол' not in file_name and 'Решение' not in file_name and 'Protocol' not in file_name and 'Reshenie' not in file_name:
                    if pathlib.Path(file_name).suffix in lst_exet:
                        if len(file_name) > 75:
                            file_name_server = file_name[:30] + '_' + file_name[-35::1]
                        else:
                            file_name_server = file_name
                        name_on_server = _dir.name_file_lot_on_server(_id=_id, original_name=file_name_server,
                                                                      lot_num=lot_num)
                        _path_absolute = _dir.return_absolute_path(name_on_server)
                        _dir.create_dir()
                        self.download.request_to_download_general(url=link_etp,
                                                                  referer=self.response.url,
                                                                  host=main_url,
                                                                  _abs_path=_path_absolute)
                        _path_relative = _dir.name_in_column_files(name_on_server)
                    lot_lst.append(
                        {'original_name': file_name, 'link': _path_relative, 'link_etp': self.url.parse_url(link_etp)})
                    # FILES INSIDE ARCHIVE
                    if pathlib.Path(file_name).suffix in lst_exet_archive:
                        if len(file_name) > 75:
                            file_name_server = file_name[:30] + '_' + file_name[-35::1]
                        else:
                            file_name_server = file_name
                        name_on_server = _dir.name_file_lot_on_server(_id=_id, original_name=file_name_server,
                                                                      lot_num=lot_num)
                        _path_absolute = _dir.return_absolute_path(name_on_server)
                        _dir.create_dir()
                        lst_files = self.download.request_to_download_general(url=link_etp,
                                                                              referer=self.response.url,
                                                                              host=main_url,
                                                                              _abs_path=_path_absolute,
                                                                              _id=_id, lot_num=lot_num,
                                                                              _relative_path=_dir.return_download_dir_etp())
                        lot_lst.extend(lst_files)

        lot_dict['lot'] = lot_lst
        return lot_dict
