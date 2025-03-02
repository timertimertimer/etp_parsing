import logging
import requests

from general_utils import CheckIfCorrectContactInfo, return_parse_date
from general_utils.db import DBHelper, get_db
from general_utils.models import Counterparty, TradingFloor, LegalCase, DebtorMessage, Auction
from general_utils.models.counterparty import CounterpartyType, CounterpartySRO, CounterpartyDebtorCategory

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")


class Fedresurs:
    BACKEND_URL = 'https://fedresurs.ru/backend'
    HEADERS = {
        'accept': 'application/json, text/plain, */*',
        'cache-control': 'no-cache',
        'pragma': 'no-cache',
        'referer': 'https://fedresurs.ru/',
        'sec-ch-ua': '"Not(A:Brand";v="99", "Google Chrome";v="133", "Chromium";v="133"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.0.0 Safari/537.36'
    }

    def __init__(self):
        self._guid = None
        self.session = requests.Session()
        self.session.headers.update(self.HEADERS)
        self.db_session = get_db()

    def make_request(self, *args, **kwargs):
        params = kwargs.get('params', {})
        url = args[0] or kwargs.get('url') or self.BACKEND_URL
        headers = kwargs.get('headers', self.HEADERS)
        response = self.session.get(url, params=params, headers=headers)
        try:
            response.raise_for_status()
        except Exception as e:
            raise e
        return response.json()

    def search(self, search_string: str, url: str = None, path: str = '', params: dict = None, headers: dict = None):
        data = self.make_request(
            f'{url or self.BACKEND_URL}{f"/{path}" if len(path) else ""}',
            params={"searchString": search_string, 'limit': 15, 'offset': 0, 'isActive': 'true'} | (params or {}),
            headers=headers or self.HEADERS
        )
        if not (data := data.get('pageData')):
            logger.warning(f'Not found guid for {search_string}')
            return
        return data


class BankrotFedresurs(Fedresurs):
    BACKEND_URL = 'https://bankrot.fedresurs.ru/backend'
    HEADERS = Fedresurs.HEADERS | {'referer': 'https://bankrot.fedresurs.ru/'}

    def __init__(self):
        super().__init__()
        self.session.headers.update(self.HEADERS)


