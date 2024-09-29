import logging
import pathlib
import re
from difflib import SequenceMatcher
import pandas as pd
from bs4 import BeautifulSoup as BS
from bs4 import CData

from .finished_section import MAIN_URL
from ..utils.config import lst_exeption, lst_exet, lst_exet_archive, path_relative, path_absolute
from ..utils.download import DownloadFiles
from ..utils.work_with_path_and_dir import GeneralFilesDir
from ..utils.working_with_url import UrlConfig

logger = logging.getLogger(__name__)


class DocumentGeneral:
    path_rel = path_relative['torgi_gov_bankrot']
    path_abs = path_absolute['torgi_gov_bankrot']
    path_rel_gov = path_relative['torgi_gov_government']
    path_abs_gov = path_absolute['torgi_gov_government']

    def __init__(self, resposne_):
        self.response = resposne_
        self.url = UrlConfig()
        self._dir = GeneralFilesDir(path_relative=self.path_rel, path_absolute=self.path_abs)
        self._dir2 = GeneralFilesDir(path_relative=self.path_rel_gov, path_absolute=self.path_abs_gov)
        self.soup = BS(str(self.response.body.decode('utf-8')).replace('&lt;', '<').replace('&gt;', '>'),
                       features='lxml')

    def download_general(self, lst_with_files: list, spider_name=None, _id=None, referer=None):
        """ add and download general(if archives or images) """
        try:
            download = DownloadFiles()
            general_dict = dict()
            general_lst = list()
            _path_relative = ''
            if spider_name == 'torgi_government':
                _dir = self._dir2
            else:
                _dir = self._dir
            if len(lst_with_files) > 0:
                data = lst_with_files
                for d in data:
                    # d[0] -> file name d[1] -> file link
                    if not any(ele in d[1] for ele in lst_exeption):
                        if pathlib.Path(d[1]).suffix in lst_exet:
                            _dir.create_dir()
                            if len(d[1]) > 85:
                                file_name_server = d[1][:30] + '_' + d[1][-35::1]
                            else:
                                file_name_server = d[1]
                            name_on_server = _dir.name_file_on_server(_id=_id, original_name=file_name_server)
                            _path_absolute = _dir.return_absolute_path(name_on_server)
                            download.request_to_download_general(url=d[0],
                                                                 referer=self.response.url,
                                                                 _abs_path=_path_absolute)
                            _path_relative = _dir.name_in_column_files(name_on_server, )
                            general_lst.append(
                                {'original_name': d[1], 'link': _path_relative,
                                 'link_etp': self.url.parse_url(d[0])})
                        # FILES INSIDE ARCHIVE
                        elif pathlib.Path(d[1]).suffix in lst_exet_archive:
                            if len(d[1]) > 75:
                                file_name_server = d[1][:30] + '_' + d[1][-35::1]
                            else:
                                file_name_server = d[1]
                            name_on_server = _dir.name_file_on_server(_id=_id, original_name=file_name_server)
                            _path_absolute = _dir.return_absolute_path(name_on_server)
                            _dir.create_dir()
                            lst_files = download.request_to_download_general(url=d[0],
                                                                             referer=referer,
                                                                             _abs_path=_path_absolute,
                                                                             _id=_id,
                                                                             _relative_path=_dir.return_download_dir_etp())
                            general_lst.extend(lst_files)
                        else:
                            general_lst.append(
                                {'original_name': d[1], 'link': '',
                                 'link_etp': self.url.parse_url(d[0])})
                general_dict['general'] = general_lst
                return general_lst
            else:
                return general_lst
        except Exception as ex:
            logger.error(f'{self.response.url} :: INVALID DATA GENERAL DOCS {ex}', exc_info=True)


