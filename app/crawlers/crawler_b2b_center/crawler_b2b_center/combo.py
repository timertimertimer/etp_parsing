from bs4 import BeautifulSoup

from app.utils import logger, Contacts


class Combo:
    def __init__(self, response):
        self.response = response
        self.soup = BeautifulSoup(response.text, 'lxml')

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
