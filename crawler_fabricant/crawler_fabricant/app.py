import logging
import pathlib
import re

from bs4 import BeautifulSoup as BS

from crawler_fabricant.crawler_fabricant.locator import Locator
from general_utils import DownloadFiles, FilesDir, format_time_auction, UrlConfig, dedent_func, \
    CheckIfCorrectContactInfo
from general_utils.config import lst_exeption, lst_exet, lst_exet_archive

logger = logging.getLogger(__name__)


class Combo:
    def __init__(self, response):
        self.response = response
        self.soup = BS(response.text, features='lxml')

    def download_general(self):
        ...

    def download_lot(self):
        ...

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
        soup = BS(str(self.soup.text), features='lxml')
        check_type = soup.find('div', string=re.compile('Способ проведения процедуры'))
        if check_type:
            check_type = check_type.find_next('div')
            if check_type:
                string = check_type.get_text().strip()

    @property
    def trading_type(self):
        string = self.get_trading_type_text()

        offer = ['Публичное предложение продавца', 'offer']
        auction = ['Открытый аукцион с открытой формой подачи ценовых предложений',
                   'Открытый аукцион с закрытой формой подачи ценовых предложений',
                   'Закрытый аукцион с открытой формой подачи ценовых предложений',
                   'Закрытый аукцион с закрытой формой подачи ценовых предложений',
                   'Аукцион продавца',
                   'Аукцион с закрытой формой подачи предложений о цене', 'auction']
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
        try:
            address = BS(self.response.xpath(Locator.address_loc).get(), features='lxml').get_text(strip=True)
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

    def get_status(self, lot):
        status = lot.xpath(Locator.status_loc).get().strip()
        active = ('Этап приема заявок', 'Проводятся торги')
        pending = ('Ожидание этапа приема заявок',)
        try:
            if status in active:
                return 'active'
            elif status in pending:
                return 'pending'
            else:
                return 'ended'
        except:
            return None

    def get_lot_id(self, lot):
        return self.get_lot_link(lot).split('/')[-1]

    def get_lot_link(self, lot):
        return lot.xpath(Locator.lot_link_loc).get().strip()

    def get_lot_number(self, lot):
        short_name = self.get_short_name(lot)
        pattern = re.compile(r'Лот.?№?\s?\d+', re.IGNORECASE)
        lots_num = list(filter(lambda x: len(x) > 0, list(map(lambda y: y, pattern.findall(short_name)))))
        return lots_num

    def get_short_name(self, lot):
        return lot.xpath(Locator.lot_number_loc).get().strip()

    def get_property_information(self, lot):
        return dedent_func(lot.xpath(Locator.property_info_loc).get())

    def get_start_date_requests(self, lot):
        try:
            return format_time_auction(lot.xpath(Locator.start_request_auction).get())
        except Exception as e:
            print(e)
            return None

    def get_end_date_requests(self, lot):
        try:
            return format_time_auction(lot.xpath(Locator.end_request_auction).get())
        except Exception as e:
            print(e)
            return None

    def get_start_date_trading(self, lot):
        try:
            return format_time_auction(lot.xpath(Locator.start_trading_auction).get())
        except Exception as e:
            print(e)
            return None

    def get_end_date_trading(self, lot):
        try:
            return format_time_auction(lot.xpath(Locator.end_date_trading_auc).get())
        except Exception as e:
            print(e)
            return None

    def get_start_price(self, lot):
        match = re.search(
            r'\d+\.\d{1,2}',
            lot.xpath(Locator.start_price_auc).get().replace('\xa0', '').replace(',', '.')
        )
        try:
            if match:
                return float(match.group())
        except (ValueError, TypeError) as e:
            print(e)
            return None

    def get_step_price(self, lot):
        _div_step = lot.xpath(Locator.step_price_auc).get()
        if _div_step:
            step = ''.join(re.findall(r'^\d*\,?\d+', _div_step.replace('\xa0', ''))).replace(',', '.')
            start_price = self.get_start_price(lot)
            try:
                step = float(step)
                return round(start_price * step / 100, 2)
            except (ValueError, TypeError):
                return None

    @property
    def periods(self):
        ...