class CounterpartyFedresurs(Fedresurs):
    PATH = ''

    def __init__(self, counterparty: Counterparty):
        super().__init__()
        self.counterparty = counterparty

    @property
    def guid(self):
        if not self._guid:
            self.guid = self._get_guid(self.counterparty.inn)
        return self._guid

    @guid.setter
    def guid(self, value):
        self._guid = value

    def _get_guid(self, search_string: str):
        data = self.search(search_string, path='fast')
        if data:
            return data[0]['guid']
        else:
            logger.warning(f'Not found guid for {search_string}')

    def parse(self):
        if not self.counterparty.fedresurs_url:
            if not self.main():
                logger.error(f'Not found {self.counterparty}')
                return
            self.get_main_info()
            if counterparty := DBHelper.get_counterparty(
                    self.db_session, self.counterparty.inn, self.counterparty.name, self.counterparty.short_name
            ):
                self.counterparty.id = counterparty.id
        self.bankruptcy()
        DBHelper.store_model(self.counterparty, self.db_session)
        if not self.counterparty.sro_memberships:
            self.sro_membership()

    def main(self) -> str:
        if self.guid:
            data = self.make_request(f'{self.BACKEND_URL}/{self.guid}/main')
            self.counterparty.short_name = data.get('name')
            return data
        else:
            logger.warning(f'No guid provided for {self.counterparty}')

    def get_main_info(self, guid: str = None, new_sro: Counterparty = None):  # Общая информация
        data = self.make_request(
            f'{self.BACKEND_URL if not new_sro else CompanyFedresurs.BACKEND_URL}/{guid or self.guid}')
        counterparty = new_sro or self.counterparty
        counterparty.inn = data.get('inn') or self.counterparty.inn
        counterparty.kpp = data.get('kpp')
        counterparty.ogrn = data.get('ogrn')
        counterparty.snils = data.get('snils')
        counterparty.name = data.get('fullName')
        counterparty.email = (
                CheckIfCorrectContactInfo.check_email(data.get('contacts', {}).get('email')) or counterparty.email
        )
        counterparty.phone = (
                CheckIfCorrectContactInfo.check_phone(data.get('contacts', {}).get('phone')) or counterparty.phone
        )
        counterparty.url = data.get('tradePlace', {}).get('site') or data.get('contacts', {}).get('site')
        counterparty.fedresurs_url = (
            f'https://fedresurs.ru/{"companies" if self.counterparty.type == "legal_entity" else "persons"}/{self.guid}'
        )
        address_str = data.get('address') or data.get('addressEgrul')
        if address_str:
            address = (
                    DBHelper.get_or_create_address(address_str, self.db_session) or
                    self.counterparty.address
            )
            counterparty.address_id = address.id

    def sro_membership(self):
        data = self.make_request(
            f'{self.BACKEND_URL}/{self.guid}/sro-membership', params={'limit': 15, 'offset': 0, 'isActive': True}
        )
        if not (data := data.get('pageData')) and isinstance(self, PersonFedresurs):
            data = self.make_request(
                f'{self.BACKEND_URL}/{self.guid}/sro-membership-au', params={'limit': 15, 'offset': 0, 'isActive': True}
            )
            if not (data := data.get('pageData')):
                logger.info(f'Not found sro data for {self.counterparty}')
                return
        for membership in data:
            sro_name = membership['sro']['name']
            if not DBHelper.get_counterparty_sro(
                    counterparty_id=self.counterparty.id,
                    sro_counterparty_short_name=sro_name,
                    session=self.db_session
            ):
                sro = DBHelper.get_counterparty(short_name=sro_name, session=self.db_session)
                if not sro:
                    sro = Counterparty(short_name=sro_name, type=CounterpartyType.legal_entity)
                    self.get_main_info(membership['sro']['guid'], sro)
                    sro = DBHelper.store_model(sro, self.db_session)
                counterparty_sro = CounterpartySRO(
                    counterparty_id=self.counterparty.id,
                    sro_id=sro.id,
                    message_number=membership.get('messageInclude', {}).get('number'),
                    activity_type=membership['sroActivities'][0],
                    entered_at=return_parse_date(membership['dateInclude'], '%Y-%m-%dT%H:%M:%S')
                )
                DBHelper.store_model(counterparty_sro, self.db_session)

    def bankruptcy(self):
        data = self.make_request(f'{self.BACKEND_URL}/{self.guid}/bankruptcy')
        if not (data := data.get('pageData')):
            logger.info(f'Not found bankruptcy data for {self.counterparty}')
            return
        for legal_case in data['legalCases']:
            guid = legal_case['guid']
            number = legal_case['number']
            if not (legal_case := DBHelper.get_legal_case(number=number, session=self.db_session)):
                legal_case = LegalCase(number=number)
            lgf = LegalCaseFedresurs(legal_case, guid)
            lgf.parse()
            for message in legal_case['lastPublications']:
                d_m = DebtorMessage()
                d_m.legal_case_id = legal_case.id
                d_m.number = message['number']
                d_m.type = message['typeName']
                d_m.fedresurs_url = f'https://fedresurs.ru/bankruptmessages/{message["guid"]}'
                data = self.make_request(f'{self.BACKEND_URL}/bankruptmessages/{message["guid"]}')
                d_m.content = data['content']['messageInfo']['messageContent']['text']
                DBHelper.store_model(d_m, self.db_session)


class PersonFedresurs(CounterpartyFedresurs):
    PATH = 'persons'
    BACKEND_URL = f'https://fedresurs.ru/backend/{PATH}'

    def __init__(self, counterparty: Counterparty):
        super().__init__(counterparty)
        self.counterparty.type = CounterpartyType.individual

    def parse(self):
        data = self.main()
        if not data:
            logger.error(f'Not found {self.counterparty}')
            return
        if 'IndividualEntrepreneur' in data['roles']:
            self.get_individual_entrepreneurs()
        self.get_main_info()
        self.bankruptcy()
        DBHelper.store_model(self.counterparty, self.db_session)
        self.sro_membership()

    def get_individual_entrepreneurs(self):
        data = self.make_request(f'{self.BACKEND_URL}/{self.guid}/individual-entrepreneurs',
                                 params={'limit': 1, 'offset': 0})
        if not (data := data.get('pageData')):
            logger.error(f'Not found ogrnip data for {self.counterparty}')
            return
        data = data[0]
        self.counterparty.ogrnip = data['ogrnip']
        return data


