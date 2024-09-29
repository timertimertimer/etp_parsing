from bs4 import BeautifulSoup as BS
import re
from collections import deque
from ..utils.work_with_text_and_number import dedent_func, make_float, cut_lot_number, delete_extra_symbols
from ..utils.check_inn_email_etc import CheckIfCorrectContactInfo
from ..utils.working_with_time import format_time_auction
from ..utils.download import DownloadFiles
from ..utils.work_with_path_and_dir import GeneralFilesDir
from ..utils.working_with_url import UrlConfig
from numpy import float64
import pandas as pd
import pathlib

__all__ = ['re',
           'deque',
           'dedent_func',
           'BS',
           'soup',
           'CheckIfCorrectContactInfo',
           'format_time_auction',
           'make_float', 'float64', 'pd',
           'cut_lot_number', 'delete_extra_symbols',
           'DownloadFiles',
           'pathlib',
           'GeneralFilesDir', 'UrlConfig']


def soup(response):
    return BS(str(response.body.decode('utf-8')), features='lxml')
