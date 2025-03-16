import logging
import re

from bs4 import BeautifulSoup

from .config import data_origin
from general_utils import format_time, UrlConfig, dedent_func, CheckIfCorrectContactInfo
from general_utils.models import DownloadData

logger = logging.getLogger(__name__)


class Combo:
    addresses = dict()

    def __init__(self, response):
        self.response = response
        self.soup = BeautifulSoup(response.text, "html.parser")

    def get_table_value(self, name_table, name_row):
        for table_cont in self.soup.select('.etp-block'):
            if table_cont.h2 is None:
                continue
            if table_cont.h2.get_text().strip() != name_table:
                continue
            for row in table_cont.select('tr'):
                try:
                    if row.select('td')[0].get_text().strip() == row.select('td')[1].get_text().strip():
                        return row.select('td')[1].get_text().strip()
                    if row.select('td')[0].get_text().strip() != name_row:
                        continue
                    return row.select('td')[1].get_text().strip()
                except Exception as e:
                    return

    def download(self):
        files = list()
        for row in self.soup.select_one('.etp-main-content>.row:last-child table:last-child').select('tr')[1:]:
            t = row.find_all('td')
            name = t[2].get_text(strip=True)
            link = UrlConfig.url_join(data_origin, t[5].find('a').get('href'))
            files.append(DownloadData(url=link, file_name=name))
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
        trading_type = self.response.css('h1::text').get()
        if trading_type.strip() in [
            'Публичное предложение'
        ]:
            trading_type = 'offer'

        elif trading_type.strip() in [
            'Открытый аукцион',
            'Закрытый аукцион',
            'Аукцион с закрытой формой представления цены'
        ]:
            trading_type = 'auction'

        elif trading_type.strip() in [
            'Конкурс'
        ]:
            trading_type = 'competition'
        else:
            return
        return trading_type

    @property
    def trading_form(self):
        trading_form = self.response.css('h1::text').get()
        if trading_form.strip() in [
            'Закрытый аукцион'
        ]:
            trading_form = 'closed'

        elif trading_form.strip() in [
            'Публичное предложение',
            'Открытый аукцион',
            'Конкурс',
            'Аукцион с закрытой формой представления цены'
        ]:
            trading_form = 'open'
        else:
            return
        return trading_form

    @property
    def trading_org(self):
        return self.get_table_value(
            'Контактное лицо',
            'ФИО'
        )

    @property
    def trading_org_contacts(self):
        return {
            'email': CheckIfCorrectContactInfo.check_email(self.get_table_value(
                'Контактное лицо',
                'Адрес электронной почты',
            )),
            'phone': CheckIfCorrectContactInfo.check_phone(self.get_table_value(
                'Контактное лицо',
                'Телефон',
            ))
        }

    @property
    def case_number(self):
        return CheckIfCorrectContactInfo.check_case_number(self.get_table_value(
            'Информация о должнике',
            'Номер дела о банкротстве',
        ))

    @property
    def debtor_inn(self):
        for el in [
            self.get_table_value(
                'Данные должника - физического лица',
                'ИНН',
            ),
            self.get_table_value(
                'Данные должника - юридического лица',
                'ИНН',
            ),
            self.get_table_value(
                'Данные должника - ИП',
                'ИНН',
            )
        ]:
            if el:
                return CheckIfCorrectContactInfo.check_inn(el)

    @property
    def address(self):
        address = self.get_table_value(
            'Информация о должнике',
            'Наименование арбитражного суда'
        )
        if address:
            return CheckIfCorrectContactInfo.check_address(address)

    @property
    def arbit_manager(self):
        initial_arbit_manager = [
            self.get_table_value(
                'Информация об арбитражном управляющем',
                'Фамилия',
            ),
            self.get_table_value(
                'Информация об арбитражном управляющем',
                'Имя',
            ),
            self.get_table_value(
                'Информация об арбитражном управляющем',
                'Отчество',
            )
        ]
        result = []
        for part_name in initial_arbit_manager:
            if part_name is None: continue
            result.append(part_name)
        arbit_manager = []
        for pn in result:
            for part_name in list(set(initial_arbit_manager)):
                if part_name == pn:
                    arbit_manager.append(part_name)
        if len(result) == 0:
            return
        return dedent_func(' '.join(arbit_manager))

    @property
    def arbit_manager_inn(self):
        return CheckIfCorrectContactInfo.check_inn(self.get_table_value(
            'Информация об арбитражном управляющем',
            'ИНН',
        ))

    @property
    def arbit_manager_org(self):
        return dedent_func(self.get_table_value(
            'Информация об арбитражном управляющем',
            'Наименование СРО',
        ))

    @property
    def lot_id(self):
        return self.trading_id

    @property
    def lot_link(self):
        return self.trading_link

    @property
    def lot_number(self):
        return self.get_table_value(
            'Общая информация',
            'Номер',
        )

    @property
    def short_name(self):
        return dedent_func(self.get_table_value(
            'Общая информация',
            'Наименование',
        ))

    @property
    def lot_info(self):
        return dedent_func(self.get_table_value(
            'Общая информация',
            'Сведения об имуществе, его составе и характеристиках, описание',
        ))

    @property
    def property_information(self):
        return dedent_func(self.get_table_value(
            'Общая информация',
            'Порядок ознакомления с имуществом',
        ))

    @property
    def start_date_requests(self):
        date = [
            self.get_table_value(
                'Датирование',
                'Дата начала приема заявок на участие в открытом аукционе',
            ),
            self.get_table_value(
                'Датирование',
                'Дата начала приема заявок на участие в конкурсе',
            )
        ]
        start_date_requests = None
        for arr_item in date:
            if arr_item:
                start_date_requests = format_time(arr_item)
        if start_date_requests is None and len(self.periods) != 0:
            return self.periods[0]['start_date_requests']
        return start_date_requests

    @property
    def end_date_requests(self):
        date = [
            self.get_table_value(
                'Датирование',
                'Дата окончания приема заявок на участие в открытом аукционе',
            ),
            self.get_table_value(
                'Датирование',
                'Дата окончания приема заявок на участие в конкурсе',
            )
        ]
        end_date_requests = None
        for arr_item in date:
            if arr_item:
                end_date_requests = format_time(arr_item)
        if end_date_requests is None and len(self.periods) != 0:
            return self.periods[-1]['end_date_requests']
        return end_date_requests

    @property
    def start_date_trading(self):
        date = [
            self.get_table_value(
                'Датирование',
                'Дата проведения открытого аукциона',
            ),
            self.get_table_value(
                'Датирование',
                'Дата проведения конкурса',
            )
        ]
        start_date_trading = None
        for arr_item in date:
            if arr_item:
                start_date_trading = format_time(arr_item)
        if start_date_trading is None and len(self.periods) != 0:
            return self.periods[0]['start_date_requests']
        return start_date_trading

    @property
    def end_date_trading(self):
        if len(self.periods) != 0:
            return self.periods[-1]['end_date_requests']

    def clean_price(self, price):
        if '%' in price:
            return
        return float(price.replace(" ", "").replace("руб.", "").replace(',', '.'))

    @property
    def start_price(self):
        return self.clean_price(self.get_table_value(
            'Общая информация',
            'Начальная цена',
        ))

    @property
    def step_price(self):
        price = [
            self.get_table_value(
                'Общая информация',
                'Единицы шага',
            ),
            self.get_table_value(
                'Общая информация',
                'Введите значение шага',
            ),
            self.get_table_value(
                'Общая информация',
                'Значение шага',
            )
        ]
        if all([p is None for p in price]):
            return
        if all([p is not None for p in price[1:]]):
            return
        if price[0] == 'Проценты' and price[1] is not None:
            number = re.search(r'\d+', price[1]).group()
            return round(self.start_price * 0.01 * int(number), 2)
        elif price[0] == 'Проценты' and price[2] is not None:
            return round(self.start_price * 0.01 * int(price[2]), 2)

        if price[0] == 'Рубли' and price[1] is not None:
            return self.clean_price(price[1])
        elif price[0] == 'Рубли' and price[2] is not None:
            return self.clean_price(price[2])

    @property
    def periods(self):
        periods = []
        for table_cont in self.soup.select('.etp-block'):
            if table_cont.h2 is None:
                continue
            if table_cont.h2.get_text().strip() != 'Общая информация':
                continue
            for row in table_cont.select('tr'):
                if not row.select('td')[0].get_text().strip().startswith('Промежуток'):
                    continue
                if len(row.select('td')) < 2:
                    continue
                periods.append(row.select('td')[1].get_text().strip())
        final_periods = []
        for period_str in periods:
            period_str = period_str.split(': ')
            period = {
                "start_date_requests": format_time(period_str[0].split(' - ')[0]),
                "end_date_requests": format_time(period_str[0].split(' - ')[1]),
                "end_date_trading": format_time(period_str[0].split(' - ')[1]),
                "current_price": self.clean_price(period_str[-1])
            }

            final_periods.append(period)

        return final_periods
