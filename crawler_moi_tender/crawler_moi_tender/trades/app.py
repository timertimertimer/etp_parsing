import re

from bs4 import BeautifulSoup

from ..utils.check_inn_email_phone import CheckIfCorrectContactInfo
from ..utils.work_with_text_and_number import dedent_func, contains
from ..utils.working_with_time import format_time


class Combo:
    def __init__(self, response):
        self.response = response
        self.soup = BeautifulSoup(response, 'lxml')
        self.check = CheckIfCorrectContactInfo()

    def get_lots(self):
        lots = self.soup.find_all('div', class_=re.compile('tender'))
        lots_data = []
        for lot in lots:
            procedure_type = lot.find('div', class_='type').get_text(strip=True)
            if 'закрыт' in procedure_type.lower():  # Доступ по паролю
                continue
            trading_id = trading_number = dedent_func(lot.find('div', class_='num').get_text(strip=True))
            status = self.parse_status(dedent_func(lot.find('div', class_='status').get_text(strip=True)))
            trading_org = dedent_func(lot.find('div', class_='company').get_text(strip=True))
            category = dedent_func(lot.find('div', class_='tender-cat').get_text(strip=True))
            short_desc = lot.find('div', class_='short-desc')
            trading_link = short_desc.find('a')['href']
            short_name = dedent_func(short_desc.find('a').get_text(strip=True))
            start_price = lot.find('div', class_='price').get_text(strip=True)
            company = lot.find('div', class_='company').find('a')
            org = dedent_func(company.get_text(strip=True))
            org_link = dedent_func(company['href'])
            lots_data.append((
                trading_link, trading_id, trading_number, status, trading_org, category, short_name, start_price, org,
                org_link
            ))
        return lots_data

    def parse_status(self, status: str):
        status = status.strip().lower()
        if status == 'процедура закрыта':
            return 'closed'
        else:
            return 'open'

    def download_general(self):
        ...

    def download_lot(self):
        ...

    @property
    def trading_form(self):
        ...

    @property
    def trading_org_contacts(self):
        email = self.soup.find('a', href=re.compile('mailto:'))
        if email:
            email = self.check.check_email(dedent_func(email.get_text()))
            phone = email.find_next('div', class_='value').get_text()
            phone = self.check.check_phone(phone)
            return {"email": email, "phone": phone}

    @property
    def index(self):
        ...

    @property
    def address(self):
        region = dedent_func(self.soup.find('div', class_='label', text='Регион').find_next('div').get_text(strip=True))
        city = dedent_func(self.soup.find('div', class_='label', text='Город').find_next('div').get_text(strip=True))
        return f'{region}, {city}'

    @property
    def detailed_address(self):
        ...

    @property
    def encumbrance(self):
        ...

    @property
    def description_encumbrance(self):
        ...

    @property
    def lot_number(self):
        ...

    @property
    def lot_info(self):
        return dedent_func(self.soup.find('div', class_='description').get_text())

    @property
    def property_information(self):
        ...

    @property
    def start_date_requests(self):
        start = self.soup.find('div', class_='label', text=contains('Дата публикации извещения')).find_next(
            'div').get_text(strip=True)
        return format_time(start)

    @property
    def end_date_requests(self):
        start = self.soup.find('div', class_='label', text=contains('Дата публикации извещения')).find_next(
            'div').get_text(strip=True)
        return format_time(start)

    @property
    def start_date_trading(self):
        ...

    @property
    def end_date_trading(self):
        ...

    @property
    def min_price(self):
        ...

    @property
    def deposit(self):
        ...

    @property
    def step_price(self):
        ...

    @property
    def periods(self):
        ...

    @property
    def quantity(self):
        ...

    @property
    def unit(self):
        ...
