import logging
import pathlib
import re
from bs4 import BeautifulSoup

from general_utils import dedent_func, CheckIfCorrectContactInfo, format_time_auction, get_region
from general_utils.config import lst_exeption, lst_exet, lst_exet_archive
from ..utils.download import DownloadFiles
from ..utils.work_with_path_and_dir import GeneralFilesDir
from ..locators.trade_locator import TradeLocator

logger = logging.getLogger(__name__)


class Combo:
    addresses = dict()

    def __init__(self, response):
        self.response = response
        self.loc = TradeLocator
        self.general_dir = GeneralFilesDir()

    def parse_status(self, status: str):
        active = (
            "Торги в стадии приема заявок",
            "Прием заявок",
            "Проводится приём заявок",
            "Идут торги",
        )
        pending = ("Объявлены торги", "Имущество не продано. Определяется дата новых торгов")
        ended = (
            "Проведена инвентаризация",
            "Проведена оценка",
            "Имущество реализовано",
            "Имущество не реализовано",
            "Приём заявок завершен",
        )
        status = status.strip()
        try:
            if status in active:
                return "active"
            elif status in pending:
                return "pending"
            elif status in ended:
                return "ended"
            else:
                return None
        except:
            return None

    @property
    def trading_id(self):
        _id = re.findall(r"\d+", str(self.trading_link))
        return "".join(_id)

    @property
    def trading_link(self):
        return self.response.url

    @property
    def trading_type_and_form(self):
        try:
            type_, form = self.response.xpath(self.loc.trading_type_and_form_loc).get().strip().lower().split("/")
        except Exception as e:
            return None, None
        if "закрыт" in form:
            form = "closed"
        elif "открыт" in form:
            form = "open"
        else:
            ...
        if "аукцион" in type_:
            type_ = "auction"
        elif "конкурс" in type_:
            type_ = "competition"
        elif "предложение" in type_:
            type_ = "offer"
        else:
            ...
        return type_, form

    @property
    def trading_org(self):
        try:
            org = BeautifulSoup(self.response.xpath(self.loc.trading_org_loc).get(), "lxml").get_text().strip()
            return "".join(re.sub(r"\s+", " ", org))
        except:
            logger.warning(f"{self.response.url} :: INVALID DATA ORGANIZER", exc_info=True)

    @property
    def trading_org_inn(self):
        return

    @property
    def trading_org_contacts(self):
        return

    @property
    def msg_number(self):
        return

    @property
    def case_number(self):
        case = dedent_func(BeautifulSoup(self.response.xpath(self.loc.case_number_loc).get(), "lxml").get_text())
        if case:
            return CheckIfCorrectContactInfo.check_case_number(case)
        else:
            return

    @property
    def debitor_inn(self):
        inn = self.response.xpath(self.loc.debtor_inn_loc).get()
        if not inn:
            return
        trade_inn = dedent_func(inn)
        pattern = re.compile(r"\d{10,12}")
        return "".join(pattern.findall(trade_inn))

    def get_address(self):
        address = BeautifulSoup(self.response.xpath(self.loc.address_loc).get(), "lxml").get_text(strip=True)
        if address not in self.addresses:
            self.addresses[address] = get_region(address)
        return address, self.addresses[address]

    @property
    def arbit_manager(self):
        try:
            td_org = dedent_func(
                BeautifulSoup(self.response.xpath(self.loc.arbit_manager_loc).get(), "lxml").get_text()
            )
            if td_org != "None":
                return "".join(re.sub(r"\s+", " ", td_org))
        except:
            logger.warning(f"{self.response.url} :: INVALID DATA ARBITR NAME")

    @property
    def arbit_manager_inn(self):
        return

    @property
    def arbit_manager_org(self):
        try:
            td_company = dedent_func(
                BeautifulSoup(self.response.xpath(self.loc.arbit_manager_org_loc).get(), "lxml").get_text()
            )
            if td_company != "None":
                if "(" in td_company:
                    td_company = "".join(
                        [x if len(td_company) > 0 else None for x in re.split(r"\(", td_company, maxsplit=1)[0]]
                    )
                return "".join(dedent_func(td_company))
        except:
            logger.warning(f"{self.response.url} :: INVALID DATA ARBITR COMPANY")

    @property
    def lot_id(self):
        return

    @property
    def lot_link(self):
        return self.trading_link

    @property
    def lot_number(self):
        match = re.search(
            r"лота №(\d+) ",
            BeautifulSoup(self.response.xpath(self.loc.lot_number_loc).get(), "lxml").get_text().strip().lower(),
        )
        if match:
            return match.group(1)
        logger.warning(f"{self.response.url} :: LOT WITHOUT NUMBER")

    @property
    def lot_info(self):
        total_info = []
        for info in self.response.xpath(self.loc.lot_info_loc).getall():
            soup = BeautifulSoup(info, "lxml")
            total_info.append(soup.get_text())
        return dedent_func("\n".join(total_info))

    @property
    def property_information(self):
        return

    @property
    def start_date_requests(self):
        return format_time_auction(self.response.xpath(self.loc.start_date_requests_loc).get())

    @property
    def end_date_requests(self):
        return format_time_auction(self.response.xpath(self.loc.end_date_requests_loc).get())

    def start_and_end_dates_trading(self):
        date_interval = (
            BeautifulSoup(self.response.xpath(self.loc.start_and_end_dates_trading_loc).get(), "lxml")
            .get_text()
            .strip()
        )
        parts = date_interval.split("-")
        if len(parts) == 2:
            start_date, end_date = parts
        else:
            start_date, end_date = parts[0], None
        return format_time_auction(start_date), format_time_auction(end_date) if end_date else None

    @property
    def start_date_trading(self):
        return self.start_and_end_dates_trading()[0]

    @property
    def end_date_trading(self):
        return self.start_and_end_dates_trading()[1]

    @property
    def start_price(self):
        try:
            p = self.response.xpath(self.loc.start_price_loc).get().strip()
            if p:
                p = re.sub(r"\s", "", dedent_func(p).replace(",", "."))
                p = "".join([x for x in p if x.isdigit() or x == "."])
                if len(p) > 0:
                    return round(float(p), 2)
        except Exception as e:
            logger.error(f"{self.response.url} :: INVALID START PRICE\n{e}")

    @property
    def step_price(self):
        return

    @property
    def periods(self):
        return

    def download_general(self):
        dir = self.general_dir
        download = DownloadFiles()
        general_lst = list()
        links = self.response.xpath(self.loc.general_files_loc).getall()
        for link in links:
            a = BeautifulSoup(str(link), features="lxml").find("a")
            name = a.get_text().strip()
            link = a.get("href")
            if not any(ele in name for ele in lst_exeption):
                if pathlib.Path(name).suffix in lst_exet:
                    dir.create_dir()
                    if len(name) > 75:
                        file_name_server = name[0][:30] + "_" + name[0][-35::1]
                    else:
                        file_name_server = name[0]
                    name_on_server = dir.name_file_on_server(self.trading_id, file_name_server)
                    _path_absolute = dir.return_absolute_path(name_on_server)
                    download.request_to_download_general(url=link, referer=self.response.url, _abs_path=_path_absolute)
                    _path_relative = dir.name_in_column_files(
                        name_on_server,
                    )
                    general_lst.append(
                        {"original_name": name, "link": _path_relative, "link_etp": self.url.parse_url(link)}
                    )
                    # FILES INSIDE ARCHIVE
                elif pathlib.Path(name).suffix in lst_exet_archive:
                    if len(name) > 75:
                        file_name_server = name[:30] + "_" + name[-35::1]
                    else:
                        file_name_server = name
                    name_on_server = dir.name_file_on_server(self.trading_id, file_name_server)
                    _path_absolute = dir.return_absolute_path(name_on_server)
                    self.general_dir.create_dir()
                    lst_files = download.request_to_download_general(
                        url=link,
                        referer=self.response.url,
                        _abs_path=_path_absolute,
                        _id=self.trading_id,
                        _relative_path=dir.return_download_dir_etp(),
                    )
                    general_lst.extend(lst_files)
                else:
                    general_lst.append({"original_name": name, "link": "", "link_etp": link})
        return general_lst

    def download_lot(self):
        return []
