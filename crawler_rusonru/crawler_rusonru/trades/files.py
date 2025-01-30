from bs4 import BeautifulSoup as BS

from general_utils.config import lst_exeption, lst_exet, lst_exet_archive
from ..locators.locators_doc import LocatorDoc
import logging
import pathlib
from ..utils.config import path_relative, path_absolute
from ..utils.work_with_text_and_number import dedent_func
from ..utils.work_with_path_and_dir import GeneralFilesDir
from ..utils.download import DownloadFiles
from ..utils.working_with_url import UrlConfig

logger = logging.getLogger(__name__)


class DocumentGeneral:

    def __init__(self, resposne_, domain):
        self.response = resposne_
        self.url = UrlConfig()
        self.loc = LocatorDoc
        self.path_rel = path_relative[domain]
        self.path_abs = path_absolute[domain]
        self._dir = GeneralFilesDir(path_relative=self.path_rel, path_absolute=self.path_abs)
        self.soup = BS(str(self.response.body.decode('utf-8')).replace('&lt;', '<').replace('&gt;', '>'),
                       features='lxml')

    def get_doc_table(self):
        """ :return document block bs4 """
        try:
            table_doc = self.response.xpath(self.loc.document_general_loc).get()
            if table_doc:
                table_doc = BS(str(table_doc), features='lxml')
                return table_doc
        except Exception as ex:
            logger.error(f'{self.response.url} :: DURRING GETTING DOC TABLE ERROR HAD BEEN APEARED {ex}')

    def get_name_links_doc_gen(self) -> list:
        """ :return list  with tuple( 2 elements - original name and link inside """
        block = self.get_doc_table()
        lst_docs = list()
        if block:
            # find all tag <a> with documents
            all_a = block.find_all('a')
            for a in all_a:
                original_name = dedent_func(a.get_text().strip().replace('. ', '.'))
                link_file = a.get('href')
                lst_docs.append((original_name, link_file))
            return lst_docs
        else:
            return list()

    def download_general(self, _id=None):
        """ add and download general(if archives or images) """
        try:
            download = DownloadFiles()
            general_dict = dict()
            general_lst = list()
            _path_relative = ''
            if self.get_name_links_doc_gen():
                for d in self.get_name_links_doc_gen():
                    # d[0] -> file name d[1] -> file link
                    if not any(ele in d[0] for ele in lst_exeption):
                        if pathlib.Path(d[0]).suffix in lst_exet:
                            self._dir.create_dir()
                            if len(d[0]) > 75:
                                file_name_server = d[0][:30] + '_' + d[0][-35::1]
                            else:
                                file_name_server = d[0]
                            name_on_server = self._dir.name_file_on_server(_id=_id, original_name=file_name_server)
                            _path_absolute = self._dir.return_absolute_path(name_on_server)
                            download.request_to_download_general(url=d[1],
                                                                 referer=self.response.url,
                                                                 _abs_path=_path_absolute)
                            _path_relative = self._dir.name_in_column_files(name_on_server)
                            general_lst.append(
                                {'original_name': d[0], 'link': _path_relative,
                                 'link_etp': self.url.parse_url(d[1])})
                        # FILES INSIDE ARCHIVE
                        elif pathlib.Path(d[0]).suffix in lst_exet_archive:
                            if len(d[0]) > 75:
                                file_name_server = d[0][:30] + '_' + d[0][-35::1]
                            else:
                                file_name_server = d[0]
                            name_on_server = self._dir.name_file_on_server(_id=_id, original_name=file_name_server)
                            _path_absolute = self._dir.return_absolute_path(name_on_server)
                            self._dir.create_dir()
                            lst_files = download.request_to_download_general(url=d[1],
                                                                             referer=self.response.url,
                                                                             _abs_path=_path_absolute,
                                                                             _id=_id,
                                                                             _relative_path=self._dir.return_download_dir_etp())
                            general_lst.extend(lst_files)
                        else:
                            general_lst.append(
                                {'original_name': d[0], 'link': '',
                                 'link_etp': self.url.parse_url(d[1])})
                general_dict['general'] = general_lst
                return general_dict
            else:
                return {'general': dict()}
        except Exception as ex:
            logger.error(f'{self.response.url} :: INVALID DATA GENERAL DOCS {ex}', exc_info=True)


