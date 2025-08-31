import json
from typing import Optional

from app.utils import logger, Contacts


class Combo:
    def __init__(self, response):
        self.response = response
        self.data = json.loads(response.text)
        self.common_data = self.data['commonInfo']

    @property
    def trading_id(self):
        return self.common_data['eisNumber']

    @property
    def trading_link(self):
        return f'https://tender.lot-online.ru/procedure?procedureNumber={self.trading_id}&lotNumber=1'

    @property
    def trading_type(self):
        type_ = self.common_data['purchaseMethodCode']
        d = {
            'auction': ['smspAuction']
        }
        for k, v in d.items():
            if type_ in v:
                return k
        logger.warning(f'{self.response.url} | Could not parse trading_type={type_}')
        return None

    @property
    def trading_number(self):
        return self.trading_id

    @property
    def trading_form(self):
        return 'open'

    @property
    def trading_org(self):
        return self.data['organization'].get('title') or self.data['organization'].get('shortTitle')

    @property
    def trading_org_inn(self):
        return Contacts.check_inn(self.data['organization'].get('inn'))

    @property
    def trading_org_contacts(self):
        return {
            'email': Contacts.check_email(self.data['organization'].get('contactEmail')),
            'phone': Contacts.check_phone(self.data['organization'].get('contactPhone')),
        }

    @property
    def address(self):
        return self.common_data.get('customerOkato')

    @property
    def lot_number(self):
        return self.common_data.get('lotNumber')

    @property
    def categories(self):
        categories = []
        pn = self.data['productionNomenclatures'][0]
        if okpd := pn.get('okpd2Title'):
            categories.append(okpd)
        if okved := pn.get('okved2Title'):
            categories.append(okved)
        return categories

    @property
    def main_stage(self) -> Optional[list]:
        stages = self.data.get('stages')
        if not stages:
            return

        if len(stages) > 1:
            pass

        return self.main_stage[0]['stageList']

    @property
    def start_date_requests(self):
        return self.main_stage['']

    @property
    def end_date_requests(self):
        ...

    @property
    def start_date_trading(self):
        ...

    @property
    def end_date_trading(self):
        ...

    @property
    def start_price(self):
        ...

    @property
    def step_price(self):
        ...

    @property
    def periods(self):
        ...

    def download_general(self):
        ...

    def download_lot(self):
        ...
