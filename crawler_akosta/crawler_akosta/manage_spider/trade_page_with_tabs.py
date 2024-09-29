from bs4 import BeautifulSoup as BS
import logging
import re

from crawler_akosta.utils.work_with_text_and_number import dedent_func
from crawler_akosta.utils.working_with_time import format_time_auction

logger = logging.getLogger(__name__)


class TradePage:

    def __init__(self, _response):
        self.response = _response
        self.soup = BS(str(self.response.body.decode('utf-8')).replace('&lt;', '<').replace('&gt;', '>'),
                       features='lxml')

    @property
    def get_lot_div_sector(self):
        """ get tag <div> with <a> lots """
        try:
            div_lot = self.soup.find('div', id='formMain:dataLot').find('tbody', id='formMain:dataLot_data')
            return div_lot
        except Exception as ex:
            logger.error(f'{self.response.url} :: {ex}')

    def get_post_lot_data(self):
        """ get post data (formMain....j_idt63) """
        try:
            lst_a = list()
            for a in self.get_lot_div_sector.find_all('a'):
                lst_a.append(a.get('id'))
            return lst_a
        except Exception as ex:
            logger.error(f'{self.response.url} :: {ex}')

    def get_trading_type(self):
        """ :return trading type """
        try:
            trading_type = self.soup.find('label', string=re.compile('Вид торгов', re.IGNORECASE)).parent
            trading_type = dedent_func(trading_type.get_text().strip().split('.')[-1].strip())
            offer = ('Продажа посредством публичного предложения',)
            auction = ('Открытый аукцион с открытой формой подачи предложений',
                       'Открытый аукцион с закрытой формой подачи предложений',)
            competition = ('Открытый конкурс с открытой формой подачи предложений',
                           'Открытый конкурс с закрытой формой подачи предложений')

            if trading_type in offer:
                return 'offer'
            elif trading_type in auction:
                return 'auction'
            elif trading_type in competition:
                return 'competition'
        except Exception as ex:
            logger.error(f'{self.response.url} :: {ex}')

    def get_trading_form(self):
        """ :return trading form """
        trading_form = self.soup.find('label', string=re.compile('Вид торгов', re.IGNORECASE)).parent
        trading_form = dedent_func(trading_form.get_text().strip().split('.')[-1].strip())
        _open = ('Продажа посредством публичного предложения', 'Открытый аукцион с открытой формой подачи предложений',
                 'Открытый аукцион с закрытой формой подачи предложений',
                 'Открытый конкурс с открытой формой подачи предложений',
                 'Открытый конкурс с закрытой формой подачи предложений')
        if trading_form in _open:
            return 'open'
        else:
            logger.error(f'{self.response.url} :: ERROR TRADING FORM')
            return 'open'

    def return_org_text(self):
        """ return organizer text for getting information about """
        try:
            div_organizer = self.soup.find('a', title='Перейти на карту организатора').parent
            return div_organizer
        except Exception as ex:
            logger.error(f'{self.response.url} :: ERROR ORG TEXT - {ex}')

    def get_org_name(self):
        """ return full name of organizer """
        try:
            _div = self.return_org_text()
            return dedent_func(_div.a.get_text().strip())
        except Exception as ex:
            logger.error(f'{self.response.url} :: ERROR org name {ex}')

    def get_org_email(self):
        """ return org email """
        try:
            _div = self.return_org_text()
            pattern_mail = re.compile(r"([a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+)")
            email = pattern_mail.findall(_div.get_text().strip())
            return dedent_func(' '.join(email))
        except Exception as ex:
            logger.error(f'{self.response.url} :: ERROR organizer email {ex}')

    def get_org_phone(self):
        """ return organizer phone """
        _div = self.return_org_text()
        p_in_div = _div.find_all('p')
        if len(p_in_div) > 0:
            phone = ''.join([p.get_text().strip() for p in p_in_div if 'Тел.' in p.get_text().strip()])
            phone = ''.join(
                [x for x in phone.split(':')[-1] if x.isdigit() or x == '+' or x == '(' or x == ')' or x == ' '])
            phone = phone.strip()
            if len(phone) > 5:
                return phone
            else:
                return ''

    def get_org_contacts(self) -> dict:
        """ :return org contacts  """
        try:
            email = self.get_org_email()
            phone = self.get_org_phone()
            return {'email': email, 'phone': phone}
        except Exception as e:
            logger.error(f'{self.response.url} :: func get_org_contacts {e}')
            return dict()

    def get_lot_number(self, _id):
        """ return lot_number """
        try:
            tr = self.soup.find('a', id=_id)
            if tr:
                tr = tr.parent.parent
                if tr:
                    tr = tr.find('td').get_text()
                    return tr
        except Exception as ex:
            logger.error(f'{self.response.url} :: {ex}')

    def get_short_name(self):
        """ return short name """
        try:
            pass
        except Exception as ex:
            logger.error(f'{self.response.url} :: {ex}')

    # AUCTION TYPE

    def start_date_trading_auc(self):
        """ :return start date request auction """
        try:
            start = self.soup.find('label', string=re.compile('Дата и время начала аукциона', re.IGNORECASE))
            if start:
                start = start.parent
                start = dedent_func(start.get_text().strip().split(':', maxsplit=1)[-1].strip())
                start = re.sub(r'\s+', ' ', start)
                start = ''.join(re.findall(r'\d{1,2}.\d{1,2}.\d{2,4}\s\s?\d{1,2}:\d{1,2}', start)[0])
                if start:
                    return format_time_auction(start)
                else:
                    logger.error(f'{self.response.url} :: START DATE WAS NOT FOUND (2)')
            else:
                logger.error(f'{self.response.url} :: START DATE WAS NOT FOUND (1)')
        except Exception as e:
            logger.error(f'{self.response.url} :: ERROR start date request auction {e}')

    def end_date_end_auc(self):
        """ :return end date request auction """
        try:
            end = self.soup.find('label', string=re.compile('Дата и время завершения аукциона', re.IGNORECASE))
            if end:
                end = end.parent
                end = dedent_func(end.get_text().strip().split(':', maxsplit=1)[-1].strip())
                end = re.sub(r'\s+', ' ', end)
                end = ''.join(re.findall(r'\d{1,2}.\d{1,2}.\d{2,4}\s\s?\d{1,2}:\d{1,2}', end)[0])
                if end:
                    return format_time_auction(end)
                else:
                    logger.error(f'{self.response.url} :: END DATE WAS NOT FOUND (2)')
            else:
                logger.error(f'{self.response.url} :: END DATE WAS NOT FOUND (1)')
        except Exception as e:
            logger.error(f'{self.response.url} :: ERROR end date request auction {e}')

    def return_period_trading_auc(self) -> list or None:
        """ :return 2 dates start and end date trading in list
         first index is start date trading
         second index is end date trading
         """
        try:
            period_auc = self.soup.find('label', string=re.compile('Период приема заявок', re.IGNORECASE))
            period_auc = dedent_func(period_auc.parent.get_text().strip().split(':', maxsplit=1)[-1].strip())
            period_auc = re.sub(r'\s+', ' ', period_auc)
            pattern_perio_auc = re.compile(r'\d{1,2}.\d{1,2}.\d{2,4}\s\s?\d{1,2}:\d{1,2}')
            lst_start_trading = pattern_perio_auc.findall(period_auc)
            return lst_start_trading
        except Exception as e:
            logger.error(f'{self.response.url} :: ERROR during return periods of trading auction {e}')

    def start_date_request_auc(self):
        """ :return start date trading """
        try:
            lst = self.return_period_trading_auc()
            if 1 <= len(lst) < 3:
                _date = format_time_auction(lst[0])
                return _date
            else:
                logger.error(f'{self.response.url} :: check data for start date trading auction ')
        except Exception as e:
            logger.error(f'{self.response.url} :: ERROR START DATE TRADING AUCTION {e}')

    def end_date_request_auc(self):
        """ :return end date trading """
        try:
            lst = self.return_period_trading_auc()
            if len(lst) == 2:
                _date = format_time_auction(lst[1])
                return _date
            else:
                logger.error(f'{self.response.url} :: check data for END date trading auction ')
        except Exception as e:
            logger.error(f'{self.response.url} :: ERROR START DATE TRADING AUCTION {e}')
