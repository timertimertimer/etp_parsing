import re

from bs4 import BeautifulSoup

from general_utils import dedent_func, CheckIfCorrectContactInfo, format_time
from ..locators.locator_auction import LocatorAuction
import logging

logger = logging.getLogger(__name__)


class Auction:

    def __init__(self, response_):
        self.response = response_
        self.soup = BeautifulSoup(self.response.text, 'lxml')
        self.loc_auc = LocatorAuction

    def get_trading_type(self):
        """ return trading type """
        try:
            offer = ('публичное предложение', 'закрытое публичное предложение')
            auction = ('аукцион с открытой формой представления цены', 'аукцион с закрытой формой представления цены',
                       'закрытый аукцион с открытой формой представления цены',
                       'закрытый аукцион с закрытой формой представления цены')
            competition = ('конкурс с открытой формой представления цены',
                           'конкурс с закрытой формой представления цены',
                           'закрытый конкурс с открытой формой представления цены',
                           'закрытый конкурс с закрытой формой представления цены')
            _type_text = self.response.xpath(self.loc_auc.trading_type).get()
            _type_text1 = BeautifulSoup(str(_type_text), features='lxml').get_text().lower()
            text = dedent_func(_type_text1)
            if text in offer:
                return 'offer'
            elif text in auction:
                return 'auction'
            elif text in competition:
                return 'competition'
        except Exception as e:
            logger.error(f'{self.response.url} :: INVALID DATA TRADING TYPE {e}')

    def get_trading_form(self):
        """ :return trading form """
        _open = ('публичное предложение', 'аукцион с открытой формой представления цены',
                 'аукцион с закрытой формой представления цены', 'конкурс с открытой формой представления цены',
                 'конкурс с закрытой формой представления цены')
        closed = ('закрытое публичное предложение', 'закрытый аукцион с открытой формой представления цены',
                  'закрытый аукцион с закрытой формой представления цены',
                  'закрытый конкурс с открытой формой представления цены',
                  'закрытый конкурс с закрытой формой представления цены')
        _type_text = self.response.xpath(self.loc_auc.trading_type).get()
        _type_text1 = BeautifulSoup(str(_type_text), features='lxml').get_text().lower()
        text = dedent_func(_type_text1)
        if text in _open:
            return 'open'
        elif text in closed:
            return 'closed'

    def get_trading_id(self):
        """ :return trading id """
        try:
            _id = re.findall(r'\d+$', str(self.response.url))
            return ''.join(_id)
        except Exception as ex:
            logger.error(f'{self.response.url} :: INVALID DATA Trading ID {ex}')

    def get_block_org(self):
        """ :return trading organizer block(section with info) """
        try:
            org_block = self.response.xpath(self.loc_auc.trading_org).get()
            if not org_block:
                org_block = self.response.xpath(self.loc_auc.trading_org2).get()
            org_block = BeautifulSoup(str(org_block), features='lxml')
            return org_block
        except Exception as ex:
            logger.error(f'{self.response.url} :: INVALID DATA TRADING ORG {ex}')

    def get_org_name(self):
        """ :return trading organizer company or person name """
        try:
            # bs4 object
            block = self.get_block_org()
            name = (
                block.find('td', string=re.compile('аименование', re.IGNORECASE)) or
                block.find('td', string=re.compile('ФИО', re.IGNORECASE))
            )
            if name:
                return dedent_func(name.findNext('td').get_text(strip=True))
        except Exception as ex:
            logger.error(f'{self.response.url} :: INVALID DATA get_org_name {ex}')

    def get_inn_org(self):
        """ return organizer INN """
        try:
            # bs4 object
            block = self.get_block_org()
            _inn = block.find('td', string=re.compile('ИНН', re.IGNORECASE))
            if _inn:
                _inn = dedent_func(_inn.findNext('td').get_text().strip())
                return CheckIfCorrectContactInfo.check_inn(_inn)
        except Exception as ex:
            logger.error(f'{self.response.url} :: INVALID DATA ORG INN {ex}')

    def get_email(self):
        """ :return org email """
        try:
            block = self.get_block_org()
            email = block.find('td', string=re.compile('E-mail', re.IGNORECASE)).findNext('td')
            if email:
                email = dedent_func(email.get_text().strip())
                return CheckIfCorrectContactInfo.check_email(email)
            else:
                return ''
        except Exception as ex:
            logger.error(f'{self.response.url} :: INVALID DATA EMAIL ORG {ex}')
            return ''

    def get_phone(self):
        """ :return phone org """
        try:
            block = self.get_block_org()
            phone = block.find('td', string=re.compile('Телефон', re.IGNORECASE)).findNext('td')
            if phone:
                phone = dedent_func(phone.get_text().strip())
                return CheckIfCorrectContactInfo.check_phone(phone)
            else:
                return ''
        except Exception as ex:
            logger.error(f'{self.response.url} :: INVALID DATA PHONE ORG {ex}')
            return ''

    def get_org_contacts(self):
        email = self.get_email()
        phone = self.get_phone()
        return {'email': email, 'phone': phone}

    def get_block_trade_info(self):
        """ return block(bs4) that contains msg number """
        try:
            info_block = self.response.xpath(self.loc_auc.trade_info).get()
            info_block = BeautifulSoup(str(info_block), features='lxml')
            return info_block
        except Exception as ex:
            logger.error(f'{self.response.url} :: INVALID DATA get_block_trade_info {ex}')

    def msg_number(self):
        """ retur mesage number """
        block = self.get_block_trade_info()
        block = BeautifulSoup(str(block), features='lxml')
        msg = block.find('td', string=re.compile('о проведении торгов на fedresurs.ru', re.IGNORECASE)).findNext('td')
        if msg:
            msg = re.findall(r'\d{6,8}', msg.get_text())
            if len(msg) > 0:
                return ' '.join(msg)

    def get_block_debtor_info(self):
        """ :return block with debtor info """
        try:
            debtor_block = self.response.xpath(self.loc_auc.debtor_info).get()
            debtor_block = BeautifulSoup(str(debtor_block), features='lxml')
            return debtor_block
        except Exception as ex:
            logger.error(f'{self.response.url} :: INVALID DATA DEBTOR INFO {ex}')

    def case_number(self):
        """ :return case number """
        block = self.get_block_debtor_info()
        if block:
            case = block.find('td', string=re.compile('Номер дела о банкротстве', re.IGNORECASE)).findNext('td')
            if case:
                case = dedent_func(case.get_text().strip())
                return CheckIfCorrectContactInfo.check_case_number(case)

    def get_inn_debtor(self):
        """ return debtor INN """
        try:
            # bs4 object
            block = self.get_block_debtor_info()
            _inn = block.find('td', string=re.compile('ИНН', re.IGNORECASE)).findNext('td')
            if _inn:
                _inn = dedent_func(_inn.get_text().strip())
                if re.match(r'\d{9,13}', _inn):
                    inn = _inn
                else:
                    inn = self.response.xpath(self.loc_auc.extra_loc_debtor).get()
                return CheckIfCorrectContactInfo.check_inn(inn)
        except Exception as ex:
            logger.error(f'{self.response.url} :: INVALID DATA DEBTOR INN {ex}')

    @property
    def address(self):
        try:
            if table := self.get_block_debtor_info():
                address = table.find('td', string='Адрес')
                if address:
                    address = address.findNextSibling('td').get_text(strip=True)
                sud = table.find('td', string='Наименование суда')
                if sud:
                    sud = sud.findNextSibling('td').get_text(strip=True)
                region = table.find('td', string='Регион')
                if region:
                    region = region.findNextSibling('td').get_text(strip=True)
                if not any([address, sud]):
                    return region
                if not address:
                    address = sud
                return address
        except Exception as e:
            logger.error(f'{self.response.url} :: ERROR function {self.address.__name__}')

    def get_arbitr_block(self):
        """ :return block with arbitr info """
        try:
            block_arbitr = self.response.xpath(self.loc_auc.arbitr_info).get()
            arb = BeautifulSoup(str(block_arbitr), features='lxml')
            return arb
        except Exception as ex:
            logger.error(f'{self.response.url} :: {ex}')

    def get_arbitr_full_name(self):
        """ :return full arbitr name """
        try:
            block = self.get_arbitr_block()
            if block:
                last_name = block.find('td', string=re.compile('Фамилия', re.IGNORECASE))
                if last_name:
                    last_name = dedent_func(last_name.findNext('td').get_text().strip())
                else:
                    last_name = ''
                first_name = block.find('td', string=re.compile('Имя', re.IGNORECASE))
                if first_name:
                    first_name = dedent_func(first_name.findNext('td').get_text().strip())
                else:
                    first_name = ''
                middle_name = block.find('td', string=re.compile('Отчество', re.IGNORECASE))
                if middle_name:
                    middle_name = dedent_func(middle_name.findNext('td').get_text().strip())
                else:
                    middle_name = ''
                return ' '.join([last_name, first_name, middle_name])
        except Exception as e:
            logger.error(f'{self.response.url} :: INVALID DATA ARBITR NAME {e}')
            return None

    def get_arbitr_inn(self):
        """ return arbitr INN """
        try:
            # bs4 object
            block = self.get_arbitr_block()
            _inn = block.find('td', string=re.compile('ИНН', re.IGNORECASE)).findNext('td')
            if _inn:
                _inn = dedent_func(_inn.get_text().strip())
                return CheckIfCorrectContactInfo.check_inn(_inn)
        except Exception as ex:
            logger.error(f'{self.response.url} :: INVALID DATA ARBITR INN {ex}')

    def get_arbitr_company(self):
        """ return arbitr company """
        try:
            # bs4 object
            block = self.get_arbitr_block()
            company = block.find('td', string=re.compile('аименование СРО', re.IGNORECASE)).findNext('td')
            if company:
                company = dedent_func(company.get_text().strip())
                if '(' in company:
                    company = re.split(r'\(', company, maxsplit=1)[0]
                if ',' in company:
                    company = re.split(r',', company, maxsplit=1)[0]
                return company
        except Exception as ex:
            logger.error(f'{self.response.url} :: INVALID DATA ARBITR company {ex}')

    def date_block_auction(self):
        """ :return block with auction dates of trading """
        try:
            block = self.response.xpath(self.loc_auc.dates_trading).get()
            date_ = BeautifulSoup(str(block), features='lxml')
            return date_
        except Exception as ex:
            logger.error(f'{self.response.url} :: {ex}')

    def start_date_request_auc(self):
        """ :return start date request auction """
        try:
            # bs4 object
            block = self.date_block_auction()
            if block:
                start = block.find('td', string=re.compile('ата начала представления заявок на участи',
                                                           re.IGNORECASE)).findNext('td')
                if start:
                    start = format_time(dedent_func(start.get_text().strip()))
                    return start
        except Exception as ex:
            logger.error(f'{self.response.url} :: ERROR start date request auction {ex}')
            return None

    def end_date_request_auc(self):
        """ :return end date request auction """
        try:
            # bs4 object
            block = self.date_block_auction()
            if block:
                end = block.find('td', string=re.compile('ата окончания представления заявок на', re.IGNORECASE))
                if end:
                    end = format_time(dedent_func(end.findNext('td').get_text().strip()))
                    return end
        except Exception as ex:
            logger.error(f'{self.response.url} :: ERROR start date request auction {ex}')
            return None

    def start_date_trading_auc(self):
        """ :return start date trading auction """
        try:
            # bs4 object
            block = self.date_block_auction()
            if block:
                start = block.find('td', string=re.compile('ата проведени', re.IGNORECASE))
                if start:
                    start = format_time(dedent_func(start.findNext('td').get_text().strip()))
                    return start
        except Exception as ex:
            logger.error(f'{self.response.url} :: ERROR start date request auction {ex}')
            return None

    # LOTS (FOR ALL TYPES OF TRADE)
    def count_lots(self) -> list:
        """ :return list with lots table """
        lot = self.soup.find_all('table', id=re.compile('table_lot', re.IGNORECASE))
        if len(lot) > 0:
            return lot


    def table_trading_page_trade_info(self):
        """ return table with title "Information about trades" """
        table = self.soup.find('th', string=re.compile('Информация о ходе торгов', re.IGNORECASE))
        if table:
            table = table.find_parent('table')
            return table
        else:
            logger.error(
                f'{self.response.url} :: ERROR function class Auction {self.table_trading_page_trade_info.__name__}')

    def start_date_requests(self):
        """ return start date requests auction """
        if table := self.table_trading_page_trade_info():
            text = r'Дата начала представления заявок на участие'
            start = table.find('td', string=re.compile(text, re.IGNORECASE))
            if start:
                start = start.findNextSibling('td').get_text().replace('-', ' ')
                start = re.sub(r'\s+', ' ', start)
                try:
                    return format_time(start)
                except Exception as e:
                    print(e)
                    logger.error(f'{self.response.url} :: ERROR function {self.start_date_requests.__name__}')

    def end_date_requests(self):
        """ return end date requests auction """
        if table := self.table_trading_page_trade_info():
            text = r'Дата окончания представления заявок на участие'
            end = table.find('td', string=re.compile(text, re.IGNORECASE))
            if end:
                end = end.findNextSibling('td').get_text().replace('-', ' ')
                end = re.sub(r'\s+', ' ', end)
                try:
                    return format_time(end)
                except Exception as e:
                    print(e)
                    logger.error(f'{self.response.url} :: ERROR function {self.end_date_requests.__name__}')

    def start_date_trading(self):
        """ return start date trading auction """
        if table := self.table_trading_page_trade_info():
            text = r'Дата проведения'
            start_trading = table.find_all('td', string=re.compile(text, re.IGNORECASE))
            if len(start_trading) > 1:
                start_t = None
                for s in start_trading:
                    if len(s.get_text().strip()) < 18:
                        start_t = s
                        if start_t:
                            start_trading = start_t.findNextSibling('td').get_text().replace('-', ' ')
                            start_trading = re.sub(r'\s+', ' ', start_trading)
                            try:
                                return format_time(start_trading)
                            except Exception as e:
                                print(e)
                                logger.error(f'{self.response.url} :: ERROR function {self.start_date_requests.__name__}')
            elif len(start_trading) == 1:
                try:
                    start_trading = start_trading[0]
                    start_trading = start_trading.findNextSibling('td').get_text().replace('-', ' ')
                    start_trading = re.sub(r'\s+', ' ', start_trading)
                    try:
                        return format_time(start_trading)
                    except Exception as e:
                        print(e)
                        logger.error(f'{self.response.url} :: ERROR function {self.start_date_requests.__name__}')
                except Exception as e:
                    print(e)


