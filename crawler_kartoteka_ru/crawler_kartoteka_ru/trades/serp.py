from random import randint

from bs4 import BeautifulSoup as BS
import re

from icecream import ic

from ..utils.working_with_url import UrlConfig
from ..utils.config import _lot_link_part, _link_to_lots_page
from ..utils.work_with_text_and_number import dedent_func
from ..utils.check_inn_email_etc import CheckIfCorrectContactInfo
import logging

logger = logging.getLogger(__name__)


class SerpPage:

    def __init__(self, response_):
        self.response = response_
        self.url = UrlConfig()
        self.check = CheckIfCorrectContactInfo()
        self.soup = BS(str(self.response.text), features='lxml')

    def get_pagination_next_page(self):
        """ find pagination  and return next page"""
        try:
            td_pagination = self.response.xpath('//td[contains(., "Страницы")]').get()
            if td_pagination:
                td = BS(str(td_pagination), features='lxml')
                current_page = td.strong.get_text()
                assume_next_page = int(current_page) + 1
                next_page = self.soup.find('a', string=str(assume_next_page))
                if next_page:
                    link = self.url.url_join(_lot_link_part['kartoteka_lot'], next_page.get('href'))
                    return link
        except Exception as e:
            logger.error(f'{self.response.url} :: ERROR PAGINATION {e}')


    def get_table_with_links(self):
        """ find table with links(tr) to trading_page and return list with <TR> info """
        try:
            return self.soup.find("table", class_="data").find_all('tr')
        except Exception as e:
            print(e)
            return None

    def get_links_to_trade_page(self) -> list:
        """ fetch and join links to trading page """
        final_list = list()
        if tr_list := self.get_table_with_links():
            for link in tr_list:
                part_of_link = ''.join(
                    re.findall(r'.+window\.location=.?(/trade/view/purchase/general.html\?id=\d+).?', str(link)))
                if len(part_of_link) > 0 and 'purchase/general.html?id' in part_of_link:
                    final_list.append(self.url.url_join(_lot_link_part['kartoteka_lot'], part_of_link))
            return final_list
        else:
            return final_list

    def get_trading_type_field(self):
        """ parse trading page and fetch field with trading type info """
        try:
            table = self.soup.find('th', string=re.compile(r'Информация о торгах', re.IGNORECASE)).findParent('table')
            if table:
                td = table.find('td', string=re.compile(r'Форма проведения торгов и подачи', re.IGNORECASE))
                if td:
                    trading_type = td.find_next('td').get_text()
                    return dedent_func(trading_type.lower())
        except Exception as e:
            logger.error(f'{self.response.url} :: ERROR had occured when trading type data tried to fetch \n{e}')

    def trading_type(self):
        """ trading type in english """
        try:
            offer = ['открытые торги посредством публичного предложения',
                     'закрытые торги посредством публичного предложения']
            auction = ['открытый аукцион с открытой формой представления предложений о цене',
                       'открытый аукцион с закрытой формой представления предложений о цене',
                       'закрытый аукцион с открытой формой представления предложений о цене',
                       'закрытый аукцион с закрытой формой представления предложений о цене']
            competition = ['открытый конкурс с открытой формой представления предложений о цене',
                           'открытый конкурс с закрытой формой представления предложений о цене',
                           'закрытый конкурс с открытой формой представления предложений о цене',
                           'закрытый конкурс с закрытой формой представления предложений о цене']
            if _type := self.get_trading_type_field():
                if _type in offer:
                    return 'offer'
                elif _type in auction:
                    return 'auction'
                elif _type in competition:
                    return 'competition'

        except Exception as e:
            print(e)
            logger.error(f'{self.response.url} :: ERROR function {self.trading_type.__name__}')

    def get_trading_id(self):
        """ return trading id """
        try:
            _id = ''.join(re.findall(r'\d+$', str(self.response.url).strip()))
            return _id
        except Exception as e:
            print(e)
            logger.error(f'{self.response.url} :: ERROR {self.get_trading_id.__name__}')

    def get_trading_number(self):
        """ return trading number according pattern """
        try:
            pattern = r'\d{4,}\-\D{4}'
            trading_number_h1 = self.soup.find('h1', string=re.compile(r'идентификационный', re.IGNORECASE))
            trading_number = ''.join(re.findall(pattern, trading_number_h1.get_text()))
            return trading_number
        except Exception as e:
            print(e)
            logger.error(f'{self.response.url} :: ERROR {self.get_trading_number.__name__}')

    def get_trading_form(self):
        """ return trading form - open or close """
        open_form = ['открытый аукцион с открытой формой представления предложений о цене',
                     'открытый конкурс с открытой формой представления предложений о цене',
                     'открытый аукцион с закрытой формой представления предложений о цене',
                     'открытый конкурс с закрытой формой представления предложений о цене',
                     'открытые торги посредством публичного предложения']
        close_form = ['закрытый аукцион с открытой формой представления предложений о цене',
                      'закрытый конкурс с открытой формой представления предложений о цене',
                      'закрытый аукцион с закрытой формой представления предложений о цене',
                      'закрытый конкурс с закрытой формой представления предложений о цене',
                      'закрытые торги посредством публичного предложения']
        if _type := self.get_trading_type_field():
            if _type in open_form:
                return 'open'
            elif _type in close_form:
                return 'closed'
            else:
                return None

    def get_org_table(self):
        """ return organizer table"""
        try:
            table_org = self.soup.find('th', string=re.compile(r'Организатор торгов', re.IGNORECASE)).findParent('table')
            return table_org
        except Exception as e:
            print(e)
            logger.error(f'{self.response.url} :: ERROR function {self.get_org_table.__name__}')

    def get_org_name(self):
        """ get organizer name """
        try:
            if table_org := self.get_org_table():
                org_name_title = table_org.find('td', string=re.compile(r'Наименование', re.IGNORECASE))
                org_name = org_name_title.find_next('td').get_text()
                return dedent_func(org_name.title())
        except Exception as e:
            print(e)
            logger.error(f'{self.response.url} :: ERROR function {self.get_org_name.__name__}')

    def get_org_email(self):
        """ return email of organizer """
        try:
            if table_org := self.get_org_table():
                org_email_title = table_org.find('td', string=re.compile(r'Адрес электронной почты', re.IGNORECASE))
                org_email = org_email_title.find_next('td').get_text()
                return dedent_func(self.check.check_email(org_email))
        except Exception as e:
            print(e)
            return ''

    def get_org_phone(self):
        """ return email of organizer """
        try:
            if table_org := self.get_org_table():
                org_phone_title = table_org.find('td', string=re.compile(r'Номер контактного телефона', re.IGNORECASE))
                org_phone = org_phone_title.find_next('td').get_text()
                return dedent_func(self.check.check_phone(org_phone))
        except Exception as e:
            print(e)
            return ''

    def full_org_contacts(self):
        """ retrun email and phone of organizer """
        return {'email': self.get_org_email(), 'phone': self.get_org_phone()}

    def get_msg_number(self):
        """ return msg_number """
        try:
            table_fed = self.soup.find('th', string=re.compile(r'ЕФРСБ', re.IGNORECASE)).findParent('table')
            msg_number_title = table_fed.find('td', string=re.compile(r'номер торгов на ЕФРСБ', re.IGNORECASE))
            msg_number_text = msg_number_title.find_next('td').get_text()
            msg_number = re.findall(r'\d{7,8}', msg_number_text)
            if len(msg_number) > 0:
                return ' '.join(msg_number)
        except Exception as e:
            print(e)
            logger.error(f'{self.response.url} :: ERROR function {self.get_msg_number.__name__}')

    def get_debt_table_info(self):
        """ return table with debtor case """
        try:
            table_debt_info = self.soup.find('th', string=re.compile(r'Сведения о банкротстве', re.IGNORECASE)).findParent('table')
            return table_debt_info
        except Exception as e:
            print(e)
            return None

    def get_case_number(self):
        """ return case number """
        if table := self.get_debt_table_info():
            case_title = table.find('td', string=re.compile(r'Номер дела о банкротстве', re.IGNORECASE))
            if case_title:
                case_td = case_title.find_next('td').get_text()
                return self.check.check_case_number(case_td)

    def get_debtor_inn(self):
        """ :return debtor inn """
        table_debtor = self.soup.find('th', string=re.compile(r'Сведения о должнике', re.IGNORECASE))
        if table_debtor:
            table_debtor = table_debtor.findParent('table')
            debtor_inn_title = table_debtor.find('td', string=re.compile(r'ИНН', re.IGNORECASE))
            if debtor_inn_title:
                debtor_inn = debtor_inn_title.find_next('td').get_text()
                return self.check.check_inn(dedent_func(debtor_inn))

    def get_arbitr_table(self):
        """ return table with arbitr info """
        try:
            table_arbitr_info = self.soup.find('th', string=re.compile(r'Арбитражный управляющий', re.IGNORECASE)).findParent('table')
            return table_arbitr_info
        except Exception as e:
            print(e)
            logger.error(f'{self.response.url} :: ERROR function {self.get_arbitr_table.__name__}')

    def get_arbitr_name(self):
        """ return arbitr name """
        if table := self.get_arbitr_table():
            arbitr_name = table.find('td', string=re.compile(r'Фамилия', re.IGNORECASE))
            if arbitr_name:
                name = arbitr_name.find_next('td').get_text()
                return dedent_func(name)

    def get_arbitr_org(self):
        """ return atbitr organization """
        if table := self.get_arbitr_table():
            arbitr_org = table.find('td', string=re.compile(r'Название саморегулируемой организации', re.IGNORECASE))
            if arbitr_org:
                org = arbitr_org.find_next('td').get_text()
                return dedent_func(org)

    def get_cache_number(self):
        """ return cache number for concatenation with document's page url if error then return random number """
        cache_number = self.soup.find(href=re.compile(r'/StylesCMS/kartotek.css\?cache=\d{11,16}'))
        if cache_number:
            cache_number = ''.join(re.findall(r'\d{11,16}', str(cache_number)))
            if len(cache_number) >= 11:
                return cache_number
        # RANDOM 13 NUMBERS
        return str(randint(162220000000, 162229999999))

    def get_lots_link(self, _id, page_number):
        """ return link to lot page """
        part_of_link = _link_to_lots_page['kartoteka_lot_page']
        return f'{part_of_link + str(_id)  + "&page=" + page_number + "&_=" + str(self.get_cache_number())}'

    def fetch_lots_tables_on_page(self):
        """ return amount of lots on current page //table[contains(@id,"lotNumber")]"""
        lot_tables = self.soup.find_all('table', id=re.compile('lotNumber', re.IGNORECASE))
        return lot_tables

    def get_current_page_lot(self):
        """ find pagination on lot page and current page """
        last_a = self.soup.find('span', class_='paginatorSelectedPage')
        return last_a.get_text()

    def find_next_page_lot(self):
        """ find next page on lot page if it is exist """
        current_page = self.get_current_page_lot()
        assume_next_page = int(current_page) + 1
        next_page = self.soup.find('a', string=str(assume_next_page))
        if next_page:
            return next_page.get_text()
