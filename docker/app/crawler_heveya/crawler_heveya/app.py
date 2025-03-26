import logging
import re
from itertools import takewhile

from bs4 import BeautifulSoup

from general_utils import UrlConfig, contains, CheckIfCorrectContactInfo, dedent_func, format_time
from general_utils.models import DownloadData

logger = logging.getLogger(__name__)


class Combo:
    def __init__(self, response):
        self.response = response
        self.soup = BeautifulSoup(self.response.text, 'lxml')

    def download_lot(self):
        files = list()
        for a in self.soup.find('div', class_='mainPhoto').find_all('img'):
            link = a.get("src")
            name = link.split('/')[-1]
            files.append(DownloadData(url=link, file_name=name, refere=self.response.url))
        return files

    def download_general(self):
        return []

    @property
    def start_price(self):
        return self.get_main_info()[3]

    @property
    def step_price(self):
        return self.get_main_info()[4]

    @property
    def trading_org(self):
        return self.get_main_info()[1]

    @property
    def trading_org_contacts(self):
        return self.get_main_info()[2]

    @property
    def trading_type(self):
        return self.get_main_info()[0]

    def get_main_info(self):
        soup = BeautifulSoup(self.response.xpath('//div[@class="prices right__prices"]').get(), 'lxml')
        start_price = self.parse_price(soup.find('div', class_='value rouble').get_text())

        step_price = soup.find('span', class_='caption', text="Шаг повышения:")
        if step_price:
            type_ = 'auction'
            step_price = step_price.find_next('div', class_='value').find('span').get_text()
            p = ''.join([p for p in step_price if p.isdigit() or p == '.'])
            p = re.sub(r'\.$', '', p).strip()
            if len(p) > 0:
                step_price = round(float(p), 2)
        else:
            type_ = 'offer'

        org = soup.find('span', text=contains('ОТ')).find_next('a')
        try:
            org = "".join(re.sub(r"\s+", " ", org.get_text().strip()))
        except:
            logger.warning(f"{self.response.url} :: INVALID DATA ORGANIZER", exc_info=True)

        org_contacts = soup.find('div', class_='contacts').find_all('a')
        email = None
        phone = None
        for el in org_contacts:
            href = el.get('href')
            value = el.find('span').get_text()
            if href.startswith('tel:'):
                phone = CheckIfCorrectContactInfo.check_phone(dedent_func(value).replace(';', '').strip())
            if href.startswith('mailto:'):
                email = CheckIfCorrectContactInfo.check_email(dedent_func(value).replace(';', '').strip())
        return (
            type_,
            org,
            {'email': email, 'phone': phone},
            start_price,
            step_price,
        )

    def get_phone_number(self, org_contacts):
        """get phone number of organizer"""
        try:
            phone = dedent_func(org_contacts.find_all('a', class_=contains('tel:'))).replace(';', '').strip()
            return CheckIfCorrectContactInfo.check_phone(phone)
        except:
            return

    def get_email(self, org_contacts):
        """get email of organizer"""
        try:
            email = dedent_func(org_contacts.find('a', class_=contains('mailto:'))).replace(';', '').strip()
            return CheckIfCorrectContactInfo.check_email(email)
        except:
            return

    def parse_price(self, price: str):
        try:
            price = re.sub(r"\s", "", dedent_func(price).replace(",", "."))
            price = "".join([x for x in price if x.isdigit() or x == "."])
            if len(price) > 0:
                return round(float(price), 2)
        except Exception as e:
            logger.error(f"{self.response.url} :: INVALID START PRICE\n{e}")

    @property
    def trading_id(self):
        return self.lot_id

    @property
    def trading_link(self):
        return self.response.url

    @property
    def trading_number(self):
        return

    @property
    def trading_form(self):
        return 'open'

    @property
    def case_number(self):
        case_ = self.soup.find('span', text=contains('Дело о банкротстве'))
        if case_:
            return CheckIfCorrectContactInfo.check_case_number(dedent_func(case_.find_next('a').get_text()))

    @property
    def debtor_inn(self):
        inn = self.soup.find('span', text=contains('ИНН должника'))
        if inn:
            return CheckIfCorrectContactInfo.check_inn(dedent_func(inn.find_next('span').get_text()))

    def get_address(self):
        address = self.soup.find('span', class_='dataCaption', text=contains('Адрес'))
        if not address:
            return
        address = dedent_func(address.find_next('span', class_='item__value value').get_text(strip=True))
        if address == 'Торги по банкротству':
            pass
        if address and 'Информация скрыта' not in address:
            return address

    @property
    def arbit_manager(self):
        manager = self.soup.find('h2', class_='blockHeader', text=contains('Арбитражный управляющий'))
        if not manager:
            return self.trading_org()
        return dedent_func(manager.find_next('a', class_='personalDataPanel_company').get_text())

    @property
    def arbit_manager_inn(self):
        return

    @property
    def arbit_manager_org(self):
        return

    @property
    def lot_id(self):
        return ''.join(re.findall(r'\d+', str(self.response.url)))

    @property
    def lot_link(self):
        return self.response.url

    @property
    def lot_number(self):
        return

    @property
    def short_name(self):
        short_name = self.soup.find('div', class_='breadcrumbs').find_all('span', class_='item')[-1]
        return dedent_func(short_name.get_text())

    @property
    def lot_info(self):
        return dedent_func(self.soup.find('span', text='Описание:').find_next('span').get_text())

    @property
    def property_information(self):
        info = self.soup.find('h2', text='Порядок осмотра')
        if info:
            return dedent_func(info.find_next('p').get_text())

    @property
    def start_date_requests(self):
        return format_time(self.soup.find('h2', text='Дата начала приема заявок').find_next('p').get_text())

    @property
    def end_date_requests(self):
        return format_time(self.soup.find('h2', text='Дата окончания приема заявок').find_next('p').get_text())

    @property
    def start_date_trading(self):
        start = self.soup.find('h2', text='Начало подачи предложений')
        if start:
            return format_time(start.find_next('p').get_text())
        return self.start_date_requests

    @property
    def end_date_trading(self):
        return format_time(self.soup.find('h2', text='Подведение итогов торгов').find_next('p').get_text())

    @property
    def periods(self):
        table = self.soup.find('h2', text='Порядок понижения цены')
        if not table:
            return
        check_value = 10000000000000000000000
        table = table.find_next('div', class_='priceDowngrade').find('div', class_='body').find_all('div',
                                                                                                    class_='gridRow')
        periods = []
        for row in table:
            columns = row.find_all('div')  # Ищем все столбцы в строке
            start = columns[0].get_text(strip=True)
            end = columns[1].get_text(strip=True)
            price = columns[2].get_text(strip=True)
            price = "".join(takewhile(lambda x: x != "р" and x != "Р", price))
            try:
                if isinstance(price, str):
                    price = ''.join(re.sub(r"\s", "", price)).replace(',', '.')
                    price = round(float(price), 2)
                else:
                    price = round(float(price), 2)
                if check_value < price:
                    logger.critical(
                        f'{self.response.url} :: INVALID PRICE ON PERIOD - CURRENT PRICE HIGHER THAN PREVIUOS')
                else:
                    check_value = price
            except:
                logger.error(f'{self.response.url} Period Price - {price} typeof - {type(price)}')
                return None
            try:
                period = {
                    'start_date_requests': format_time(start),
                    'end_date_requests': format_time(end),
                    'end_date_trading': format_time(end),
                    'current_price': price
                }
                periods.append(period)
            except:
                continue
        return periods
