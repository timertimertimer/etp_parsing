import logging
import re
import pandas as pd
from bs4 import BeautifulSoup as BS

from general_utils.models import DownloadData
from .locator import Locator
from general_utils import UrlConfig, dedent_func, CheckIfCorrectContactInfo, contains, format_time
from .config import data_origin_url

logger = logging.getLogger(__name__)


class Combo:
    def __init__(self, response):
        self.response = response
        self.soup = BS(response.text, features='lxml')

    def download_general(self):
        files = list()
        if not (table := self.soup.find('div', id="proc").find('table')):
            return files
        for file in table.find_all('tr')[1:]:
            if not (link := file.find('td', class_='action')):
                continue
            link = UrlConfig.url_join(data_origin_url, link.find('a', text=contains('Скачать')).get('href'))
            name = file.find('td', class_='procedure-document-file').find('b').get_text(strip=True)
            files.append(DownloadData(url=link, file_name=name, referer=self.trading_link))
        return files

    def download_lot(self, lot_number: str):
        files = list()
        if not (table := self.soup.find('div', id=f"lot{lot_number}")):
            return files
        for file in table.find('table').find_all('tr')[1:]:
            if not (link := file.find('td', class_='action')):
                continue
            link = UrlConfig.url_join(data_origin_url, link.find('a', text=contains('Скачать')).get('href'))
            name = file.find('td', class_='lot-document-file').find('b').get_text(strip=True)
            files.append(DownloadData(url=link, file_name=name, referer=self.trading_link))
        return files

    def count_lots(self):
        return self.response.xpath(Locator.div_info_lot_offer).getall()[1:]

    def link_doc_page(self, url):
        try:
            link_to_document = BS(self.response.css(Locator.doc_link_loc).get(), features='lxml').a['href']
            if data_origin_url not in link_to_document:
                return UrlConfig.url_join(data_origin_url, link_to_document)
            else:
                return link_to_document
        except:
            logger.error(f'{url}:: INVALID DATA REFERENCE TO DOC PAGE')

    @property
    def trading_id(self):
        return self.response.url.split('/')[-1]

    @property
    def trading_link(self):
        return self.response.url

    @property
    def trading_number(self):
        number = self.response.xpath(Locator.offer_trading_number_loc2).get()
        number1 = self.response.xpath(Locator.offer_trading_number_loc).get()
        if number is None:
            number = number1
        if number:
            number = BS(str(number), features='lxml').get_text()
            number = ''.join(re.findall(r'\d+', number))
        return number

    def get_trading_type_text(self):
        check_type = self.soup.find('div', text=re.compile('Способ проведения процедуры'))
        if check_type:
            check_type = check_type.find_next('div')
            if check_type:
                return check_type.get_text().strip()

    @property
    def trading_type(self):
        string = self.get_trading_type_text()

        offer = ['Публичное предложение продавца']
        auction = [
            'Открытый аукцион с открытой формой подачи ценовых предложений',
            'Открытый аукцион с закрытой формой подачи ценовых предложений',
            'Закрытый аукцион с открытой формой подачи ценовых предложений',
            'Закрытый аукцион с закрытой формой подачи ценовых предложений',
            'Аукцион продавца',
            'Аукцион с закрытой формой подачи предложений о цене'
        ]
        competition = ['Открытый конкурс', 'Закрытый конкурс', 'Конкурс продавца']
        match1 = ''.join(filter(lambda x: re.findall(string, x, flags=re.IGNORECASE), auction))
        match2 = ''.join(filter(lambda x: re.findall(string, x, flags=re.IGNORECASE), offer))
        match3 = ''.join(filter(lambda x: re.findall(string, x, flags=re.IGNORECASE), competition))

        if match1:
            return 'auction'
        elif match2:
            return 'offer'
        elif match3:
            return 'competition'
        else:
            return None

    @property
    def trading_form(self):
        string = self.get_trading_type_text()
        open_form = ['Публичное предложение продавца',
                     'Открытый аукцион с открытой формой подачи ценовых предложений',
                     'Открытый аукцион с закрытой формой подачи ценовых предложений',
                     'Открытый конкурс',
                     'Аукцион продавца',
                     'Аукцион с закрытой формой подачи предложений о цене', 'open']
        close_form = ['Закрытый аукцион с открытой формой подачи ценовых предложений',
                      'Закрытый аукцион с закрытой формой подачи ценовых предложений',
                      'Закрытый конкурс']
        match1 = ''.join(filter(lambda x: re.findall(string, x, flags=re.IGNORECASE), open_form))
        match2 = ''.join(filter(lambda x: re.findall(string, x, flags=re.IGNORECASE), close_form))

        if match1:
            return 'open'
        elif match2:
            return 'closed'
        else:
            return 'closed'

    @property
    def trading_org(self):
        try:
            first_loc = dedent_func(self.response.xpath(Locator.offer_org_name_loc1).get())
            second_loc = dedent_func(
                BS(str(self.response.xpath(Locator.offer_org_name_loc2).get()), features='lxml').get_text())
            if first_loc:
                return first_loc
            elif second_loc:
                return second_loc
            else:
                return None
        except:
            logger.warning(f'{self.response.url} :: INVALID DATA TRADING ORG - OFFER ')

    @property
    def trading_org_inn(self):
        try:
            trade_inn = BS(self.response.xpath(Locator.offer_org_inn_loc).get(), features='lxml').get_text()
            pattern = re.compile(r'\d{10,12}')
            if pattern:
                return ''.join(pattern.findall(trade_inn))
        except:
            return None

    @property
    def trading_org_contacts(self):
        phone = ''
        try:
            org_phone = BS(self.response.xpath(Locator.offer_org_phone_loc).get(), features='lxml').get_text().strip()
            org_phone = CheckIfCorrectContactInfo.check_phone(org_phone)
            phone = org_phone
        except:
            pass
        email = ''
        try:
            org_email = BS(self.response.xpath(Locator.offer_org_email_loc).get(), features='lxml').get_text().strip()
            org_email = CheckIfCorrectContactInfo.check_email(org_email)
            email = org_email
        except:
            pass

        return {'email': email, 'phone': phone}

    @property
    def msg_number(self):
        td_msg = BS(self.response.text, features='lxml').find('div',
                                                              string=re.compile('сообщения .* ЕФРСБ', re.IGNORECASE))
        if td_msg:
            td_msg = dedent_func(td_msg.find_next('div').get_text().strip())
        try:
            if td_msg:
                match = re.findall(r'\d{7,9}', td_msg)
                return CheckIfCorrectContactInfo.check_msg_number(' '.join(match))
            else:
                return
        except:
            logger.error(f'{self.response.url} :: INVALID DATA MSG_NUMBER OFFER', exc_info=True)

    @property
    def case_number(self):
        case_ = self.response.xpath(Locator.offer_case_number).get()
        try:
            case_ = ''.join(BS(str(case_), features='lxml').get_text()).replace('№', '').replace('\\', '/').replace(' ',
                                                                                                                    '').strip()
            if len(case_) < 42:
                return CheckIfCorrectContactInfo.check_case_number(case_)
        except:
            logger.warning(f'{self.response.url} :: INVALID CASE_NUMBER  OFFER')
            return None

    @property
    def debtor_inn(self):
        try:
            debitor_inn = BS(self.response.xpath(Locator.deb_inn_loc).get(), features='lxml').get_text()
            pattern = re.compile(r'\d{10,12}')
            if pattern:
                return ''.join(pattern.findall(debitor_inn))
        except:
            return

    @property
    def address(self):
        address = self.response.xpath(Locator.address_loc).get()
        if not address:
            address = self.response.xpath(Locator.sud_loc).get()
        try:
            address = BS(address, features='lxml').get_text(strip=True)
            return ' '.join(address.split())
        except:
            return

    @property
    def arbit_manager(self):
        try:
            last_name = dedent_func(
                BS(str(self.response.xpath(Locator.arbitr_last_name).get()), features='lxml').get_text())
            name = dedent_func(BS(str(self.response.xpath(Locator.arbitr_name).get()), features='lxml').get_text())
            middle_name = dedent_func(
                BS(str(self.response.xpath(Locator.arbitr_mid_name).get()), features='lxml').get_text())
            return ' '.join(list(filter(lambda x: x != 'None', [last_name, name, middle_name])))
        except:
            pass

    @property
    def arbit_manager_inn(self):
        try:
            arb_inn = BS(self.response.xpath(Locator.arbitr_inn).get(), features='lxml').get_text()
            pattern = re.compile(r'\d{10,12}')
            if pattern:
                return ''.join(pattern.findall(dedent_func(arb_inn)))
        except:
            return None

    @property
    def arbit_manager_org(self):
        try:
            td_company = BS(str(self.response.xpath(Locator.arbitr_org).get()), features='lxml').get_text()
            if td_company != 'None':
                if '(' in td_company:
                    td_company = ''.join(
                        [x if len(td_company) > 0 else None for x in re.split(r'\(', td_company, maxsplit=1)[0]])
                return ''.join(dedent_func(td_company))

        except:
            logger.warning(f'{self.response.url} :: INVALID DATA TRADING ORG - OFFER ')

    def create_soup(self, lot):
        return BS(lot, features='lxml')

    def get_status(self, lot):
        status = self.create_soup(lot).find('span', class_='kim-state-label').get_text(strip=True)
        active = ('Этап приема заявок', 'Проводятся торги', 'Прием заявок')
        pending = ('Ожидание этапа приема заявок', 'Ожидается начало нового этапа', 'Ожидается начало приема заявок')
        if status in active:
            return 'active'
        elif status in pending:
            return 'pending'
        else:
            return 'ended'

    def get_lot_id(self, lot):
        return self.get_lot_link(lot).split('/')[-1]

    def get_lot_link(self, lot):
        return UrlConfig.url_join(data_origin_url, self.create_soup(lot).find('a', text='Просмотр').get('href').strip())

    def get_lot_number(self, lot):
        short_name = self.get_short_name(lot)
        pattern = re.compile(r'Лот.?\W\s?\d{1,}\:?|Лот.?\W\d{1,}\.?', flags=re.IGNORECASE)
        match = pattern.findall(str(short_name))
        lot_number = ''.join(re.findall(r'\d+', min(match)))
        return lot_number

    def get_short_name(self, lot):
        return dedent_func(
            self.create_soup(lot).find('div', class_='panel-heading clearfix')
            .find(text=True, recursive=False).get_text(strip=True).removesuffix('-').strip()
        )

    def get_lot_info(self, lot):
        return dedent_func(
            self.create_soup(lot)
            .find('div', text=re.compile('Предмет договора', re.IGNORECASE))
            .find_next('div').get_text(strip=True)
        )

    def get_property_information(self, lot):
        return dedent_func(
            self.create_soup(lot)
            .find('div', text=re.compile('Порядок ознакомления с имуществом', re.IGNORECASE))
            .find_next('div').get_text(strip=True)
        )

    def get_categories(self, lot):
        return ' '.join(
            self.create_soup(lot)
            .find('div', text=re.compile('Классификатор имущества для ЕФРСБ', re.IGNORECASE))
            .find_next('div').get_text(strip=True).split()
        )

    def get_start_date_requests(self, lot):
        try:
            return format_time(
                self.create_soup(lot)
                .find('div', text=re.compile('Дата и время начала приема заявок', re.IGNORECASE))
                .find_next('div').get_text(strip=True)
            )
        except Exception as e:
            print(e)
            return None

    def get_end_date_requests(self, lot):
        try:
            return format_time(
                self.create_soup(lot)
                .find('div', text=re.compile('Дата и время окончания приема заявок', re.IGNORECASE))
                .find_next('div').get_text(strip=True)
            )
        except Exception as e:
            print(e)
            return None

    def get_start_date_trading(self, lot):
        try:
            return format_time(
                self.create_soup(lot)
                .find('div', text=re.compile('Дата и время начала аукциона', re.IGNORECASE))
                .find_next('div').get_text(strip=True)
            )
        except Exception as e:
            print(e)
            return None

    def get_end_date_trading(self, lot):
        try:
            return format_time(
                self.create_soup(lot)
                .find('div', text=re.compile('Дата и время подведения итогов', re.IGNORECASE))
                .find_next('div').get_text(strip=True)
            )
        except Exception as e:
            print(e)
            return None

    def get_start_price(self, lot):
        match = re.search(
            r'\d+\.\d{1,2}',
            self.create_soup(lot)
            .find('div', text=re.compile('Начальная цена предмета договора', re.IGNORECASE))
            .find_next('div').get_text(strip=True)
            .replace('\xa0', '').replace(',', '.')
        )
        try:
            if match:
                return float(match.group())
        except (ValueError, TypeError) as e:
            print(e)
            return None

    def get_step_price(self, lot):
        _div_step = (
            self.create_soup(lot)
            .find('div', text=re.compile('Шаг аукциона', re.IGNORECASE))
        )
        if _div_step:
            _div_step = _div_step.find_next('div').get_text(strip=True)
            step = ''.join(re.findall(r'^\d*\,?\d+', _div_step.replace('\xa0', ''))).replace(',', '.')
            start_price = self.get_start_price(lot)
            try:
                step = float(step)
                return round(start_price * step / 100, 2)
            except (ValueError, TypeError):
                return None

    def get_periods(self, lot):
        tables = (
            self.create_soup(lot)
            .find('div', text=re.compile('Этап понижения', re.IGNORECASE))
            .find_next('div')
        )
        periods = []
        check_value = 10000000000000000000000
        for table in tables.find_all('table'):
            _table = pd.read_html(str(table))
            df = _table[0][1]
            start = df.iloc[1]
            end = df.iloc[2]
            price_ = df.iloc[3]
            price_ = ''.join(filter(lambda x: x.isdigit() or x == ',', price_)).replace(',', '.')
            try:
                if isinstance(price_, str):
                    price = ''.join(re.sub(r"\s", "", price_)).replace(',', '.')
                    price = round(float(price), 2)
                else:
                    price = round(float(price_), 2)
                if check_value < price:
                    logger.critical(
                        f'{self.response.url} :: INVALID PRICE ON PERIOD - CURRENT PRICE HIGHER THAN PREVIUOS'
                    )
                else:
                    check_value = price
            except:
                logger.error(f'{self.response.url} Period Price - {price_} typeof - {type(price_)}')
                return None
            try:
                period = {
                    'start_date_requests': format_time(start),
                    'end_date_requests': format_time(end),
                    'end_date_trading': format_time(end),
                    'current_price': price
                }
                periods.append(period)
            except:
                continue
        return periods
