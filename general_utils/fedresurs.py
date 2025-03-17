import logging
import requests

from general_utils import CheckIfCorrectContactInfo, return_parse_date
from general_utils.models import Counterparty, TradingFloor, LegalCase
from general_utils.models.counterparty import CounterpartyType

logger = logging.getLogger(__name__)
retry_count = 5


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
        self.data = dict()
        self.session = requests.Session()
        self.session.headers.update(self.HEADERS)

    def make_request(self, *args, **kwargs):
        params = kwargs.get('params', {})
        url = args[0] or kwargs.get('url') or self.BACKEND_URL
        headers = kwargs.get('headers', self.HEADERS)
        for i in range(retry_count):
            try:
                response = self.session.get(url, params=params, headers=headers, timeout=15)
                response.raise_for_status()
                break
            except (requests.exceptions.ConnectionError, requests.exceptions.ReadTimeout) as e:
                if i + 1 == retry_count:
                    logger.error(f'Connection error: {e}. All attempts failed')
                    raise e
                logger.warning(f'Connection error: {e}. Trying again. Attempt {i + 1}')
        return response.json()

    def search(self, search_string: str, url: str = None, path: str = '', params: dict = None, headers: dict = None):
        data = self.make_request(
            f'{url or self.BACKEND_URL}{f"/{path}" if len(path) else ""}',
            params={"searchString": search_string, 'limit': 15, 'offset': 0} | (params or {}),
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
    BACKEND_URL = f'https://fedresurs.ru/backend/{PATH}'

    def __init__(self, inn: str = None, name: str = None, guid: str = None, data: dict = None):
        super().__init__()
        self.data = self.data or data or dict()
        self.data['inn'] = self.data.get('inn', inn)
        self.data['name'] = self.data.get('name', name)
        self.data['guid'] = guid or self.data.get('guid') or self.get_guid()
        self.data['publications'] = list()

    def get_guid(self):
        search_string = self.data['inn'] or self.data['name']
        if not search_string:
            return
        data = self.search(search_string, path='fast')
        if not data:
            return
        self.data['guid'] = data[0]['guid']
        return self.data['guid']

    def parse(self) -> None:
        if not self.main():
            logger.error(f'Not found {self.data.get("name") or self.data.get("inn")}')
            return
        self.parse_main_info()

    def main(self) -> dict | None:
        if self.data['guid']:
            data = self.make_request(f'{self.BACKEND_URL}/{self.data["guid"]}/main')
            self.data['short_name'] = data.get('name')
            return data

    def parse_main_info(self) -> None:
        data = self.make_request(f'{self.BACKEND_URL}/{self.data["guid"]}')
        self.data['inn'] = data.get('inn')
        self.data['kpp'] = data.get('kpp')
        self.data['ogrn'] = data.get('ogrn')
        self.data['okopf'] = data.get('okopf', {}).get('code')
        self.data['snils'] = data.get('snils')
        self.data['name'] = data.get('fullName')
        self.data['email'] = CheckIfCorrectContactInfo.check_email(data.get('contacts', {}).get('email'))
        self.data['phone'] = CheckIfCorrectContactInfo.check_phone(data.get('contacts', {}).get('phone'))
        self.data['url'] = data.get('tradePlace', {}).get('site') or data.get('contacts', {}).get('site')
        self.data['fedresurs_url'] = f'https://fedresurs.ru/{self.PATH}/{self.data["guid"]}'
        self.data['address'] = data.get('address') or data.get('addressEgrul')

    def parse_sro_membership(self) -> None:
        data = self.make_request(
            f'{self.BACKEND_URL}/{self.data["guid"]}/sro-membership',
            params={'limit': 15, 'offset': 0, 'isActive': True}
        )
        if not (data := data.get('pageData')) and isinstance(self, PersonFedresurs):
            data = self.make_request(
                f'{self.BACKEND_URL}/{self.data["guid"]}/sro-membership-au',
                params={'limit': 15, 'offset': 0, 'isActive': True}
            )
            if not (data := data.get('pageData')):
                return
        memberships = list()
        for membership in data:
            sro = CompanyFedresurs(data=dict(
                guid=membership['sro']['guid'], type=CounterpartyType.legal_entity, short_name=membership['sro']['name']
            ))
            sro.parse_main_info()
            sro.data['message_number'] = membership.get('messageInclude', {}).get('number')
            sro.data['activity_type'] = membership.get('sroActivities', [None])[0]
            sro.data['entered_at'] = return_parse_date(membership['dateInclude'])
            memberships.append(sro.data)
        self.data['sro_memberships'] = memberships

    def parse_bankruptcy(self) -> list[dict] | None:
        data = self.make_request(f'{self.BACKEND_URL}/{self.data["guid"]}/bankruptcy')
        if not (data := data.get('legalCases')):
            return
        legal_cases = list()
        for legal_case in data:
            guid = legal_case['guid']
            number = legal_case['number']
            lgf = LegalCaseFedresurs(number, guid)
            lgf.parse()
            # messages = list()
            for message in legal_case['lastPublications']:
                if 'reportTypeName' in message:
                    continue
                # bmf = BankrotMessageFedresurs(message["guid"])
                # bmf.parse()
                # messages.append({'message': bmf.data, 'files': bmf.files})
            # legal_cases.append({'case': lgf.data, 'messages': messages})
            legal_cases.append(lgf.data)
        self.data['legal_cases'] = legal_cases
        return legal_cases

    def parse_publications(self):
        data = self.make_request(
            f'{self.BACKEND_URL}/{self.data["guid"]}/publications', params={'limit': 3, 'offset': 0}
        )
        if not (data := data.get('pageData')):
            return
        for publication in data:
            if publication['publicationType'] != 'BankruptMessage' or publication['isLocked']:
                continue
            bmf = BankrotMessageFedresurs(publication['guid'])
            bmf.parse()
            self.data['publications'].append(bmf.data)


class PersonFedresurs(CounterpartyFedresurs):
    PATH = 'persons'
    BACKEND_URL = f'https://fedresurs.ru/backend/{PATH}'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.data["type"] = CounterpartyType.individual

    def parse(self) -> None:
        if not (data := self.main()):
            logger.error(f'Not found {self.data.get("name") or self.data.get("inn")}')
            return
        self.parse_main_info()
        if 'IndividualEntrepreneur' in data['roles']:
            self.parse_ogrnip()

    def parse_ogrnip(self) -> None:
        data = self.make_request(
            f'{self.BACKEND_URL}/{self.data["guid"]}/individual-entrepreneurs', params={'limit': 1, 'offset': 0}
        )
        if not (data := data.get('pageData')):
            logger.error(f'Not found ogrnip data for {self.data["name"]}')
            return
        data = data[0]
        self.data["ogrnip"] = data['ogrnip']


class CompanyFedresurs(CounterpartyFedresurs):
    PATH = 'companies'
    BACKEND_URL = f'https://fedresurs.ru/backend/{PATH}'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.data["type"] = CounterpartyType.legal_entity


class ArbitrManagerFedresurs(PersonFedresurs):
    def get_guid(self) -> str | None:
        search_string = self.data.get("inn") or self.data.get("name")
        if search_string:
            data = self.search(
                search_string, url=f'{BankrotFedresurs.BACKEND_URL}/arbitrmanagers',
                headers={'referer': 'https://bankrot.fedresurs.ru/'}
            )
            if data:
                if len(data) > 1:
                    return
                self.data["guid"] = data[0]['guid']
                return self.data["guid"]


class PersonOrganizerFedresurs(PersonFedresurs):
    def get_guid(self):
        search_string = self.data.get("inn") or self.data.get("name")
        data = self.search(
            search_string, url=f'{BankrotFedresurs.BACKEND_URL}/prsnTradeOrgs',
            headers={'referer': 'https://bankrot.fedresurs.ru/'}
        )
        if data:
            if len(data) > 1:
                return
            self.data["guid"] = data[0]['guid']
            return self.data["guid"]


class CompanyOrganizerFedresurs(CompanyFedresurs):
    def get_guid(self):
        search_string = self.data.get("inn") or self.data.get("name")
        data = self.search(
            search_string, url=f'{BankrotFedresurs.BACKEND_URL}/cmpTradeOrgs',
            headers={'referer': 'https://bankrot.fedresurs.ru/'}
        )
        if data:
            if len(data) > 1:
                return
            self.data["guid"] = data[0]['guid']
            return self.data["guid"]


class TradingFloorFedresurs(CompanyFedresurs):

    def get_guid(self):
        search_string = self.data['name']
        data = self.search(
            search_string, url=f'{BankrotFedresurs.BACKEND_URL}/tradeplaces', headers=BankrotFedresurs.HEADERS
        )
        if data:
            self.data["guid"] = data[0]['operator']['guid']
            return self.data["guid"]

    def parse(self) -> dict | None:
        if not self.main():
            logger.error(f'Not found {self.data["name"]}')
            return
        self.parse_main_info()
        self.parse_sro_membership()
        return self.data


class BankrotMessageFedresurs(Fedresurs):
    BACKEND_URL = 'https://fedresurs.ru/backend/bankruptcy-messages'

    def __init__(self, guid: str):
        super().__init__()
        self.data["guid"] = guid

    def parse(self) -> None:
        data = self.make_request(f'{self.BACKEND_URL}/{self.data["guid"]}')
        self.data['number'] = data['number']
        self.data['type'] = data['messageType']
        try:
            self.data['content'] = data['content']['messageInfo']['messageContent'].get('text')
        except Exception as e:
            pass
        legal_case_number = data['bankrupt'].get('legalCaseNumber')
        self.data['legal_case_number'] = CheckIfCorrectContactInfo.check_case_number(legal_case_number.strip()) if legal_case_number else None
        self.data['fedresurs_url'] = f'https://fedresurs.ru/bankruptmessages/{self.data["guid"]}'
        self.data['published_at'] = return_parse_date(data['datePublish'])
        files = list()
        for doc in data['docs']:
            files.append(dict(
                name=doc['name'].strip(), url=f'{Fedresurs.BACKEND_URL}/bankruptcy-message-docs/{doc["guid"].strip()}'
            ))
        self.data['files'] = files


class LegalCaseFedresurs(Fedresurs):
    BACKEND_URL = 'https://fedresurs.ru/backend/legal-cases'

    def __init__(self, case_number: str = None, guid: str = None):
        super().__init__()
        self.data['number'] = case_number
        self.data["guid"] = guid or self.get_guid()

    def get_guid(self):
        data = self.search(
            self.data['number'], url=AuctionFedresurs.BACKEND_URL, params={'onlyAvailableToParticipate': True}
        )
        if not data:
            return
        auction_guid = data[0]['guid']
        data = self.make_request(f'{AuctionFedresurs.BACKEND_URL}/{auction_guid}')
        return data.get('legalCase', {}).get('guid')

    def parse(self) -> str | None:
        if not self.data["guid"]:
            return
        data = self.make_request(f'{self.BACKEND_URL}/{self.data["guid"]}')
        self.data['status'] = data.get('status', {}).get('code')
        self.data['number'] = CheckIfCorrectContactInfo.check_case_number(data.get('number'))
        self.data['court_name'] = data.get('courtName').strip()
        self.data['fedresurs_url'] = f'https://fedresurs.ru/legalcases/{self.data["guid"]}'
        self.data['debtor_category'] = data.get('bankruptCategory', {}).get('code')


class AuctionFedresurs(Fedresurs):
    BACKEND_URL = 'https://fedresurs.ru/backend/biddings'

    def __init__(self, trading_id: str, trading_number: str, trading_floor_name: str, case_number: str):
        super().__init__()
        self.data['trading_id'] = trading_id
        self.data['trading_number'] = trading_number
        self.data['trading_floor_name'] = trading_floor_name
        self.data['case_number'] = case_number

    def get_guid(self):
        if self.data.get('guid'):
            return self.data['guid']
        for search_string in (
                self.data['trading_id'], self.data['trading_number'], self.data['case_number']
        ):
            if not search_string:
                continue
            data = self.search(search_string, params={'onlyAvailableToParticipate': True})
            if not data:
                continue
            for data_ in data:
                if data_['tradePlace']['name'].strip() == self.data['trading_floor_name'].strip():
                    self.data['guid'] = data_['guid']
                    return data_['guid']
        return

    def parse(self):
        if not self.data["guid"]:
            return
        self.parse_main_info()

    def parse_main_info(self):
        data = self.make_request(f'{self.BACKEND_URL}/{self.data["guid"]}')
        self.data['arbit_manager'] = data.get('arbitrManager', {}).get('name')
        self.data['arbit_manager_inn'] = data.get('arbitrManager', {}).get('inn')
        self.data['debtor_inn'] = data.get('debtor', {}).get('inn')

    def get_messages(self, guid: str = None):
        data = self.make_request(f'{self.BACKEND_URL}/{guid or self.data["guid"]}')
        main_message_guid = data.get('message', {}).get('guid')
        self.legal_case_guid = data.get('legalCase', {}).get('guid')
        messages = []
        return [main_message_guid] + messages

    def get_auction_messages(self):
        data = self.make_request(f'{self.BACKEND_URL}/{self.data["guid"]}/messages', params={'limit': 3, 'offset': 0})
        if not (data := data.get('pageData')):
            logger.info(f'Not found messages for {self.data["guid"]}')
            return
        return [message['guid'] for message in data]


def parse_counterparties():
    from general_utils.db import DBHelper
    counterparties = DBHelper.get_all(Counterparty)
    for counterparty in counterparties:
        if counterparty.inn:
            if len(counterparty.inn) > 10:
                fed_client = PersonFedresurs(counterparty.inn)
            else:
                fed_client = CompanyFedresurs(counterparty.inn)
            fed_client.parse()


def parse_trading_floors():
    from general_utils.db import DBHelper
    trading_floors = DBHelper.get_all(TradingFloor)
    for trading_floor in trading_floors:
        fed_client = TradingFloorFedresurs(name=trading_floor.file_name)
        trading_floor_counterparty_data = fed_client.parse()
        if trading_floor_counterparty_data:
            trading_floor_counterparty_data, _ = trading_floor_counterparty_data
            counterparty = DBHelper.store_counterparty_from_dict(trading_floor_counterparty_data, Counterparty)
            trading_floor.counterparty_id = counterparty.id
            DBHelper.store_model(trading_floor)


def parse_legal_cases():
    from general_utils.db import DBHelper
    legal_cases = DBHelper.get_all(LegalCase)
    for legal_case in legal_cases:
        if legal_case.fedresurs_url:
            continue
        fed_client = LegalCaseFedresurs(case_number=legal_case.number)
        fed_client.parse()


def parse_counterparty(inn: str):
    from general_utils.db import DBHelper
    counterparty = DBHelper.get_counterparty(inn=inn)
    fed_client = CompanyFedresurs(counterparty)
    fed_client.parse()


def test():
    auction_client = AuctionFedresurs(
        case_number='А73-7136/2024',
        trading_id='104258896',
        trading_number='13592-ОТПП',
        trading_floor_name='"Аукционы Сибири"'
    )
    auction_client.get_guid()


if __name__ == '__main__':
    test()
    # parse_legal_cases()
    # parse_counterparties()
    # parse_auctions()
    # parse_trading_floors()
    # parse_counterparty('1656057203')