class CompanyFedresurs(CounterpartyFedresurs):
    PATH = 'companies'
    BACKEND_URL = f'https://fedresurs.ru/backend/{PATH}'

    def __init__(self, counterparty: Counterparty):
        super().__init__(counterparty)
        self.counterparty.type = CounterpartyType.legal_entity


class TradingFloorFedresurs(CompanyFedresurs):

    def __init__(self, trading_floor: TradingFloor):
        self.trading_floor = trading_floor
        self.counterparty = trading_floor.counterparty or Counterparty(name=trading_floor.name)
        super().__init__(self.counterparty)

    @property
    def guid(self):
        if not self._guid:
            self.guid = self._get_guid(self.counterparty.name)
        return self._guid

    @guid.setter
    def guid(self, value):
        self._guid = value

    def _get_guid(self, search_string: str):
        data = self.search(
            search_string, url=f'{BankrotFedresurs.BACKEND_URL}/tradeplaces', headers=BankrotFedresurs.HEADERS
        )
        if data:
            return data[0]['operator']['guid']

    def parse(self):
        if not self.counterparty.fedresurs_url:
            if not self.main():
                logger.error(f'Not found {self.counterparty}')
                return
            self.get_main_info()
            if counterparty := DBHelper.get_counterparty(
                    self.db_session, self.counterparty.inn, self.counterparty.name, self.counterparty.short_name
            ):
                self.counterparty.id = counterparty.id
            DBHelper.store_model(self.counterparty, self.db_session)
        self.trading_floor.counterparty_id = self.counterparty.id
        if not self.counterparty.sro_memberships:
            self.sro_membership()
        self.bankruptcy()
        DBHelper.store_model(self.trading_floor, self.db_session)


class AuctionFedersurs(Fedresurs):
    BACKEND_URL = 'https://fedresurs.ru/backend/biddings'

    def __init__(self, auction: Auction):
        super().__init__()
        self.auction = auction

    @property
    def guid(self):
        if not self._guid:
            self.guid = self._get_guid(self.auction.number)
        return self._guid

    @guid.setter
    def guid(self, value):
        self._guid = value

    def _get_guid(self, search_string: str):
        data = self.search(search_string, params={'onlyAvailableToParticipate': True})
        if not data:
            logger.warning(f'Not found guid for {search_string}')
            return
        return data[0]['guid']

    def parse(self):
        if not self.guid:
            logger.warning(f'Not found guid for {self.auction}')
            return
        debtor_category_value = self.get_main_info()
        # DBHelper.store_model(self.legal_case, self.db_session)
        # self.parse_debtor_category(debtor_category_value)

    def get_main_info(self, guid: str = None):  # Общая информация
        data = self.make_request(f'{self.BACKEND_URL}/{guid or self.guid}')
        legal_case_guid = data.get('legalCase', {}).get('guid')
        main_message_guid = data.get('message', {}).get('guid')
        messages = self.get_auction_messages()
        self.parse_messages([main_message_guid] + messages)

    def get_auction_messages(self):
        data = self.make_request(f'{self.BACKEND_URL}/{self.guid}/messages', params={'limit': 3, 'offset': 0})
        if not (data := data.get('pageData')):
            logger.info(f'Not found messages for {self.auction}')
            return
        return [message['guid'] for message in data]

    def parse_messages(self, messages):
        for message in messages:
            data = self.make_request(f'{BankrotMessageFedresurs}/{message}')
            legal_case_number = data.get('bankrupt', {}).get('legalCaseNumber')
            legal_case: LegalCase = DBHelper.get_legal_case(number=legal_case_number, session=self.db_session)
            if not (legal_case and legal_case.fedresurs_url):
                legal_case = LegalCase(number=legal_case_number)
            lgf = LegalCaseFedresurs(legal_case)
            lgf.parse()
            message_number = data.get('number')
            if not DBHelper.get_debtor_message(message_number, self.db_session):
                new_message = DebtorMessage(
                    number=data.get('number'),
                    type=data.get('typeName'),
                )

