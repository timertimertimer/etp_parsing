from bs4 import BeautifulSoup

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
        return self.soup.find('td', text='Способ проведения процедуры').find_next('td').text


    @property
    def status(self):
        ...

    @property
    def trading_org(self):
        return self.soup.find('td', text='Организатор').find_next('td').text

    @property
    def trading_org_inn(self):
        return None

    @property
    def trading_org_contacts(self):
        return {"email": None, "phone": None}

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
