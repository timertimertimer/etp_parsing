from bs4 import BeautifulSoup as BS
import re
import logging
from ..utils.check_inn_email_etc import CheckIfCorrectContactInfo
from ..utils.working_with_time import return_timestamp_moskow, format_time_period, format_time_auction, format_time
from ..utils.working_with_url import UrlConfig
from ..utils.config import data_origin
from collections import deque
from ..utils.work_with_text_and_number import dedent_func, make_float, cut_lot_number, delete_extra_symbols
from ..utils.work_with_path_and_dir import GeneralFilesDir
from ..utils.download import DownloadFiles
import pathlib
from numpy import float64, integer
import pandas as pd


__all__ = ['BS', 're', 'logging', 'CheckIfCorrectContactInfo', 'soup',
           'return_timestamp_moskow', 'UrlConfig', 'data_origin', 'deque', 'dedent_func',
           'make_float', 'format_time_period', 'format_time_auction',
           'cut_lot_number', 'delete_extra_symbols',
           'GeneralFilesDir', 'DownloadFiles', 'pathlib', 'float64', 'pd', 'format_time', 'integer'

           ]


def soup(response_):
    return BS(str(response_.body.decode('utf-8')), features='lxml')