class DocumentLot:

    def __init__(self, resposne_, domain):
        self.response = resposne_
        self.url = UrlConfig()
        self.loc = LocatorDoc
        self.path_rel = path_relative[domain]
        self.path_abs = path_absolute[domain]
        self._dir = GeneralFilesDir(path_relative=self.path_rel, path_absolute=self.path_abs)
        self.soup = BS(str(self.response.body.decode('utf-8')).replace('&lt;', '<').replace('&gt;', '>'),
                       features='lxml')

    def get_lot_files(self, table: str):
        """ :arg table -> text representation of lot table
            :return list with original names and links
        """
        try:
            if table:
                soup = BS(str(table), features='lxml')
                files = soup.find_all('a', class_="file_link")
                if len(files) > 0:
                    lst_links = list()
                    for f in files:
                        lst_links.append((f.get_text(),f.get('href')))
                    return lst_links
                else:
                    return list()
        except Exception as ex:
            logger.error(f'{self.response.url} :: INVALID DATA get_lot_files {ex}', exc_info=True)

    def download_lot_files(self, table, _id=None, lot_number=None):
        """ download or just write in table DB files of lot """
        try:
            download = DownloadFiles()
            lot_dict = dict()
            lot_list = list()
            _path_relative = ''
            if self.get_lot_files(table):
                for d in self.get_lot_files(table):
                    # d[0] -> file name d[1] -> file link
                    if not any(ele in d[0] for ele in lst_exeption):
                        if pathlib.Path(d[0]).suffix in lst_exet:
                            self._dir.create_dir()
                            if len(d[0]) > 75:
                                file_name_server = d[0][:30] + '_' + d[0][-35::1]
                            else:
                                file_name_server = d[0]
                            name_on_server = self._dir.name_file_lot_on_server(_id=_id,
                                                                               lot_num=lot_number,
                                                                               original_name=file_name_server)
                            _path_absolute = self._dir.return_absolute_path(name_on_server)
                            download.request_to_download_general(url=d[1],
                                                                 referer=self.response.url,
                                                                 _abs_path=_path_absolute)
                            _path_relative = self._dir.name_in_column_files(name_on_server)
                            lot_list.append(
                                {'original_name': d[0], 'link': _path_relative,
                                 'link_etp': self.url.parse_url(d[1])})
                        # FILES INSIDE ARCHIVE
                        elif pathlib.Path(d[0]).suffix in lst_exet_archive:
                            if len(d[0]) > 75:
                                file_name_server = d[0][:30] + '_' + d[0][-35::1]
                            else:
                                file_name_server = d[0]
                            name_on_server = self._dir.name_file_lot_on_server(_id=_id,
                                                                               lot_num=lot_number,
                                                                               original_name=file_name_server)
                            _path_absolute = self._dir.return_absolute_path(name_on_server)
                            self._dir.create_dir()
                            lst_files = download.request_to_download_general(url=d[1],
                                                                             referer=self.response.url,
                                                                             _abs_path=_path_absolute,
                                                                             _id=_id,
                                                                             _relative_path=self._dir.return_download_dir_etp())
                            lot_list.extend(lst_files)
                        else:
                            lot_list.append(
                                {'original_name': d[0], 'link': '',
                                 'link_etp': self.url.parse_url(d[1])})
                lot_dict['lot'] = lot_list
                return lot_dict
            else:
                return {'lot': list()}
        except Exception as ex:
            logger.error(f'{self.response.url} :: INVALID DATA GENERAL DOCS {ex}', exc_info=True)

