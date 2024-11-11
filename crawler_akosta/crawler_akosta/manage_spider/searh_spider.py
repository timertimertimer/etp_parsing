from os import environ, path, chdir, getcwd
from pathlib import PurePosixPath

import pandas as pd
from scrapy.utils.conf import closest_scrapy_cfg

from crawler_akosta.utils.config import search_link
from crawler_akosta.utils.working_with_url import UrlConfig

proj_root = closest_scrapy_cfg()
home_dir = environ['HOME']
data_file = 'data_parse.csv'
_dir_with_project = path.join(home_dir, PurePosixPath(proj_root).parent) + '/'
_dir_with_csv = PurePosixPath(proj_root).parent.name + '/'
full_path = _dir_with_project + _dir_with_csv + data_file


class SearchTrade:
    def __init__(self, response_):
        self.response = response_
        self.url = UrlConfig()

    @staticmethod
    def return_lst_unique_data() -> list:
        """
        read csv file and
        return list of trading id
        """
        data_set = set()
        if not path.exists(full_path):
            return []
        df = pd.read_csv(full_path, delimiter=',', header=None)
        for i in range(len(df)):
            data_set.add(df.iloc[i][1])
        return list(data_set)

    def return_search_url(self, param):
        """ concatenate url with param and return it """
        _param = {'keyword': param}
        complete = self.url.return_url_param(search_link, _param)
        return complete
