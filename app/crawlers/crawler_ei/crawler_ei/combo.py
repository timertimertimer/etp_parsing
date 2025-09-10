from bs4 import BeautifulSoup

from app.db.models import DownloadData
from app.utils import logger, Contacts, DateTimeHelper, make_float


class Combo:
    def __init__(self, lot):
        self.lot = lot

    def download_lot(self):
        files = list()
        docs = self.lot.get("documents", {}).get("documents", []) or []
        for doc in docs:
            link = doc.get("url")
            name = doc.get("name")
            files.append(DownloadData(url=link, file_name=name))
        for i, image in enumerate(self.lot.get("images")):
            link = image.get("origin")
            name = link.split("/")[-1]
            files.append(DownloadData(url=link, file_name=name, is_image=True, order=i))
        return files

    @classmethod
    def download_general(cls):
        return []

    @property
    def trading_id(self):
        return self.lot_id

    @property
    def trading_link(self):
        return self.lot_link

    @property
    def lot_id(self):
        return self.lot["id"]

    @property
    def trading_type(self):
        types = {
            "auction": ["Открытый аукцион", "Аукцион", "Аукцион на понижение"],
            "offer": ["Публичное предложение"],
            "competition": ["Конкурс"],
        }
        for k, v in types.items():
            if self.lot["typeTorg"] in v:
                return k
        logger.warning(
            f"{self.lot_link} | Could not parse trading type: {self.lot['typeTorg']}"
        )
        return None

    @property
    def trading_number(self):
        return self.trading_id

    @property
    def trading_form(self):
        return "open"

    @property
    def trading_org(self):
        manager_profile = self.lot.get("manager", {}).get("profile")
        if not manager_profile:
            return None
        return " ".join(
            [
                manager_profile.get("lastName"),
                manager_profile.get("firstName"),
                manager_profile.get("middleName"),
            ]
        )

    @property
    def trading_org_inn(self):
        return Contacts.check_inn(
            self.lot.get("manager", {}).get("profile", {}).get("inn")
        )

    @property
    def trading_org_contacts(self):
        return {
            "email": None,
            "phone": Contacts.check_phone(
                self.lot.get("manager", {}).get("profile", {}).get("phone")
            ),
        }

    @property
    def msg_number(self):
        return Contacts.check_msg_number(self.lot.get("torg", {}).get("msgId"))

    @property
    def case_number(self):
        return Contacts.check_case_number(
            ((self.lot.get("casefile") or {}).get("casefile", {}) or {}).get("regNumber")
        )

    @property
    def debtor_inn(self):
        bankrupt = self.lot.get("bankrupt", {}).get("bankrupt", {}) or {}
        return Contacts.check_inn(bankrupt.get("profile", {}).get("inn"))

    @property
    def address(self):
        return self.lot.get("region")

    @property
    def arbit_manager(self):
        return None

    @property
    def arbit_manager_inn(self):
        return None

    @property
    def arbit_manager_org(self):
        return None

    @property
    def status(self):
        active = (
            "Торги в стадии приема заявок",
            "Прием заявок",
            "Проводится приём заявок",
            "Идут торги",
        )
        pending = (
            "Объявлены торги",
            "Имущество не продано. Определяется дата новых торгов",
        )
        ended = (
            "Проведена инвентаризация",
            "Проведена оценка",
            "Имущество реализовано",
            "Имущество не реализовано",
            "Приём заявок завершен",
            "Не объявлено",
        )
        status = self.lot["markerState"]
        if status in active:
            return "active"
        elif status in pending:
            return "pending"
        elif status in ended:
            return "ended"
        return None

    @property
    def lot_link(self):
        return f"https://ei.ru/lot/{self.lot_id}"

    @property
    def lot_number(self):
        return "1"

    @property
    def short_name(self):
        return self.lot.get("title")

    @property
    def lot_info(self):
        return BeautifulSoup(
            self.lot.get("description", {}).get("description"), "lxml"
        ).get_text()

    @property
    def categories(self):
        return [el["name"] for el in self.lot.get("categories", []) or []]

    @property
    def property_information(self):
        return None

    @property
    def start_date_requests(self):
        return DateTimeHelper.smart_parse(self.lot["startedAt"], '%d.%m.%Y, %H:%M').astimezone(DateTimeHelper.moscow_tz)

    @property
    def end_date_requests(self):
        return DateTimeHelper.smart_parse(self.lot["endAt"], '%d.%m.%Y, %H:%M').astimezone(DateTimeHelper.moscow_tz)

    @property
    def start_date_trading(self):
        return DateTimeHelper.smart_parse(self.lot["completedAt"], '%d.%m.%Y, %H:%M').astimezone(DateTimeHelper.moscow_tz)

    @property
    def end_date_trading(self):
        return None

    @property
    def start_price(self):
        return make_float(self.lot["start_price"])

    @property
    def step_price(self):
        return make_float(self.lot['step'])

    @property
    def periods(self):
        return None
    
