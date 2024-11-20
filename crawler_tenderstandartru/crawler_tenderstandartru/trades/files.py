import pathlib

from icecream import ic

from .libraries import *

from ..utils.config import lst_exet, lst_exet_archive, path_absolute, path_relative

logger = logging.getLogger(__name__)


class GeneralFiles:

    def __init__(self, response_):
        self.response = response_
        self.soup = soup(self.response)
        self._dir = GeneralFilesDir(path_absolute=path_absolute['tenderstandart'], path_relative=path_relative['tenderstandart'])
        self.url = UrlConfig()

    def section_general_docs(self):
        """ return section with general docs """
        _div = self.soup.find('div', id='divDocuments')
        if _div:
            return _div
        else:
            logger.error(
                f'{self.response.url} :: ERROR function class GeneralFiles {self.section_general_docs.__name__}')

    def find_general_files(self):
        """ find and return general fiels in tuple packed in list(deque) """
        if table := self.section_general_docs():
            general = list()
            a_tag = table.find_all(href=re.compile('/Document/.+/.+'))
            for a in a_tag:
                link = a.get('href')
                link = re.sub(r'/$', '', data_origin['tenderstandart']) + link
                name = dedent_func(a.get_text())
                general.append((name, link))
            return deque(general)
        return list()

    def download_files_general(self, _id):
        """ itterate throught list with file info(name and link) """
        if lst := self.find_general_files():
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
        self.soup = soup(self.response)
        self._dir = GeneralFilesDir(path_absolute=path_absolute['tenderstandart'], path_relative=path_relative['tenderstandart'])
        self.url = UrlConfig()

    def section_doc_lots(self):
        """ return div with lots documents """
        _div = self.soup.find('div', id='divDocuments')
        if _div:
            return _div
        else:
            logger.error(
                f'{self.response.url} :: ERROR function class GeneralFiles {self.section_doc_lots.__name__}')

    def images_on_lot_page(self) -> list or None:
        """ fetch info from section on lot page """
        _div = self.soup.find('div', class_='links picture-links')
        if _div:
            lot = list()
            a_tag = _div.find_all(href=re.compile('/Picture/.+/.+'))
            for a in a_tag:
                link = a.get('href')
                link = re.sub(r'/$', '', data_origin['tenderstandart']) + link
                name = pathlib.Path(str(link)).stem + '.jpg'
                lot.append((name, link))
            if len(lot) > 0:
                return lot

    def find_lot_files(self):
        """ find and return general fiels in tuple packed in list(deque) """
        lot = list()
        if table := self.section_doc_lots():
            a_tag = table.find_all(href=re.compile('/Document/.+/.+'))
            for a in a_tag:
                link = a.get('href')
                link = re.sub(r'/$', '', data_origin['tenderstandart']) + link
                name = dedent_func(a.get_text())
                lot.append((name, link))
        if img := self.images_on_lot_page():
            lot.extend(img)
        return deque(lot)
        return list()

    def download_files_lot(self, _id, lot_number):
        """ itterate throught list with file info(name and link) """
        if lst := self.find_lot_files():
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
                    name_on_server = self._dir.name_file_lot_on_server(_id=_id, lot_num=''.join(lot_number),
                                                                       original_name=file_name_server)
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
                    name_on_server = self._dir.name_file_lot_on_server(_id=_id, lot_num=''.join(lot_number),
                                                                       original_name=file_name_server)
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
