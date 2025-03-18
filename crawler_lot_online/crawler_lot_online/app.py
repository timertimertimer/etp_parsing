import re
import logging
from bs4 import BeautifulSoup

from general_utils import UrlConfig, contains, dedent_func, format_time, parse_datetime, return_parse_date
from general_utils.models import DownloadData

logger = logging.getLogger(__name__)


class Combo:
    addresses = dict()

    def __init__(self, response):
        self.response = response
        self.soup = BeautifulSoup(response.text, 'lxml')

    def download_general(self):
        return []

    def download_lot(self, data_origin):
        files = list()
        for link in self.soup.find('div', id='lot_documents').find_all('a'):
            name = link.get_text().strip()
            link = link.get('href')
            files.append(
                DownloadData(url=UrlConfig.url_join(data_origin, link), file_name=name, referer=self.response.url)
            )
        return files

    @property
    def trading_type(self):
        type_ = self.soup.find('strong', text=contains('Вид процедуры:'))
        if type_:
            type_ = type_.find_next('span').text.strip().lower()
            if any([
                'аукцион' in type_,
                'сессия' in type_,
            ]):
                return 'auction'
            elif 'конкурс' in type_:
                return 'competition'
            elif 'предложени' in type_:
                return 'offer'
            else:
                pass

    @property
    def trading_org(self):
        org = self.soup.find('strong', text=contains('Организатор'))
        if org:
            org = org.find_next('span').text.strip()
            return dedent_func(org)

    @property
    def status(self):
        status = self.soup.find('p', id='lot_status')
        if status:
            status = status.text.strip().lower()
            if status in (
                    'подача заявок', 'опубликована', 'опубликован проект', 'размещена в еис', 'подача предложений'
            ):
                return 'active'
            elif status in ('рассмотрение заявок', 'ожидает рассмотрения заявок', 'ожидает начала подачи предложений'):
                return 'pending'
            elif status in ('завершена', 'рассмотрение предложений/подведение итогов', 'отменена'):
                return 'ended'
            else:
                pass

    @property
    def category(self):
        category = self.soup.find('strong', text=contains('Категория'))
        if category:
            categories = category.find_next('span').text.strip().split('/')
            categories_ = []
            for category in categories:
                category = category.strip()
                if category == 'Рубрикатор':
                    continue
                categories_.append(category)
            return categories_

    @property
    def address(self):
        country = self.soup.find('strong', text=contains('Страна'))
        if country:
            country = country.find_next('span').text.strip()
        address = self.soup.find('strong', text=contains('Адрес'))
        if address:
            address = address.find_next('span').text.strip()
            address = dedent_func(f'{country}, {address}')
            return address

    @property
    def lot_info(self):
        info = self.soup.find('strong', text=contains('Описание лота'))
        if info:
            info = info.find_next('span').text.strip()
            return dedent_func(info)

    @property
    def start_date_requests(self):
        return self.get_dates_from_interval('Прием заявок')[0]

    @property
    def end_date_requests(self):
        return self.get_dates_from_interval('Прием заявок')[1]

    @property
    def start_date_trading(self):
        return self.get_dates_from_interval('Подача предложений')[0]

    @property
    def end_date_trading(self):
        return self.get_dates_from_interval('Подача предложений')[1]

    def get_dates_from_interval(self, label):
        date_requests = self.soup.find('strong', text=contains('Прием заявок'))
        if date_requests:
            date_requests = date_requests.find_next('span').text.strip().replace(' ', ' ')
            start, end = date_requests.split(' - ')
            format = '%d/%m/%Y %H:%M (MCK)'
            return return_parse_date(start, format), return_parse_date(end, format)

    @property
    def start_price(self):
        try:
            p = self.get_acitvity_table().find('span', id='priceStart')
            if p:
                p = re.sub(r'\s', '', dedent_func(p.get_text().strip()).replace(',', '.'))
                p = ''.join([x for x in p if x.isdigit() or x == '.'])
                if len(p) > 0:
                    return round(float(p), 2)
        except ValueError as e:
            logger.error(f'{self.response.url} :: INVALID START PRICE\n{e}')

    @property
    def step_price(self):
        try:
            p = self.get_acitvity_table().find('td', id='priceStepUp')
            if p:
                p = re.sub(r'\s', '', dedent_func(p.get_text().strip()).replace(',', '.'))
                p = ''.join([x for x in p if x.isdigit() or x == '.'])
                if len(p) > 0:
                    return round(float(p), 2)
        except ValueError as e:
            logger.error(f'{self.response.url} :: INVALID STEP PRICE\n{e}')

    @property
    def min_price(self):
        try:
            p = self.get_acitvity_table().find('span', id='priceMin')
            if p:
                p = re.sub(r'\s', '', dedent_func(p.get_text().strip()).replace(',', '.'))
                p = ''.join([x for x in p if x.isdigit() or x == '.'])
                if len(p) > 0:
                    return round(float(p), 2)
        except ValueError as e:
            logger.error(f'{self.response.url} :: INVALID START PRICE\n{e}')

    def get_acitvity_table(self):
        return self.soup.find('table', class_='tbl-activity')

    @property
    def deposit(self):
        try:
            p = self.soup.find('strong', text=contains('Сумма задатка'))
            if p:
                p = p.find_next('span').text.strip()
                p = re.sub(r'\s', '', dedent_func(p).replace(',', '.'))
                p = ''.join([x for x in p if x.isdigit() or x == '.'])
                if len(p) > 0:
                    return round(float(p), 2)
        except ValueError as e:
            logger.error(f'{self.response.url} :: INVALID DEPOSIT PRICE\n{e}')

    @property
    def periods(self):
        ...
