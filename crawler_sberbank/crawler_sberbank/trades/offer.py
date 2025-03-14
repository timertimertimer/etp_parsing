import re

from general_utils import format_time_auction, dedent_func
from general_utils.config import image_formats
from ..utils.config import first_part_link
from bs4 import BeautifulSoup as BS

from ..utils.manage_spider import deep_get_dict
from ..utils.work_with_path_and_dir import GeneralFilesDir, LotFilesDir
from ..utils.download import DownloadFiles
import logging
import pathlib

logger = logging.getLogger(__name__)


class OfferParse(GeneralFilesDir):
    def __init__(self, data, url):
        self.url = url
        self.data = data
        self.lot_dir = LotFilesDir

    @property
    def get_periods(self):
        """return list with periods in dictionaries type"""
        try:
            data = deep_get_dict(self.data, 'BidView.BidReductionPeriod.Periods')
        except:
            return None
        periods = []
        for period in data:
            start = period['PeriodStartDate']
            end = period['PeriodEndDate']
            price = re.sub(r'\s', '', period['BidAmount'])
            period = {
                'start_date_requests': format_time_auction(start),
                'end_date_requests': format_time_auction(end),
                'end_date_trading': format_time_auction(end),
                'current_price': round(float(price), 2)
            }
            periods.append(period)
        return periods

    @property
    def start_date_request(self):
        """return start date request"""
        periods = self.get_periods
        try:
            return periods[0]['start_date_requests']
        except:
            logger.error(f'{self.url} :: INVALID DATA START DATE REQUEST OFFER')

    @property
    def end_date_request(self):
        """return end date request"""
        periods = self.get_periods
        try:
            return periods[-1]['end_date_requests']
        except:
            logger.error(f'{self.url} :: INVALID DATA END DATE REQUEST OFFER')

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
        start_price = deep_get_dict(self.data, 'BidView.Bids.BidTenderInfo.BidPrice')
        start_price = re.sub(r'\s', '', start_price)
        pattern = re.compile(r'\d+\.\d{1,2}')
        try:
            start_price = dedent_func(BS(str(start_price), features='lxml').get_text()).strip()
            if start_price:
                return round(float(''.join(pattern.findall(start_price)[0])), 2)
        except:
            logger.error(f'{self.url} :: INVALID DATA START PRICE OFFER')
            return None

    # working with files general
    def get_xml_data(self, xml_data: str):
        """get and return response with xml data (trading page)"""
        return xml_data

    def get_file_name_and_hash(self, lst_file_name):
        if isinstance(lst_file_name, dict):
            lst_file_name = [lst_file_name]
        clean_name = list()
        lst_hash_links = list()
        for n in lst_file_name:
            clean_name.append(n['filename'])
            lst_hash_links.append(first_part_link + n['fileid'])
        names = clean_name
        links = lst_hash_links
        return names, links

    # end working with files general

    def download(self, id, file):
        dir_ = GeneralFilesDir()
        load = DownloadFiles()
        lst_dict = list()
        name, link = self.get_file_name_and_hash(file)
        for i in range(len(name)):
            relative_path_f = ''
            name_on_server = dir_.name_file_on_server(id=id, original_name=name[i])
            if pathlib.Path(name[i]).suffix in image_formats:
                dir_.create_dir()
                relative_path_f = dir_.name_in_column_files(url=id, original_name=name[i])
                load.request_to_download(link[i], referer=self.url, original_name=name_on_server)
            lst_dict.append({'original_name': name[i],
                             'link': relative_path_f, 'link_etp': link[i]})
        return lst_dict
