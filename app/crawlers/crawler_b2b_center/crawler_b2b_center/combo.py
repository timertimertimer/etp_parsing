from bs4 import BeautifulSoup

from app.utils import logger, Contacts, dedent_func, DateTimeHelper, make_float


class Combo:
    def __init__(self, response):
        self.response = response
        self.soup = BeautifulSoup(response.text, 'lxml')

    def download_general(self):
        return []

    def download_lot(self):
        return []

    @property
    def trading_id(self):
        return self.response.url.split('?id=')[1]

    @property
    def trading_link(self):
        return self.response.url

    @property
    def trading_number(self):
        return self.trading_id

    def sposob(self):
        return self.soup.find('td', text='Способ закупки, согласно положению:').find_next('td').get_text(strip=True)

    @property
    def trading_type(self):
        d = {
            'offer': ['Открытый запрос предложений в электронной форме']
        }
        type_ = self.sposob()
        for k, v in d.items():
            if k in type_:
                return v
        logger.warning(f'{self.response.url} | Could not parse trading_type={type_}')
        return None

    @property
    def trading_form(self):
        form = self.sposob()
        if 'открыт' in form:
            return 'open'
        return 'closed'

    def get_trading_org_td(self):
        return self.soup.find('tr', class_='trade-info-organizer-name').find_all('td')[1]

    @property
    def trading_org(self):
        return self.get_trading_org_td().get_text(strip=True)

    @property
    def trading_org_contacts(self):
        email = Contacts.check_email(
            self.soup.find('tr', class_='trade-info-organizer-email').find_all('td')[1].get_text(strip=True)
        )
        phone = Contacts.check_phone(
            self.soup.find('tr', class_='trade-info-organizer-phone').find_all('td')[1].get_text(strip=True)
        )
        return {'email': email, 'phone': phone}

    @property
    def address(self):
        return self.soup.find('tr', class_='trade-info-organizer-fact-address').find_all('td')[1].get_text(strip=True)

    @property
    def short_name(self):
        if headline := self.soup.find('h1', class_='h3', attrs={'itemprop': 'headline'}):
            return dedent_func(headline.find('div', class_='s2').get_text(strip=True))
        logger.warning(f'{self.response.url} | Could not parse short_name={self.short_name}')
        return None

    @property
    def lot_info(self):
        return None

    @property
    def categories(self):
        categories = []
        if okpd2 := self.soup.find('tr', id_='trade-info-okpd2'):
            categories.append(okpd2.find_next('tr').get_text(strip=True))
        if okved2 := self.soup.find('tr', id_='trade-info-okved2'):
            categories.append(okved2.find_next('tr').get_text(strip=True))
        return categories

    @property
    def property_information(self):
        if text := self.soup.find('td', text='Порядок предоставления документации по закупке:'):
            return dedent_func(text.get_text(strip=True))
        return None

    @property
    def start_date_requests(self):
        if date := self.soup.find('td', text='Дата окончания подачи заявок:'):
            return DateTimeHelper.smart_parse(date.get_text(strip=True)).astimezone(DateTimeHelper.moscow_tz)
        logger.warning(f'{self.response.url} | Could not parse start_date_requests={self.start_date_requests}')
        return None

    @property
    def end_date_requests(self):
        if date := self.soup.find('td', text='Дата окончания подачи заявок:'):
            return DateTimeHelper.smart_parse(date.get_text(strip=True)).astimezone(DateTimeHelper.moscow_tz)
        logger.warning(f'{self.response.url} | Could not parse end_date_requests={self.end_date_requests}')
        return None

    @property
    def start_date_trading(self):
        return None

    @property
    def end_date_trading(self):
        return None

    @property
    def start_price(self):
        if price := self.soup.find('td', text='Цена за единицу продукции:'):
            return make_float(price.find_next('td').get_text(strip=True))
        logger.warning(f'{self.response.url} | Could not parse start_price={self.start_price}')
        return None

    @property
    def step_price(self):
        return None  # TODO

    @property
    def periods(self):
        return None  # TODO

    @property
    def trading_org_inn(self):
        if inn := self.soup.find('td', text='ИНН'):
            return Contacts.check_inn(inn.get_text(strip=True))
        logger.warning(f'{self.response.url} | Could not parse trading_org_inn={self.trading_org_inn}')
        return None