class DownloadPage:

    def __init__(self, response_):
        self.response = response_
        self.url = UrlConfig()
        self.soup = BS(
            str(self.response.body.decode('utf-8')).replace('&lt;', '<').replace('&gt;', '>').replace('&amp;', '&'),
            features='lxml')

    def get_documents_table(self, url_lot):
        """ find and return table with documents """
        try:
            #table = self.soup.find('table', class_='list')
            table1 = None
            table2 = self.soup.find('p', string=re.compile('Размер файла,?', re.IGNORECASE))
            if table2:
                return table2.find_parent('table')
            elif table1:
                return BS(str(table1), features='lxml')
            else:
                logger.error(f'{url_lot} :: Table with documents not found')
                return None
        except Exception as ex:
            logger.error(f'{url_lot} :{ex}: INVALID DATA DOCUMENT TABLE', exc_info=True)
            with open(f'get_documents_table.txt', 'w') as f:
                f.write(self.response.text)
            return None

    def get_all_files_links(self, url_lot):
        """ fetch and return list with links """
        try:
            if table := self.get_documents_table(url_lot):
                list_links = list()
                tbody = table.find('tbody')
                for tr in tbody.find_all('tr'):
                    href = tr.find_all('td')[0].find('a').get('href')
                    search_str = re.findall(r'\?wicket.+|resources.+', href)
                    href = MAIN_URL + ''.join(search_str)
                    list_links.append(href)
                return list_links
        except Exception as ex:
            logger.error(f'{self.response.url} :{ex}: ERROR GETTING DOCUMENTS LINKS', exc_info=True)
            return None

    def return_comlete_doc_table(self, url_lot):
        """ return only table with two(2) columns  """
        try:
            if table := self.get_documents_table(url_lot):
                df = pd.read_html(str(table))
                df = df[0].rename(columns={df[0].columns[0]: 'Links'})
                df = df.rename(columns={'Имя файла': 'File name'})
                df['Links'] = self.get_all_files_links(url_lot)
                df = df[['Links', 'File name']]
                return df
            else:
                return list()
        except Exception as ex:
            logger.error(f'{url_lot} :{ex}: ERROR PANDAS TABLE')

    def return_file_data(self, url_lot) -> tuple or None:
        """ return tuple with files links and files names """
        try:
            # pandas table
            data = list()
            pd_table = self.return_comlete_doc_table(url_lot)
            for index, row in pd_table.iterrows():
                link = row['Links']
                name = row['File name']
                data.append((link, name))
            if len(data) > 0:
                return data
        except Exception as ex:
            logger.error(f'{url_lot} :: ERROR FILES TUPLE - {ex}')
            return None

    def get_link_from_doc_view(self, trading_link, file_name):
        """ return link of file with .doc or doxc extension """
        try:
            if _a := self.soup.find('a', string=re.compile('Сохранить файл', re.IGNORECASE)):
                href = _a.get('href')
                search_str = re.findall(r'resources.+', href)
                href = MAIN_URL + ''.join(search_str)
                return href
            elif span := self.soup.find('span', string=str(file_name)):
                href = span.parent.parent.find('a').get('href')
                return MAIN_URL + href
        except Exception as ex:
            with open('error_page_doc.txt', 'w') as f:
                f.write(self.response.text)
            logger.error(f'{self.response.url} :{ex}: ERRROR FILE on {trading_link}')
            return list()

    def get_link_back_to_files(self):
        """ on page document view thre is link to go back to files """
        try:
            _a = self.soup.find('a', string=re.compile('Вернуться назад'))
            href = _a.get('href')
            search_str = re.findall(r'\?wicket.+', href)
            href = MAIN_URL + ''.join(search_str)
            return href
        except Exception as ex:
            logger.error(f'{self.response.url} :{ex}: ERRROR BUTTON GO BACK to files')
            return None

    def get_redirect_link_to_doc(self, trading_link):
        """ return link to view .doc or .doxc files """
        try:
            soup = BS(str(self.response.text), features='html.parser')
            for cd in soup.findAll(text=True):
                if isinstance(cd, CData):
                    return MAIN_URL + cd
        except Exception as e:
            logger.error(f'{self.response.url} :{trading_link}: ERROR LINK REDIRECT {e}')

    def change_sequence_of_query(self, url):
        """ change_sequence_of_query: second param take fisrt place and second vice versa """
        try:
            param_query = self.url.return_query_dict(url)
            if len(param_query.keys()) == 2:
                first = list(param_query.keys())[0]
                second = list(param_query.keys())[1]
                first_param = ''.join(param_query[first])
                second_param = ''.join(param_query[second])
                complete = f'?{second}={second_param}&{first}={first_param}'
                my_param = {'section', 'id'}
                all_param = {first, second}
                if my_param.issubset(all_param):
                    full_url = self.url.return_parsed_url(url)
                    return full_url.scheme + '://' + full_url.netloc + full_url.path + complete

        except Exception as ex:
            logger.error(f'{self.response.url} :{ex}: INVALID DATA DURRING CHANGE QUERY SEQUENCE', exc_info=True)

    def get_links_of_docs_2(self, file_name):
        """ get links to file after return from document view page """
        try:
            span = self.soup.find('span', string=str(file_name))
            href = span.parent.parent.find('a').get('href')
            return MAIN_URL + href
        except Exception as ex:
            logger.error(f'{self.response.url} :{ex}: INVALID DATA GETTING DOCUMENT FILE AFTER RETURN ')

    def manage_download_files(self, lst_files):
        """ sort for downloading files """
        return {'general': lst_files}

    def compare_links_to_download(self, dct: dict, lst: list):
        """ compare links from db with links in list to download(or just save)
            :arg dct -> dict from db with files
            :arg lst -> list with tuples(with link and name of file)
        """
        try:
            new_list = sorted([l[1] for l in lst])
            lst_dct = sorted([g['original_name'] for g in dct['general']])
            match = SequenceMatcher(a=new_list, b=lst_dct)
            if match.ratio() == 1.0:
                return round(float(1), 2)
            else:
                return match.ratio()
        except Exception as e:
            logger.error(f'{e}', exc_info=True)
            return round(float(0), 2)
