from bs4 import BeautifulSoup as BS
import re
from ..utils.working_with_time import format_time_auction
from ..utils.work_with_text_and_number import dedent_func, make_float
import logging

logger = logging.getLogger(__name__)


class AuctionPage:

    def __init__(self, response_):
        self.response = response_
        self.soup = BS(str(self.response.text), features='lxml')

    def step_price(self, table, start_price):
        """ return start price """
        if table:
            price = table.find('td', string=re.compile(r'Величина повышения начальной цены', re.IGNORECASE))
            if price:
                step_price = dedent_func(price.findNext('td').get_text()).replace(',', '.')
                if '(' in step_price:
                    step_rub = re.split(r'\(', step_price, maxsplit=1)[1].replace(')', '').strip()
                    return make_float(step_rub)
                elif '%' in step_price:
                    find_percent = re.findall(r'\d{1,2}.*%', step_price)
                    if len(find_percent) > 0:
                        if '%' in find_percent[0]:
                            per = find_percent[0].replace('%', '').strip()
                            per = int(float(per))
                            return round(start_price * (per / 100), 2)

    def get_table_time_frames_auction(self):
        """ return table with auction time shcedule data """
        try:
            table_arbitr_info = self.soup.find('th',
                                               string=re.compile(r'Информация о торгах', re.IGNORECASE)).findParent(
                'table')
            return table_arbitr_info
        except Exception as e:
            print(e)
            logger.error(f'{self.response.url} :: ERROR function {self.get_table_time_frames_auction.__name__}')

    def get_start_date_requests_auc(self):
        """ :return start date request auction """
        try:
            if table := self.get_table_time_frames_auction():
                start = table.find('td', string=re.compile(r'ачало предоставления заявок на участи', re.IGNORECASE))
                if start:
                    start = start.find_next('td').get_text()
                    return format_time_auction(dedent_func(start))
        except Exception as e:
            print(e)
            logger.error(f'{self.response.url} :: ERROR function {self.get_start_date_requests_auc.__name__}')

    def get_end_date_requests_auc(self):
        """ return start date requests auction """
        try:
            if table := self.get_table_time_frames_auction():
                end = table.find('td', string=re.compile(r'Окончание предоставления заявок на участие', re.IGNORECASE))
                if end:
                    end = end.find_next('td').get_text()
                    return format_time_auction(dedent_func(end))
        except Exception as e:
            print(e)
            logger.error(f'{self.response.url} :: ERROR function {self.get_end_date_requests_auc.__name__}')

    def get_start_date_trading_auc(self):
        """ start date trading auction """
        try:
            if table := self.get_table_time_frames_auction():
                start = table.find('td', string=re.compile(r'ачало подачи предложений о цене имуществ', re.IGNORECASE))
                if start:
                    start = start.find_next('td').get_text()
                    return format_time_auction(dedent_func(start))
        except Exception as e:
            print(e)
            logger.error(f'{self.response.url} :: ERROR function {self.get_start_date_trading_auc.__name__}')

    def get_end_date_trading_auc(self):
        """ return end date trading auction """
        try:
            if table := self.get_table_time_frames_auction():
                end = table.find('td', string=re.compile(r'ата и время подведения результатов торго', re.IGNORECASE))
                if end:
                    end = end.find_next('td').get_text()
                    return format_time_auction(dedent_func(end))
        except Exception as e:
            print(e)
            logger.error(f'{self.response.url} :: ERROR function {self.get_end_date_trading_auc.__name__}')
