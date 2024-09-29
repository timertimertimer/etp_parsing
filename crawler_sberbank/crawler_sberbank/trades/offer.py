import re

from ..locators.locator_trades import LocatorOffer
from ..utils.config import first_part_link, lst_exet
from bs4 import BeautifulSoup as BS
import pandas as pd
from ..utils.working_with_time import format_time
from ..utils.work_with_text_and_number import *
from ..utils.work_with_path_and_dir import GeneralFilesDir, LotFilesDir
from ..utils.download import DownloadFiles
import logging
import pathlib

logger = logging.getLogger(__name__)

class OfferParse(GeneralFilesDir):
    def __init__(self, response_):
        self.response = response_
        self.loc = LocatorOffer
        self.lot_dir = LotFilesDir

    @property
    def get_period_table(self):
        """return list with table data(periods)"""
        try:
            table = self.response.xpath(self.loc.period_table_loc).getall()
            return table
        except:
            return None

    @property
    def periods_offer_pandas(self):
        """return period table with changed header"""

        soup = BS(self.get_period_table[0], features='lxml')
        table = pd.read_html(str(soup).replace(',', '.'), header=0)
        dfs = table[0]

        # print(dfs)
        return dfs

    @property
    def periods_return(self):
        """return list with periods in dictionaries type"""
        periods = list()
        dfs = self.periods_offer_pandas
        for i in range(len(dfs)):
            start = dfs.iloc[i][0]
            end = dfs.iloc[i][1]
            price = re.sub(r'\s', '', dfs.iloc[i][2])
            period = {
                'start_date_requests': format_time(start),
                'end_date_requests': format_time(end),
                'end_date_trading': format_time(end),
                'current_price': round(float(price), 2)
            }
            periods.append(period)
        return periods

    @property
    def start_date_request(self):
        """return start date request"""
        dfs = self.periods_offer_pandas
        try:
            return format_time(dfs.iloc[0][0])
        except:
            logger.error(f'{self.response.url} :: INVALID DATA START DATE REQUEST OFFER')

    @property
    def end_date_request(self):
        """return end date request"""
        dfs = self.periods_offer_pandas
        try:
            return format_time(dfs.iloc[len(dfs) - 1][1])
        except:
            logger.error(f'{self.response.url} :: INVALID DATA END DATE REQUEST OFFER')

    @property
    def start_date_trading(self):
        """:return start date trading - the same as start date request"""
        return self.start_date_request

    @property
    def end_date_trading(self):
        """:return end date trading - the same as end date request"""
        return self.end_date_request

    @property
    def start_price(self):
        """:return start price"""
        start_price = self.response.xpath(self.loc.start_price_loc).get()
        start_price = re.sub(r'\s', '', start_price)
        pattern = re.compile(r'\d+\.\d{1,2}')
        try:
            start_price = dedent_func(BS(str(start_price), features='lxml').get_text()).strip()
            if start_price:
                return round(float(''.join(pattern.findall(start_price)[0])), 2)
        except:
            logger.error(f'{self.response.url} :: INVALID DATA START PRICE OFFER')
            return None

    @property
    def get_all_file_names(self):
        lst_names = self.response.xpath(self.loc.file_gen_loc).getall()
        return lst_names

    # working with files general
    def get_xml_data(self, xml_data: str):
        """get and return response with xml data (trading page)"""
        return xml_data

    def get_file_name_and_hash(self, *args):
        """get file name link params from xml_data string
        :*args - function  get_xml_data"""
        files_name = BS(*args, features='lxml')
        lst_file_name = files_name.find_all('filename')
        clean_name = list()
        lst_hash_links = list()
        for n in lst_file_name:
            if len(n.get_text()) > 0:
                clean_name.append(n.get_text())
                lst_hash_links.append(first_part_link + n.find_previous_sibling().get_text())
        names = clean_name
        links = lst_hash_links
        return names, links
    # end working with files general

    # download files general
    def download_general(self, id, *args):
        dir_ = GeneralFilesDir()
        load = DownloadFiles()
        lst_dict = list()
        name, link = self.get_file_name_and_hash(*args)
        for i in range(len(name)):
            relative_path_f = ''
            name_on_server = dir_.name_file_on_server(id=id, original_name=name[i])
            if pathlib.Path(name[i]).suffix in lst_exet:
                dir_.create_dir()
                relative_path_f = dir_.name_in_column_files(url=id, original_name=name[i])
                load.request_to_download(link[i], referer=self.response.url, original_name=name_on_server)
            lst_dict.append({'original_name': name[i],
                            'link': relative_path_f, 'link_etp': link[i]})
        return lst_dict
