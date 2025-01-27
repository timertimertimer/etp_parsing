import logging
import pathlib
import re

from bs4 import BeautifulSoup

from general_utils import DownloadFiles, FilesDir, format_time, UrlConfig, dedent_func, CheckIfCorrectContactInfo
from general_utils.config import lst_exeption, lst_exet, lst_exet_archive

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
    def trading_org_inn(self): ...

    @property
    def trading_org_contacts(self): ...

    @property
    def msg_number(self): ...

    @property
    def case_number(self): ...

    @property
    def debtor_inn(self): ...

    @property
    def address(self): ...

    @property
    def region(self): ...

    @property
    def arbit_manager(self): ...

    @property
    def arbit_manager_inn(self): ...

    @property
    def arbit_manager_org(self): ...

    @property
    def status(self): ...

    @property
    def lot_id(self): ...

    @property
    def lot_link(self): ...

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
    def step_price(self): ...

    @property
    def periods(self): ...
