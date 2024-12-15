import logging
import pathlib
import re

from bs4 import BeautifulSoup

from ..utils.download import DownloadFiles
from ..utils.work_with_path_and_dir import GeneralFilesDir
from ..utils.working_with_time import format_time
from ..utils.working_with_url import UrlConfig
from ..utils.config import lst_exeption, lst_exet, lst_exet_archive
from ..utils.work_with_text_and_number import dedent_func
from ..utils.check_inn_email_phone import CheckIfCorrectContactInfo

logger = logging.getLogger(__name__)


class Combo:
    def __init__(self, response):
        self.response = response
        self.check = CheckIfCorrectContactInfo()
        self.url = UrlConfig()
        self.general_dir = GeneralFilesDir()

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