class BankrotMessageFedresurs(Fedresurs):
    BACKEND_URL = 'https://fedresurs.ru/backend/bankruptcy-messages'

    def __init__(self, message: DebtorMessage):
        super().__init__()
        self.message = message

class LegalCaseFedresurs(Fedresurs):
    BACKEND_URL = 'https://fedresurs.ru/backend/legal-cases'

    def __init__(self, legal_case: LegalCase, guid: str = None):
        super().__init__()
        self.legal_case = legal_case
        self.guid = guid

    @property
    def guid(self):
        if not self._guid:
            self.guid = self._get_guid(self.legal_case.number)
        return self._guid

    @guid.setter
    def guid(self, value):
        self._guid = value

    def _get_guid(self, search_string: str):
        data = self.search(search_string, url=AuctionFedersurs.BACKEND_URL, params={'onlyAvailableToParticipate': True})
        if not data:
            logger.warning(f'Not found guid for {search_string}')
            return
        auction_guid = data[0]['guid']
        data = self.make_request(f'{AuctionFedersurs.BACKEND_URL}/{auction_guid}')
        return data.get('legalCase', {}).get('guid')

    def parse(self):
        if not self.guid:
            logger.warning(f'Not found guid for {self.legal_case}')
            return
        debtor_category_value = self.get_main_info()
        DBHelper.store_model(self.legal_case, self.db_session)
        self.parse_debtor_category(debtor_category_value)

    def get_main_info(self, guid: str = None):  # Общая информация
        data = self.make_request(f'{self.BACKEND_URL}/{guid or self.guid}')
        self.legal_case.name = data.get('status', {}).get('name').strip()
        self.legal_case.number = CheckIfCorrectContactInfo.check_case_number(data.get('number'))
        self.legal_case.court_name = data.get('courtName').strip()
        self.legal_case.fedresurs_url = f'https://fedresurs.ru/legal-cases/{self.guid}'
        return data.get('bankruptCategory', {}).get('name')

    def parse_debtor_category(self, debtor_category_value):
        debtor_category = DBHelper.get_or_create_debtor_category(debtor_category_value, self.db_session)
        if not DBHelper.get_counterparty_debtor_category(
                self.legal_case.auction.debtor.id, debtor_category.id, self.db_session
        ):
            counterparty_debtor_category = CounterpartyDebtorCategory(
                counterparty_id=self.legal_case.auction.debtor.id,
                debtor_category_id=debtor_category.id
            )
            DBHelper.store_model(counterparty_debtor_category, self.db_session)


def parse_counterparties():
    counterparties = DBHelper.get_all(Counterparty)
    for counterparty in counterparties:
        if counterparty.inn:
            if len(counterparty.inn) > 10:
                fed_client = PersonFedresurs(counterparty)
            else:
                fed_client = CompanyFedresurs(counterparty)
            fed_client.parse()


def parse_trading_floors():
    trading_floors = DBHelper.get_all(TradingFloor)
    for trading_floor in trading_floors:
        fed_client = TradingFloorFedresurs(trading_floor)
        fed_client.parse()


def parse_auctions():
    auctions = DBHelper.get_all(Auction)
    for auction in auctions:
        if auction.legal_case and auction.legal_case.fedresurs_url:
            continue
        fed_client = AuctionFedersurs(auction)
        fed_client.parse()


def parse_counterparty(inn: str):
    counterparty = DBHelper.get_counterparty(session=get_db(), inn=inn)
    fed_client = CompanyFedresurs(counterparty)
    fed_client.parse()


if __name__ == '__main__':
    # parse_counterparties()
    parse_auctions()
    # parse_trading_floors()
    # parse_counterparty('1656057203')
