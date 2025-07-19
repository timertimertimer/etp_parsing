from bs4 import BeautifulSoup

from app.db.models import DownloadData
from app.utils import dedent_func, contains, format_time, make_float


class Combo:
    def __init__(self, response):
        self.response = response
        self.soup = BeautifulSoup(response)

    @property
    def trading_id(self):
        return self.soup.find('span', class_='identifier').text

    @property
    def trading_link(self):
        return self.response.url

    @property
    def trading_number(self):
        return self.trading_id

    @property
    def trading_type(self):
        type_ = self.soup.find('td', text='Способ проведения процедуры').find_next('td').text
        if 'аукцион' in type_.lower():
            return 'auction'
        else:
            return None # TODO

    @property
    def trading_form(self):
        form = self.soup('td', text='Форма торгов').find_next('td')
        if 'открытый' in form.lower():
            return 'open'
        else:
            return 'closed' # TODO

    @property
    def trading_org(self):
        return dedent_func(self.soup.find('td', text='Организатор').find_next('td').text)

    @property
    def trading_org_inn(self):
        return None

    @property
    def trading_org_contacts(self):
        return {"email": None, "phone": None}

    @property
    def msg_number(self):
        return None

    @property
    def case_number(self):
        return None

    @property
    def debtor_inn(self):
        return None

    @property
    def address(self):
        ... # TODO

    @property
    def arbit_manager(self):
        return None

    @property
    def arbit_manager_org(self):
        return None

    @property
    def arbit_manager_inn(self):
        return None

    @property
    def status(self):
        mapping = {
            'Завершена процедура': 'ended'
        } # TODO
        return mapping.get(self.soup.find('div', class_=contains('rangeStage')).text)

    @property
    def lot_id(self):
        return self.soup.find('span', class_='identifier').text

    @property
    def lot_link(self):
        return self.response.url

    @property
    def lot_number(self):
        return self.soup.find('td', text="Номер лота").text

    @property
    def short_name(self):
        return dedent_func(self.soup.find('div', class_=contains('etpp-small')).text)

    @property
    def property_information(self):
        return None # TODO

    @property
    def lot_info(self):
        return dedent_func(self.soup.find('td', text='предмет торгов').text)

    @property
    def start_date_requests(self):
        return format_time(self.soup.find('span', text=contains('Начало срока подачи заявок')).text)

    @property
    def end_date_requests(self):
        return format_time(self.soup.find('span', text=contains('Окончание срока подачи заявок')).text)

    @property
    def start_date_trading(self):
        return format_time(self.soup.find('span', text=contains('Начало проведение торгов')).text)

    @property
    def end_date_trading(self):
        return format_time(self.soup.find('span', text=contains('Окончание проведения торгов')).text)

    @property
    def start_price(self):
        return make_float(self.soup.find('td', text='Начальная (минимальная) цена').text)

    @property
    def step_price(self):
        return make_float(self.soup.find('td', text='Шаг торгов').text)

    @property
    def periods(self):
        return None  # TODO

    def download_files(self):
        download_data = []
        links = self.soup.find('table', text=contains('Сообщения').find_all('a'))
        for link in links:
            url = link.get('href')
            name = link.get('value')
            download_data.append(DownloadData(file_name=name, url=url))
        return download_data