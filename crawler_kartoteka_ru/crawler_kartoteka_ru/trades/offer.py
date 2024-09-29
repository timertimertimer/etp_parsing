from numpy import float64

from crawler_kartoteka_ru.utils.work_with_text_and_number import cut_lot_number, get_lot_number, delete_extra_symbols, \
    dedent_func, make_float
from bs4 import BeautifulSoup as BS
import re
import pandas as pd
import logging

from crawler_kartoteka_ru.utils.working_with_time import format_time_auction

logger = logging.getLogger(__name__)


class OfferPage:

    def __init__(self, response_):
        self.response = response_
        self.soup = BS(str(self.response.text), features='lxml')

    def get_title_lot(self, table):
        """
        :arg table -> table with unique lot info
        return tile of lot for current table """
        try:
            table = BS(str(table), features='lxml')
            return table.find('th').get_text()
        except Exception as e:
            print(e)
            return None

    @get_lot_number
    def get_lot_number(self, title):
        """ return lotnumber  """
        if title:
            return dedent_func(title)
        else:
            return None

    @delete_extra_symbols
    @cut_lot_number
    def get_short_name(self, title):
        """ return short name  """
        if title:
            return dedent_func(title)
        else:
            return None

    def get_lot_info(self, table):
        """ return lot info """
        if table:
            lot_info = table.find('td', string=re.compile(r'Cведения об имуществе \(предприятии\)', re.IGNORECASE))
            if lot_info:
                return dedent_func(lot_info.findNext('td').get_text())

    def get_property_info(self, table):
        """ return property info """
        if table:
            prop_info = table.find('td', string=re.compile(r'Порядок ознакомления с имуществом', re.IGNORECASE))
            if prop_info:
                return dedent_func(prop_info.findNext('td').get_text())

    def start_price(self, table):
        """ return start price """
        if table:
            price = table.find('td', string=re.compile(r'Начальная цена продажи', re.IGNORECASE))
            if price:
                price = dedent_func(price.findNext('td').get_text())
                return make_float(price)

    def get_status(self, table):
        """ return status of current lot """
        if table:
            status = table.find('td', string=re.compile(r'Статус торгов', re.IGNORECASE))
            if status:
                status = dedent_func(status.findNext('td').get_text()).lower()
                active = ('идёт приём заявок', 'идет прием заявок')
                pending = ('объявлены',)
                ended = ('приём заявок завершен', 'в стадии проведения', 'подводятся итоги',
                         'торги завершены', 'торги отменены', 'прием заявок завершен',
                         'идёт приём заявок (приостановлены)')
                try:
                    if status in active:
                        return 'active'
                    elif status in pending:
                        return 'pending'
                    elif status in ended:
                        return 'ended'
                except Exception as e:
                    logger.error(f'{self.response.url} :: ERROR STATUS {e}')

    def find_period_table(self, table):
        """ return periods table """
        try:
            table_ = table.find("table", class_="data inner")
            if table_ is None:
                table_ = table.find('div', string=re.compile(r'Периоды проведения торгов', re.IGNORECASE)).findNext(
                    'table')
            table = pd.read_html(re.sub(r',', '.', str(table_)))
            df = table[0]
            return df
        except Exception as e:
            print(e)
            logger.error(f'{self.response.url} :: ERROR PERIOD TABLE IS NOT FOUND')

    def start_date_requests_offer(self, table):
        """ return start date req offer from period table """
        try:
            df = self.find_period_table(table)
            return format_time_auction(str(df.iloc[0][0]))
        except Exception as e:
            print(e)
            print(self.find_period_table(table))
            logger.error(f'{self.response.url}  :: ERROR function {self.start_date_requests_offer.__name__}')

    def end_date_requests_offer(self, table):
        """ return end date requests offer from period table """
        try:
            df = self.find_period_table(table)
            return format_time_auction(str(df.iloc[-1][1]))
        except Exception as e:
            print(e)
            logger.error(f'{self.response.url}  :: ERROR function {self.end_date_requests_offer.__name__}')

    def start_date_trading_ofer(self, table):
        """ date trading offer the same like start date requests offer """
        return self.start_date_requests_offer(table)

    def end_date_trading_offer(self, table):
        """ end date trading the same like end date requests offer """
        return self.end_date_requests_offer(table)

    def get_periods_offer(self, table):
        """ return periods offer """
        check_value = int(10000000000000000000000)
        periods = list()
        df = self.find_period_table(table)
        try:
            for t in range(len(df)):
                start_date_request = df.iloc[t][0]
                end_date_request = df.iloc[t][1]
                end_date_trading = df.iloc[t][1]
                current_price = df.iloc[t][2]
                if not re.match(r'nan', str(current_price), re.IGNORECASE):
                    if isinstance(current_price, str):
                        current_price_ = make_float(current_price)
                    elif isinstance(current_price, float64):
                        current_price_ = round(float(current_price), 2)
                    else:
                        logger.error(f'{self.response.url} :: INVALID TYPE CURRENT PRICE')
                        current_price_ = None
                    period = {
                        'start_date_requests': format_time_auction(start_date_request),
                        'end_date_requests': format_time_auction(end_date_request),
                        'end_date_trading': format_time_auction(end_date_trading),
                        'current_price': current_price_
                    }
                    periods.append(period)
                    if check_value < current_price_:
                        logger.critical(
                            f'{self.response.url} :: ERROR INVALID PRICE ON PERIOD - CURRENT PRICE HIGHER THAN PREVIUOS',
                            df)
                    check_value = current_price_
            return periods
        except Exception as e:
            logger.error(f'{self.response.url} :: ERROR PERIODS  {e}\n{df}', exc_info=True)
            return None
