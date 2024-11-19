import logging
import pathlib
import re

from bs4 import BeautifulSoup as BS

from ..utils.config import lst_exeption, lst_exet_archive, lst_exet
from ..utils.config import path_relative, path_absolute
from ..utils.download import DownloadFiles
from ..utils.work_with_path_and_dir import GeneralFilesDir
from ..utils.work_with_text_and_number import dedent_func
from ..utils.working_with_url import UrlConfig

logger = logging.getLogger(__name__)


class DocumentGeneral:
    path_rel = path_relative['betwobe']
    path_abs = path_absolute['betwobe']

    def __init__(self, resposne_):
        self.response = resposne_
        self.url = UrlConfig()
        self._dir = GeneralFilesDir(path_relative=self.path_rel, path_absolute=self.path_abs)
        self.soup = BS(str(self.response.body.decode('utf-8')).replace('&lt;', '<').replace('&gt;', '>'),
                       features='lxml')

    def check_if_docs_general(self) -> list or None:
        """ check if docs general exists """
        try:
            doc_td = self.soup.find('td', string=re.compile(r'Документация по процедуре', re.IGNORECASE))
            if doc_td := doc_td.findNext('td'):
                if divs := doc_td.find_all('div', class_='file_download_link'):
                    return divs
        except Exception as e:
            logger.error(f'{self.response.url} :: INVALID DATA GENERAL DOCS <TD> {e}')
            return None

    def get_name_and_links_doc_gen(self) -> list or None:
        """ :return list  with tuple( 2 elements - original name and link inside """
        try:
            lst_docs = list()
            if data := self.check_if_docs_general():
                for i in data:
                    original_name = dedent_func(i.get_text().strip().replace('. ', '.'))
                    original_name = re.sub(r'\(\d+.+\)$', '', original_name).strip()
                    original_name = re.sub(r'Скачать\s+файл', '', original_name).strip()
                    link_file = i.find('a').get('href')
                    lst_docs.append((original_name, link_file))
                return lst_docs
        except Exception as ex:
            logger.error(f'{self.response.url} :: ERROR GETTING LINKS AND NAMES GENERAL FILES {ex}')
            return None

    def download_general(self, _id=None):
        """ add and download general(if archives or images) """
        try:
            download = DownloadFiles()
            general_dict = dict()
            general_lst = list()
            _path_relative = ''
            if data := self.get_name_and_links_doc_gen():
                for d in data:
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
                            _path_relative = self._dir.name_in_column_files(name_on_server, )
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
                return {'general': list()}
        except Exception as ex:
            logger.error(f'{self.response.url} :: INVALID DATA GENERAL DOCS {ex}', exc_info=True)

    def lst_files_names(self, **kwargs):
        """ get all data files general and return list with only names of files """
        try:
            original_names = [pathlib.Path(n.get('original_name').split('/')[0]).stem for n in kwargs.get('general')]
            return original_names
        except Exception as e:
            logger.error(f'{self.response.url} :{e}: ERROR into lst_files_name', exc_info=True)
            return list

class DocumentLot:
    path_rel = path_relative['betwobe']
    path_abs = path_absolute['betwobe']

    def __init__(self, resposne_):
        self.response = resposne_
        self.url = UrlConfig()
        self._dir = GeneralFilesDir(path_relative=self.path_rel, path_absolute=self.path_abs)
        self.soup = BS(str(self.response.body.decode('utf-8')).replace('&lt;', '<').replace('&gt;', '>'),
                       features='lxml')

    def check_if_docs_lots(self) -> list or None:
        """ check if docs lots exists """
        try:
            doc_td = self.soup.find('td', string=re.compile(r'Документация по лоту', re.IGNORECASE))
            if doc_td := doc_td.findNext('td'):
                if divs := doc_td.find_all('div', class_='file_download_link'):
                    return divs
        except Exception as e:
            logger.error(f'{self.response.url} :: INVALID DATA LOT DOCS <TD> {e}')
            return None

    def get_name_and_links_doc_lot(self) -> list or None:
        """ :return list  with tuple( 2 elements - original name and link inside """
        try:
            lst_docs = list()
            if data := self.check_if_docs_lots():
                for i in data:
                    original_name = dedent_func(i.get_text().strip().replace('. ', '.'))
                    original_name = re.sub(r'\(\d+.+\)$', '', original_name).strip()
                    original_name = re.sub(r'Скачать\s+файл', '', original_name).strip()
                    link_file = i.find('a').get('href')
                    lst_docs.append((original_name, link_file))
                return lst_docs
        except Exception as ex:
            logger.error(f'{self.response.url} :: ERROR GETTING LINKS AND NAMES LOT FILES {ex}')
            return None

    def download_lot_files(self, name_general_lst=list, _id=None, lot_number=None):
        """ download or just write in table DB files of lot """
        try:
            download = DownloadFiles()
            lot_dict = dict()
            lot_list = list()
            _path_relative = ''
            if data := self.get_name_and_links_doc_lot():
                for d in data:
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
                            lot_file = pathlib.Path(d[0]).stem
                            if lot_file not in name_general_lst:
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
