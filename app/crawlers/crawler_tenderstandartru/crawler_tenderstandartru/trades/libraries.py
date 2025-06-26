import re
import logging
import pathlib
import pandas as pd
from collections import deque
from numpy import float64, integer
from bs4 import BeautifulSoup as BS
from ..config import data_origin
from general_utils import (
    format_time_period,
    make_float,
    UrlConfig,
    dedent_func,
    CheckIfCorrectContactInfo,
    format_time,
)

__all__ = [
    "BS",
    "re",
    "logging",
    "CheckIfCorrectContactInfo",
    "soup",
    "UrlConfig",
    "data_origin",
    "deque",
    "dedent_func",
    "make_float",
    "format_time_period",
    "pathlib",
    "float64",
    "pd",
    "format_time",
    "integer",
]


def soup(response_):
    return BS(str(response_.body.decode("utf-8")), features="lxml")
