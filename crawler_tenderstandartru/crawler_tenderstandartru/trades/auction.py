from general_utils import get_region
from .libraries import *

logger = logging.getLogger(__name__)


class AuctionParse:
    addresses = dict()

    def __init__(self, response_):
        self.response = response_
        self.soup = soup(self.response)
        self.check = CheckIfCorrectContactInfo()

    def get_organizer_name(self):
        label = self.soup.find('label', string=re.compile(r'Организатор торгов', re.IGNORECASE))
        if label:
            div_inn = label.findNext('div', class_='auction_table').find('div',
                                                                         string=re.compile(r'Сокращенное наименование:', re.IGNORECASE))
            if div_inn:
                div_inn = div_inn.findNextSibling('div')
                return div_inn.get_text()

    def get_organizer_inn(self):
        """ return organizer INN """
        label = self.soup.find('label', string=re.compile(r'Организатор торгов', re.IGNORECASE))
        if label:
            div_inn = label.findNext('div', class_='auction_table').find('div',
                                                                         string=re.compile(r'ИНН:', re.IGNORECASE))
            if div_inn:
                div_inn = div_inn.findNextSibling('div')
                inn = div_inn.get_text()
                return self.check.check_inn(inn)

    def get_org_email(self):
        """ return organizer email """
        label = self.soup.find('label', string=re.compile(r'Контактное лицо организатора торгов', re.IGNORECASE))
        if label:
            div_email = label.findNext('div', class_='auction_table').find('div',
                                                                           string=re.compile(r'E-mail:', re.IGNORECASE))
            if div_email:
                div_email = div_email.findNextSibling('div')
                email = div_email.get_text()
                return self.check.check_email(email)

    def get_org_phone(self):
        """ return organizer phone """
        label = self.soup.find('label', string=re.compile(r'Контактное лицо организатора торгов', re.IGNORECASE))
        if label:
            div_phone = label.findNext('div', class_='auction_table') \
                .find('div', string=re.compile(r'Телефон:', re.IGNORECASE))
            if div_phone:
                div_phone = div_phone.findNextSibling('div')
                phone = div_phone.get_text()
                return self.check.check_phone(phone)

    def get_full_org_contacts(self):
        """ return full org contacts - email & phone """
        return {'email': self.get_org_email(), 'phone': self.get_org_phone()}

    def get_case_number(self):
        """ return case number  """
        label = self.soup.find('label', string=re.compile(r'Сведения о банкротстве', re.IGNORECASE))
        if label:
            div_bankrot_info = label.findNext('div', class_='auction_table') \
                .find('div', string=re.compile(r'Номер дела о банкротстве:', re.IGNORECASE))
            if div_bankrot_info:
                div_bankrot_info = div_bankrot_info.findNextSibling('div')
                case_number = div_bankrot_info.get_text()
                return self.check.check_case_number(case_number)

    def get_arbitr_name(self):
        """ return arbitr name """
        label = self.soup.find('label', string=re.compile(r'Арбитражный управляющий', re.IGNORECASE))
        if label:
            div_arbitr_name = label.findNext('div', class_='auction_table'). \
                find('div', string=re.compile(r'ФИО:', re.IGNORECASE))
            if div_arbitr_name:
                div_arbitr_name = div_arbitr_name.findNextSibling('div')
                arbitr_name = div_arbitr_name.get_text()
                return dedent_func(arbitr_name)

    def get_arbitr_company(self):
        """ return arbitr company """
        label = self.soup.find('label', string=re.compile(r'Арбитражный управляющий', re.IGNORECASE))
        if label:
            div_arbitr_company = label.findNext('div', class_='auction_table'). \
                find('div', string=re.compile(r'Наименование организации арбитражных управляющих:', re.IGNORECASE))
            if div_arbitr_company:
                div_arbitr_company = div_arbitr_company.findNextSibling('div')
                arbitr_company = div_arbitr_company.get_text()
                return dedent_func(arbitr_company)

    def get_debtor_inn(self):
        """ return debtor INN """
        label = self.soup.find('label', string=re.compile(r'Сведения о должнике', re.IGNORECASE))
        if label:
            div_inn = label.findNext('div', class_='auction_table'). \
                find('div', string=re.compile(r'ИНН:', re.IGNORECASE))
            if div_inn:
                div_inn = div_inn.findNextSibling('div')
                inn = div_inn.get_text()
                return self.check.check_inn(inn)

    @property
    def address(self):
        label = self.soup.find('label', string=re.compile(r'Сведения о банкротстве', re.IGNORECASE))
        if label:
            div_bankrot_info = label.findNext('div', class_='auction_table') \
                .find('div', string=re.compile(r'Наименование арбитражного суда:', re.IGNORECASE))
            if div_bankrot_info:
                div_bankrot_info = div_bankrot_info.findNextSibling('div')
                return div_bankrot_info.get_text().strip()

    def get_property_information(self):
        """ :return property_information """
        _div = self.soup.find('div',
                              string=re.compile(r'Порядок ознакомления с имуществом:', re.IGNORECASE))
        if _div:
            prop_info = _div.findNext('div').get_text().strip().lower()
            return dedent_func(prop_info)

        logger.error(f'{self.response.url} :: ERROR function {self.get_property_information.__name__}')

    # LOT PAGE
    def get_trading_form(self, trading_form_text):
        """ :return convert trading form  """
        _open = 'открытая'
        _closed = 'закрытая'
        if trading_form_text in _open:
            return 'open'
        elif trading_form_text in _closed:
            return 'closed'
        else:
            logger.error(f'{self.response.url} :: ERROR function {self.get_trading_form.__name__} 2')

    def trading_form_div(self):
        """ :return trading form """
        _div = self.soup.find('div', string=re.compile(r'Форма торга по составу участника:', re.IGNORECASE))
        if _div:
            form_ = _div.findNext('div').get_text().strip().lower()
            return self.get_trading_form(form_)
        logger.error(f'{self.response.url} :: ERROR function {self.trading_form_div.__name__} 1')

    @delete_extra_symbols
    @cut_lot_number
    def get_short_name(self):
        """ return short name """
        previous_div = self.soup.find('div', string=re.compile(r'Номер №\s?\d+', re.IGNORECASE))
        if previous_div:
            _div = previous_div.findNext('div', string=re.compile(r'Наименование:', re.IGNORECASE))
            if _div:
                short_name = _div.findNext('div').get_text().strip().lower()
                return dedent_func(short_name)
        logger.error(f'{self.response.url} :: ERROR function {self.get_short_name.__name__}')

    def get_lot_info(self):
        """ :return lot_info """
        _div = self.soup.find('div',
                              string=re.compile(
                                  r'Сведения об имуществе, его составе, характеристиках, описание, порядок ознакомления:',
                                  re.IGNORECASE))
        if _div:
            lot_info = _div.findNext('div').get_text().strip().lower()
            return dedent_func(lot_info)
        logger.error(f'{self.response.url} :: ERROR function {self.get_lot_info.__name__}')

    def start_date_requests_auction(self):
        """ :return trading form """
        _div = self.soup.find('div', string=re.compile(r'Дата начала представления заявок на участие:', re.IGNORECASE))
        if _div:
            data_requests = _div.findNext('div').get_text().strip().lower()
            return format_time_auction(data_requests)
        logger.error(f'{self.response.url} :: ERROR function {self.start_date_requests_auction.__name__}')

    def end_date_requests_auction(self):
        """ :return trading form """
        _div = self.response.xpath('//div[contains(text(), "Дата окончания")]/following::div[1]/text()').get()
        if _div:
            end_date_req = _div.strip().lower()
            return format_time_auction(end_date_req)
        logger.error(f'{self.response.url} :: ERROR function {self.end_date_requests_auction.__name__}')

    def start_date_trading(self):
        _div = self.soup.find('div', string=re.compile(r'Дата проведения', re.IGNORECASE)) or self.soup.find('div', string=re.compile(r'Подведение результатов торгов:', re.IGNORECASE))
        if _div:
            end_date_req = _div.findNext('div').get_text().strip().lower()
            return format_time_auction(end_date_req)
        logger.error(f'{self.response.url} :: ERROR function {self.start_date_trading.__name__}')

    def start_price(self):
        start_price = self.soup.find('div', string=re.compile(r'^Начальная цена', re.IGNORECASE))
        if start_price:
            start_price = start_price.findNext('div').get_text().strip()
            if start_price:
                return make_float(start_price)

    def get_msg_number(self):
        """ return msg number  """
        _div = self.soup.find('div',
                              string=re.compile(r'Номер сообщения в ЕФРСБ:', re.IGNORECASE))
        if _div:
            msg = _div.findNext('div').get_text().strip().lower()
            return ' '.join(re.findall(r'\d{7,8}', msg))
        logger.error(f'{self.response.url} :: ERROR function {self.get_msg_number.__name__}')

    def get_step_price(self, start_price):
        """ fetch step in RUB - if it doesn't exists fetch in % """
        try:
            _div = self.soup.find('div', string=re.compile(r'Шаг, руб.:', re.IGNORECASE))
            if _div:
                step_price = _div.findNext('div').get_text().strip()
                return make_float(step_price)
            elif _div is None:
                _div = self.soup.find('div', string=re.compile(r'Шаг, % от начальной цены:', re.IGNORECASE))
                if _div:
                    step_price = _div.findNext('div').get_text().strip()

                    return make_float(start_price * int(step_price) / 100)
            logger.debug(f'{self.response.url} :: DEBUG function {self.get_step_price.__name__}')
        except Exception as e:
            logger.error(f'{self.response.url} :: ERROR function {self.get_step_price.__name__} - {e}')
