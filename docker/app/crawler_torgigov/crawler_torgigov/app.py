import logging

from general_utils import dedent_func, CheckIfCorrectContactInfo, return_parse_date
from general_utils.models import DownloadData

logger = logging.getLogger(__name__)


class Combo:
    def __init__(self, data):
        self.data = data

    def get_lots(self):
        return self.data['lots']

    def download_general(self):
        files = list()
        attachments = self.data.get('attachments', [])
        for file in attachments:
            link = f'https://torgi.gov.ru/new/file-store/v1/{file["fileId"]}'
            name = file['fileName']
            files.append(DownloadData(url=link, file_name=name))
        return files

    def download_lot(self, lot):
        files = list()
        attachments = lot.get('attachments', [])
        for file in attachments:
            link = f'https://torgi.gov.ru/new/file-store/v1/{file["fileId"]}'
            name = file['fileName']
            files.append(DownloadData(url=link, file_name=name))
        return files

    @property
    def trading_id(self):
        return self.data['id']

    @property
    def trading_link(self):
        return f'https://torgi.gov.ru/new/public/notices/view/{self.trading_id}'

    @property
    def trading_number(self):
        return self.trading_id

    @property
    def trading_type(self):
        type_value = self.data['biddForm']['name']
        if type_value == 'Сообщение о предоставлении (реализации)':
            return
        d = {
            'auction': ['Электронный аукцион', 'Аукцион'],
            'offer': ['Публичное предложение', 'Публичное предложение (цессия)'],
            'competition': ['Электронный конкурс', 'Конкурс']
        }
        for key in d:
            if type_value in d[key]:
                return key
        logger.error(f'{self.trading_link} :: Unknown trading type {type_value}')

    @property
    def trading_form(self):
        return 'open'

    @property
    def trading_org(self):
        return dedent_func(self.data['bidderOrg']['name'])

    @property
    def trading_org_inn(self):
        return CheckIfCorrectContactInfo.check_inn(self.data['bidderOrg']['inn'])

    @property
    def trading_org_contacts(self):
        return {
            'email': CheckIfCorrectContactInfo.check_email(self.data['bidderOrg']['email']),
            'phone': CheckIfCorrectContactInfo.check_phone(self.data['bidderOrg']['tel'])
        }

    @property
    def debtor_inn(self):
        return

    def get_address(self, lot):
        return lot.get('estateAddress') or lot.get('rightHolderOrg', {}).get('legalAddress')

    @property
    def arbit_manager(self):
        return self.data['bidderOrg']['contPerson']

    @property
    def status(self):
        form_value = self.data['noticeStatus']
        d = {
            'active': ['APPLICATIONS_SUBMISSION', 'PUBLISHED'],
            'pending': ['DETERMINING_WINNER'],
            'ended': ['CANCELED', 'COMPLETED']
        }
        for key in d:
            if form_value in d[key]:
                return key
        logger.error(f'{self.trading_link} :: Unknown trading form {form_value}')

    def get_category(self, lot):
        return lot['category']['name']

    def get_lot_id(self, lot):
        return lot['id']

    def get_lot_link(self, lot):
        return f'https://torgi.gov.ru/new/public/lots/lot/{self.get_lot_id(lot)}/(lotInfo:info)?fromRec=false#lotInfoSection-info'

    def get_lot_number(self, lot):
        return lot['lotNumber']

    def get_short_name(self, lot):
        return lot['lotName']

    def get_lot_info(self, lot):
        return lot['lotDescription']

    def get_deposit(self, lot):
        return lot['deposit']

    @property
    def property_information(self):
        return

    @property
    def start_date_requests(self):
        return return_parse_date(self.data['biddStartTime'])

    @property
    def end_date_requests(self):
        return return_parse_date(self.data['biddEndTime'])

    @property
    def start_date_trading(self):
        if date := self.data.get('auctionStartDate'):
            return return_parse_date(date)

    @property
    def end_date_trading(self):
        date = None
        if self.trading_type == 'offer':
            date = self.data['auctionStartDate']
        elif self.trading_type in ['auction', 'competition']:
            for el in self.data['attributes']:
                if el['fullName'] == 'Дата, время подведения результатов торгов':
                    date = el.get('value')
        else:
            pass
        if date:
            return return_parse_date(date)

    def get_start_price(self, lot):
        return lot.get('priceMin')

    def get_step_price(self, lot):
        return lot.get('priceStep')

    @property
    def periods(self):
        return
