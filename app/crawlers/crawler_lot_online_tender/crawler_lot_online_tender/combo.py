import json
from typing import Optional

from app.db.models import DownloadData
from app.utils import logger, Contacts, DateTimeHelper, make_float


class Combo:
    def __init__(self, response):
        self._step_price = None
        self.response = response
        self.data = json.loads(response.text)
        self.common_data = self.data['commonInfo']

    @property
    def trading_id(self):
        return self.common_data['eisNumber'] or self.common_data['etpNumber']

    @property
    def trading_link(self):
        return f'https://tender.lot-online.ru/procedure?procedureNumber={self.trading_id}&lotNumber=1'

    @property
    def trading_type(self):
        type_ = self.common_data['purchaseCategoryCode']
        d = {
            'auction': ['SmspAuctionCase'],
            'competition': ['SmspCompetitionCase'],
            'offer': ['SmspRFPCase'],
            'rfp': ['PriceRequestCase', 'PurchaseCase', 'SmspRFQCase']
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
    def main_stage_list(self) -> Optional[list]:
        stages = self.data.get('stages')
        if not stages:
            return []

        if len(stages) > 1:
            pass
        return stages[0]['stageList']

    def dates(self) -> dict:
        dates = dict(
            start_date_requests=None,
            end_date_requests=None,
            start_date_trading=None,
            end_date_trading=None,
        )
        for stage in self.main_stage_list:
            date_type = None
            date = stage['date'] + ' ' + (stage.get('time', '') or '')
            if stage['code'] == 'GD_START':
                date_type = 'start_date_requests'
            elif stage['code'] == 'GD_END':
                date_type = 'end_date_requests'
            elif stage['code'] == 'EXECUTION':
                date_type = 'start_date_trading'
                self.step_price = make_float(stage['tradeInfo']['minPriceStep'])
            elif stage['code'] == 'SUMMATION':
                date_type = 'end_date_trading'
            if date_type:
                dates[date_type] = DateTimeHelper.smart_parse(date.strip()).astimezone(DateTimeHelper.moscow_tz)
        return dates

    @property
    def start_price(self):
        return self.common_data['price']

    @property
    def step_price(self):
        return self._step_price

    @step_price.setter
    def step_price(self, value):
        self._step_price = make_float(value)

    @property
    def periods(self):
        return None  # TODO

    def download_general(self):
        notices = self.data.get('notices')
        files = []
        for notice in notices:
            for file in notice.get('fileSignResponse'):
                file_dto = file['fileDTO']
                link = f'https://tender.lot-online.ru/etp/downloadppf?uuid={file_dto["uuid"]}'
                name = file_dto["fileName"]
                files.append(DownloadData(url=link, file_name=name))
        return files

    def download_lot(self):
        return None
