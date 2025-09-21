import re

from bs4 import BeautifulSoup

from app.db.models import DownloadData
from .config import data_origins, hosts
from app.utils import (
    DateTimeHelper,
    URL,
    dedent_func,
    Contacts,
    make_float, logger,
)


class Combo:
    def __init__(self, response):
        self.response = response
        self.soup = BeautifulSoup(response.text, "lxml")

    def get_table_value_by(self, name_table, name_row):
        for table in self.soup.select("div.collaps-block"):
            if (
                    table.select_one("div.collaps-block__title").get_text(strip=True)
                    == name_table
            ):
                for row in table.select("div.info"):
                    if row.label.get_text(strip=True) == name_row:
                        return row.div.get_text(strip=True)
        return None

    def get_value_by(self, lot: BeautifulSoup, name_row: str):
        element = lot.find("label", text=name_row)
        if element:
            return element.findNext("div", {"class": "info__title"}).get_text(
                strip=True
            )
        return None

    def download_general(self, property_type: str):
        files = list()
        if not (docs := self.soup.select_one("div#doc")):
            return files
        for doc in docs.find_all("a"):
            link = URL.url_join(data_origins[property_type], doc.get("href"))
            name = doc.get_text(strip=True)
            file_type = doc.get("class")[-1].split("--")[-1]
            if not name.endswith(file_type):
                name = f"{name}.{file_type}"
            files.append(
                DownloadData(
                    url=link, file_name=name, referer=self.trading_link, host=hosts[property_type]
                )
            )
        return files

    def download_lot(self, lot: BeautifulSoup, property_type: str):
        files = list()
        additional_informations = lot.find_all(
            "label", text="Дополнительная информация"
        )
        if not additional_informations:
            return files
        for info in additional_informations:
            info_block = info.find_parent("div", {"class": "info"})
            for doc in info_block.find_all("a"):
                link = URL.url_join(data_origins[property_type], doc.get("href"))
                name = doc.get_text(strip=True)
                file_type = doc.get("class")[-1].split("--")[-1]
                if not name.endswith(file_type):
                    name = f"{name}.{file_type}"
                files.append(
                    DownloadData(
                        url=link, file_name=name, referer=self.trading_link, host=hosts[property_type]
                    )
                )
        return files

    @property
    def trading_id(self):
        return self.trading_link.split("/")[-1]

    @property
    def trading_link(self):
        return self.response.url

    @property
    def trading_number(self):
        return self.trading_id

    @property
    def trading_type(self):
        d = {
            "offer": ["Публичное предложение"],
            "auction": ["Открытый аукцион", "Торги на повышение", "Аукцион"],
            "rfp": ['Запрос котировок']
        }
        trading_type = self.get_table_value_by(
            "Основные сведения",
            "Форма проведения торгов",
        ) or self.get_table_value_by(
            "Основные сведения",
            "Тип процедуры"
        )
        for key in d:
            if trading_type in d[key]:
                return key
        logger.warning(f'{self.response.url} | Could not parse trading_type={trading_type}')
        return None

    @property
    def trading_form(self):
        return "open"

    @property
    def trading_org(self):
        trading_org = [
            self.get_table_value_by("Сведения об организаторе", "Фамилия"),
            self.get_table_value_by("Сведения об организаторе", "Имя"),
            self.get_table_value_by("Сведения об организаторе", "Отчество"),
            self.get_table_value_by("Сведения об организаторе", "Полное наименование"),
        ]
        result = []
        for field in trading_org:
            if field == "":
                continue
            result.append(field)
        trading_org = " ".join(result)
        return trading_org

    @property
    def trading_org_inn(self):
        trading_org_inn = self.get_table_value_by(
            "Сведения об организаторе",
            "ИНН",
        )
        return Contacts.check_inn(trading_org_inn)

    @property
    def trading_org_contacts(self):
        trading_org_contacts = [
            self.get_table_value_by(
                "Сведения об организаторе",
                "Номер контактного телефона",
            ),
            self.get_table_value_by(
                "Сведения об организаторе",
                "Адрес электронной почты",
            ),
        ]
        return {
            "email": Contacts.check_email(trading_org_contacts[1]),
            "phone": Contacts.check_phone(trading_org_contacts[0]),
        }

    @property
    def msg_number(self):
        if not (msg_number := self.get_table_value_by(
                "Основные сведения",
                "Номер сообщения «Объявление о проведении торгов» в ЕФРСБ",
        )):
            return None
        if str.isdigit(msg_number):
            msg_number = msg_number
        elif (
                str.isdigit(msg_number.split("; ")[0])
                and len(msg_number.split("; ")[0]) == 7
        ):
            msg_number = msg_number.split("; ")[0]
        elif str.isdigit(msg_number.split()[0]) and len(msg_number.split()[0]) == 7:
            msg_number = msg_number.split()[0]
        elif (
                len(msg_number.split()) >= 2
                and str.isdigit(msg_number.split()[1])
                and len(msg_number.split()[1]) == 7
        ):
            msg_number = msg_number.split()[1]
        return msg_number

    @property
    def case_number(self):
        return Contacts.check_case_number(
            self.get_table_value_by("Основные сведения", "Номер дела о банкротстве")
        )

    @property
    def debtor_inn(self):
        return Contacts.check_inn(
            self.get_table_value_by(
                "Сведения о должнике",
                "ИНН",
            )
        )

    def get_debtor_address(self) -> str:
        return self.get_table_value_by(
            "Основные сведения",
            "Наименование арбитражного суда, рассматривающего дело о банкротстве",
        )

    @property
    def arbit_manager(self):
        return " ".join(
            [
                self.get_table_value_by(
                    "Cведения об арбитражном управляющем",
                    "Фамилия",
                ) or '',
                self.get_table_value_by(
                    "Cведения об арбитражном управляющем",
                    "Имя",
                ) or '',
                self.get_table_value_by(
                    "Cведения об арбитражном управляющем",
                    "Отчество",
                ) or '',
            ]
        ).strip()

    @property
    def arbit_manager_inn(self):
        return Contacts.check_inn(
            self.get_table_value_by(
                "Cведения об арбитражном управляющем",
                "ИНН",
            )
        )

    @property
    def arbit_manager_org(self):
        return self.get_table_value_by(
            "Cведения об арбитражном управляющем",
            "Наименование СРО",
        )

    def parse_status(self, status: str):
        d = {
            "active": ["Идет прием заявок"],
            "pending": ["Торги объявлены"],
            "ended": [
                "Торги отменены",
                "Торги завершены",
                "Идет подведение итогов",
                "Торги проводятся",
                "Прием заявок окончен",
                "Торги приостановлены",
                "Процедура завершена",
                "Заключение договоров",
            ],
        }
        for key in d:
            if status in d[key]:
                return key
        return None

    def get_lots(self):
        lot_list = self.soup.find("div", id="lotlist")
        lots = []
        for lot in lot_list.find_all("h5"):
            html_between = str(lot)
            end_tag = lot.find_next_sibling("h5")
            current = lot.find_next_sibling()
            while current and current != end_tag:
                html_between += str(current)
                current = current.find_next_sibling()
            lots.append(BeautifulSoup(html_between, "lxml"))
        return lots

    @property
    def lot_id(self):
        return

    @property
    def lot_link(self):
        return

    def lot_number(self, lot: BeautifulSoup):
        return lot.find("h5").get_text(strip=True).split()[-1]

    @property
    def short_name(self):
        return

    def lot_info(self, lot: BeautifulSoup):
        return dedent_func(
            self.get_value_by(
                lot,
                "Сведения об имуществе должника (состав, характеристики, описание, порядок ознакомления с имуществом (предприятием) должника)",
            ) or self.get_value_by(
                lot, "Предмет договора"
            )
        )

    @property
    def property_information(self):
        return

    @property
    def start_date_requests(self):
        date = self.get_table_value_by(
            "Основные сведения",
            "Дата и время начала представления заявок на участие в торгах",
        ) or self.get_table_value_by(
            "Основные сведения",
            "Дата и время начала представления заявок на участие в процедуре"
        )
        if date:
            return DateTimeHelper.smart_parse(date).astimezone(DateTimeHelper.moscow_tz)
        return None

    @property
    def end_date_requests(self):
        date = self.get_table_value_by(
            "Основные сведения",
            "Дата и время окончания представления заявок на участие в торгах",
        ) or self.get_table_value_by(
            "Основные сведения",
            "Дата и время окончания представления заявок на участие в процедуре"
        )
        if date:
            return DateTimeHelper.smart_parse(date).astimezone(DateTimeHelper.moscow_tz)
        return None

    @property
    def start_date_trading(self):
        date = self.get_table_value_by(
            "Основные сведения",
            "Дата и время начала проведения торгов",
        )
        if date:
            return DateTimeHelper.smart_parse(date).astimezone(DateTimeHelper.moscow_tz)
        return None

    @property
    def end_date_trading(self):
        date = self.get_table_value_by(
            "Основные сведения",
            "Дата и время подведения результатов торгов",
        ) or self.get_table_value_by(
            "Основные сведения",
            "Дата и время подведения итогов"
        )
        if date:
            dt = DateTimeHelper.smart_parse(date)
            if dt:
                return dt.astimezone(DateTimeHelper.moscow_tz)
        return None

    def start_price(self, lot: BeautifulSoup):
        if periods := self.periods(lot):
            return periods[0]["current_price"]
        start_price = self.get_value_by(
            lot, "Начальная цена продажи имущества (предприятия) должника, руб."
        ) or self.get_table_value_by(
            lot, "Сведения о начальной (максимальной) цене договора"
        )
        if not start_price:
            return None
        try:
            if start_price:
                start_price = re.sub(
                    r"\s",
                    "",
                    dedent_func(start_price.strip()).replace(",", ".").rstrip("."),
                )
                start_price = "".join(
                    [x for x in start_price if x.isdigit() or x == "."]
                )
                if len(start_price) > 0:
                    return round(float(start_price), 2)
        except Exception as e:
            logger.warning(f"{self.response.url} :: INVALID DATA START PRICE\n{e}")
        return None

    def step_price(self, lot: BeautifulSoup):
        step_price = self.get_value_by(
            lot,
            "Величина повышения начальной цены продажи имущества (предприятия), «шаг аукциона», руб.",
        )
        try:
            if step_price:
                step_price = re.sub(
                    r"\s",
                    "",
                    dedent_func(step_price.strip()).replace(",", ".").rstrip("."),
                )
                step_price = "".join([x for x in step_price if x.isdigit() or x == "."])
                if len(step_price) > 0:
                    return round(float(step_price), 2)
        except ValueError as e:
            logger.error(f"{self.response.url} :: INVALID DATA STEP PRICE\n{e}")
        return None

    def categories(self, lot: BeautifulSoup):
        categories = lot.find(
            "div", class_="info__name", text="Классификатор имущества должников:"
        )
        if categories:
            return categories.find_next("div", class_="info__title").get_text(
                strip=True
            )
        return None

    def periods(self, lot: BeautifulSoup):
        periods = []
        for table in lot.find_all("table"):
            periods.append(
                {
                    "start_date_requests": DateTimeHelper.smart_parse(
                        table.select("td")[0].get_text(strip=True).split(" по ")[0][2:]
                    ).astimezone(DateTimeHelper.moscow_tz),
                    "end_date_requests": DateTimeHelper.smart_parse(
                        table.select("td")[0]
                        .get_text(strip=True)
                        .split(" по ")[1]
                        .split(" - ")[0]
                    ).astimezone(DateTimeHelper.moscow_tz),
                    "end_date_trading": DateTimeHelper.smart_parse(
                        table.select("td")[0]
                        .get_text(strip=True)
                        .split(" по ")[1]
                        .split(" - ")[0]
                    ).astimezone(DateTimeHelper.moscow_tz),
                    "current_price": make_float(
                        table.select("td")[0]
                        .get_text(strip=True)
                        .split(" по ")[1]
                        .split(" - ")[1]
                    ),
                }
            )
        return periods
