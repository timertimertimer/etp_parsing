import logging
import pathlib
import re

from bs4 import BeautifulSoup

from general_utils.download import DownloadFiles
from general_utils.work_with_path_and_dir import FilesDir
from general_utils.working_with_time import format_time
from general_utils.working_with_url import UrlConfig
from general_utils.config import lst_exeption, image_formats, archive_formats
from general_utils.work_with_text_and_number import dedent_func
from general_utils.check_inn_email_phone import CheckIfCorrectContactInfo

logger = logging.getLogger(__name__)


class Combo:
    def __init__(self, response):
        self.response = response

    def download_general(self): ...

    def download_lot(self): ...

    @property
    def trading_id(self): ...

    @property
    def trading_link(self): ...

    @property
    def trading_number(self): ...

    @property
    def trading_type(self): ...

    @property
    def trading_form(self): ...

    @property
    def trading_org(self): ...

    @property
    def trading_org_contacts(self): ...

    @property
    def status(self): ...

    @property
    def category(self):
        ...

    @property
    def index(self):
        ...

    @property
    def address(self):
        ...

    @property
    def encumbrance(self):
        ...

    @property
    def description_encumbrance(self):
        ...

    @property
    def lot_number(self): ...

    @property
    def short_name(self): ...

    @property
    def lot_info(self): ...

    @property
    def property_information(self): ...

    @property
    def start_date_requests(self): ...

    @property
    def end_date_requests(self): ...

    @property
    def start_date_trading(self): ...

    @property
    def end_date_trading(self): ...

    @property
    def start_price(self): ...

    @property
    def min_price(self):
        ...

    @property
    def deposit(self):
        ...

    @property
    def step_price(self): ...

    @property
    def periods(self): ...

    @property
    def quantity(self):
        ...

    @property
    def unit(self):
        ...
