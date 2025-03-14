import logging
import re

from bs4 import BeautifulSoup

from general_utils.models import DownloadData
from .config import host, data_origin
from general_utils import format_time, UrlConfig, dedent_func, CheckIfCorrectContactInfo

logger = logging.getLogger(__name__)


class Combo:
    def __init__(self, response):
        self.response = response
        self.soup = BeautifulSoup(response.text, "lxml")

    def get_table_value_by(self, name_table, name_row):
        for table in self.soup.select("div.collaps-block"):
            if table.select_one('div.collaps-block__title').get_text(strip=True) == name_table:
                for row in table.select('div.info'):
                    if row.label.get_text(strip=True) == name_row:
                        return row.div.get_text(strip=True)

    def get_value_by(self, lot: BeautifulSoup, name_row: str):
        element = lot.find("label", text=name_row)
        if element:
            return element.findNext("div", {'class': 'info__title'}).get_text(strip=True)

    def download_general(self):
        files = list()
        if not (docs := self.soup.select_one('div#doc')):
            return files
        for doc in docs.find_all('a'):
            link = UrlConfig.url_join(data_origin, doc.get('href'))
            name = doc.get_text(strip=True)
            files.append(DownloadData(url=link, file_name=name, referer=self.trading_link, host=host))
        return files

    def download_lot(self, lot: BeautifulSoup):
        files = list()
        docs = lot.find("label", text='Дополнительная информация')
        if not docs:
            return files
        docs = docs.find_next("div", {'class': 'info__title'})
        for file in docs.find_all('a'):
            link = UrlConfig.url_join(data_origin, file.get('href'))
            name = file.get_text(strip=True)
            files.append(DownloadData(url=link, file_name=name, referer=self.trading_link, host=host))
        return files

    @property
    def trading_id(self):
        return self.trading_link.split('/')[-1]

    @property
    def trading_link(self):
        return self.response.url

    @property
    def trading_number(self):
        return self.trading_id

    @property
    def trading_type(self):
        d = {
            'offer': ['Публичное предложение'],
            'auction': ['Открытый аукцион', 'Торги на повышение']
        }
        trading_type = self.get_table_value_by(
            'Основные сведения',
            'Форма проведения торгов',
        )
        for key in d:
            if trading_type in d[key]:
                return key

    @property
    def trading_form(self):
        return 'open'

    @property
    def trading_org(self):
        trading_org = [
            self.get_table_value_by(
                'Сведения об организаторе',
                'Фамилия'
            ),
            self.get_table_value_by(
                'Сведения об организаторе',
                'Имя'
            ),
            self.get_table_value_by(
                'Сведения об организаторе',
                'Отчество'
            ),
            self.get_table_value_by(
                'Сведения об организаторе',
                'Полное наименование'
            )
        ]
        result = []
        for field in trading_org:
            if field == '':
                continue
            result.append(field)
        trading_org = ' '.join(result)
        return trading_org

    @property
    def trading_org_inn(self):
        trading_org_inn = self.get_table_value_by(
            'Сведения об организаторе',
            'ИНН',
        )
        return CheckIfCorrectContactInfo.check_inn(trading_org_inn)

    @property
    def trading_org_contacts(self):
        trading_org_contacts = [
            self.get_table_value_by(
                'Сведения об организаторе',
                'Номер контактного телефона',
            ),
            self.get_table_value_by(
                'Сведения об организаторе',
                'Адрес электронной почты',
            )
        ]
        return {
            'email': CheckIfCorrectContactInfo.check_email(trading_org_contacts[1]),
            'phone': CheckIfCorrectContactInfo.check_phone(trading_org_contacts[0])
        }

    @property
    def msg_number(self):
        msg_number = self.get_table_value_by(
            'Основные сведения',
            'Номер сообщения «Объявление о проведении торгов» опубликованного в ЕФРСБ'
        )
        if str.isdigit(msg_number):
            msg_number = msg_number
        elif str.isdigit(msg_number.split('; ')[0]) and len(msg_number.split('; ')[0]) == 7:
            msg_number = msg_number.split('; ')[0]
        elif str.isdigit(msg_number.split()[0]) and len(msg_number.split()[0]) == 7:
            msg_number = msg_number.split()[0]
        elif len(msg_number.split()) >= 2 and str.isdigit(msg_number.split()[1]) and len(
                msg_number.split()[1]) == 7:
            msg_number = msg_number.split()[1]
        return msg_number

    @property
    def case_number(self):
        return CheckIfCorrectContactInfo.check_case_number(self.get_table_value_by(
            'Основные сведения',
            'Номер дела о банкротстве'
        ))

    @property
    def debtor_inn(self):
        return CheckIfCorrectContactInfo.check_inn(self.get_table_value_by(
            'Сведения о должнике',
            'ИНН',
        ))

    def get_debtor_address(self) -> str:
        return self.get_table_value_by(
            'Основные сведения',
            'Наименование арбитражного суда, рассматривающего дело о банкротстве',
        )

    @property
    def arbit_manager(self):
        return ' '.join([
            self.get_table_value_by(
                'Cведения об арбитражном управляющем',
                'Фамилия',
            ),
            self.get_table_value_by(
                'Cведения об арбитражном управляющем',
                'Имя',
            ),
            self.get_table_value_by(
                'Cведения об арбитражном управляющем',
                'Отчество',
            )
        ])

    @property
    def arbit_manager_inn(self):
        return CheckIfCorrectContactInfo.check_inn(self.get_table_value_by(
            'Cведения об арбитражном управляющем',
            'ИНН',
        ))

    @property
    def arbit_manager_org(self):
        return self.get_table_value_by(
            'Cведения об арбитражном управляющем',
            'Наименование СРО',
        )

    def parse_status(self, status: str):
        d = {
            'active': ['Идет прием заявок'],
            'pending': ['Торги объявлены'],
            'ended': [
                'Торги отменены',
                'Торги завершены',
                'Идет подведение итогов',
                'Торги проводятся',
                'Прием заявок окончен',
                'Торги приостановлены'
            ]
        }
        for key in d:
            if status in d[key]:
                return key

    def get_lots(self):
        lot_list = self.soup.find('div', id='lotlist')
        lots = []
        for lot in lot_list.find_all('h5'):
            html_between = str(lot)
            end_tag = lot.find_next_sibling('h5')
            current = lot.find_next_sibling()
            while current and current != end_tag:
                html_between += str(current)
                current = current.find_next_sibling()
            lots.append(BeautifulSoup(html_between, 'lxml'))
        return lots

    @property
    def lot_id(self):
        return

    @property
    def lot_link(self):
        return

    def lot_number(self, lot: BeautifulSoup):
        return lot.find('h5').get_text(strip=True).split()[-1]

    @property
    def short_name(self):
        return

    def lot_info(self, lot: BeautifulSoup):
        return dedent_func(self.get_value_by(
            lot,
            'Сведения об имуществе должника (состав, характеристики, описание, порядок ознакомления с имуществом (предприятием) должника)'
        ))

    @property
    def property_information(self):
        return

    @property
    def start_date_requests(self):
        date = self.get_table_value_by(
            'Основные сведения',
            'Дата и время начала представления заявок на участие в торгах',
        )
        if date:
            return format_time(date)

    @property
    def end_date_requests(self):
        date = self.get_table_value_by(
            'Основные сведения',
            'Дата и время окончания представления заявок на участие в торгах',
        )
        if date:
            return format_time(date)

    @property
    def start_date_trading(self):
        date = self.get_table_value_by(
            'Основные сведения',
            'Дата и время начала проведения торгов',
        )
        if date:
            return format_time(date)

    @property
    def end_date_trading(self):
        date = self.get_table_value_by(
            'Основные сведения',
            'Дата и время подведения результатов торгов',
        )
        if date:
            return format_time(date)

    def start_price(self, lot: BeautifulSoup):
        if self.periods(lot):
            return self.periods(lot)[0]['current_price']
        start_price = self.get_value_by(lot, 'Начальная цена продажи имущества (предприятия) должника, руб.')
        if not start_price:
            return
        try:
            if start_price:
                start_price = re.sub(r'\s', '', dedent_func(start_price.strip()).replace(',', '.').rstrip('.'))
                start_price = ''.join([x for x in start_price if x.isdigit() or x == '.'])
                if len(start_price) > 0:
                    return round(float(start_price), 2)
        except Exception as e:
            logger.warning(f'{self.response.url} :: INVALID DATA START PRICE\n{e}')

    def step_price(self, lot: BeautifulSoup):
        step_price = self.get_value_by(
            lot, 'Величина повышения начальной цены продажи имущества (предприятия), «шаг аукциона», руб.'
        )
        try:
            if step_price:
                step_price = re.sub(r'\s', '', dedent_func(step_price.strip()).replace(',', '.').rstrip('.'))
                step_price = ''.join([x for x in step_price if x.isdigit() or x == '.'])
                if len(step_price) > 0:
                    return round(float(step_price), 2)
        except ValueError as e:
            logger.error(f'{self.response.url} :: INVALID DATA STEP PRICE\n{e}')

    def periods(self, lot: BeautifulSoup):
        periods = []
        for table in lot.find_all('table'):
            periods.append({
                "start_date_requests": format_time(table.select('td')[0].get_text(strip=True).split(' по ')[0][2:]),
                "end_date_requests": format_time(
                    table.select('td')[0].get_text(strip=True).split(' по ')[1].split(' - ')[0]
                ),
                "end_date_trading": format_time(
                    table.select('td')[0].get_text(strip=True).split(' по ')[1].split(' - ')[0]
                ),
                "current_price": format_time(
                    table.select('td')[0].get_text(strip=True).split(' по ')[1].split(' - ')[1])
            })
        return periods
