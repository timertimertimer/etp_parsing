import logging
import re

import pandas as pd
from bs4 import BeautifulSoup
from numpy import float64

from general_utils import dedent_func, format_time, make_float

logger = logging.getLogger(__name__)


class OfferParse:

    def __init__(self, response_):
        self.response = response_
        self.soup = BeautifulSoup(self.response.text, 'lxml')

    def get_lot_block(self, table: str):
        """ :return table with lot info """
        try:
            if table and len(table) > 0:
                table_html = BeautifulSoup(str(table), features='lxml')
                return table_html
        except Exception as ex:
            logger.error(f'{self.response.url} :: ERROR TABLE LOT INFO {ex}', exc_info=True)
            return None

    def get_lot_status(self, table: str):
        """ :return status of lot """
        active = ('прием заявок', 'приём заявок')
        pending = ('торги объявлены', 'торги обьявлены')
        ended = ('прием заявок завершен', 'идут торги', 'подведение итогов',
                 'торги завершены', 'торги не состоялись', 'торги приостановлены',
                 'торги отменены', 'приём заявок завершен')
        try:
            block = self.get_lot_block(table=table)
            status = block.find('td', string=re.compile("Статус торгов", re.IGNORECASE)).findNext(
                'td').get_text().lower()
            status = dedent_func(status.strip())
            if status in active:
                return 'active'
            elif status in pending:
                return 'pending'
            elif status in ended:
                return 'ended'
        except Exception as ex:
            logger.error(f'{self.response.url} :: Invalid data get_lot_status {ex}')

    def get_lot_number(self, table: str):
        """ :return lot number """
        try:
            block = self.get_lot_block(table)
            if block:
                lot_number = block.find('td', string=re.compile("Номер лота", re.IGNORECASE)).findNext('td').get_text()
                num = dedent_func(lot_number.strip())
                if re.match(r'^\d+$', num):
                    return num
                else:
                    logger.error(f'{self.response.url} :: INVALID DATA LOT NUMBER')
        except Exception as ex:
            logger.error(f'{self.response.url} :: ERROR LOT NUMBER {ex}')

    def get_short_name(self, table: str):
        """ get short name of lot """
        try:
            block = self.get_lot_block(table=table)
            if block:
                short = block.find('td', string=re.compile("Наименование имущества", re.IGNORECASE))
                if short:
                    short = dedent_func(short.findNext('td').get_text().strip())
                    return short
        except Exception as ex:
            logger.error(f'{self.response.url} :: INVALID DATA SHORT NAME {ex}')

    def get_lot_info(self, table: str):
        """ get lot info """
        try:
            block = self.get_lot_block(table=table)
            if block:
                lot_info = block.find('td',
                                      string=re.compile("Cведения об имуществе \(предприятии\) должника",
                                                        re.IGNORECASE))
                if lot_info:
                    lot_info = dedent_func(lot_info.findNext('td').get_text().strip())
                    return lot_info
        except Exception as ex:
            logger.error(f'{self.response.url} :: INVALID DATA LOT INFO {ex}')

    def get_property_info(self, table: str):
        """ get property info """
        try:
            block = self.get_lot_block(table=table)
            if block:
                properti = block.find('td',
                                      string=re.compile("Порядок ознакомления с имуществом", re.IGNORECASE))
                if properti:
                    properti = dedent_func(properti.findNext('td').get_text().strip())
                    return properti
        except Exception as ex:
            logger.error(f'{self.response.url} :: INVALID DATA PROPERTY INFO {ex}')

    def start_price_AUCTION(self, table: str) -> float or None:
        """ :return start price  !!!! auction """
        try:
            # bs4 object
            block = self.get_lot_block(table=table)
            if block:
                price = block.find_all('td', string=re.compile('Начальная цена', re.IGNORECASE))
                if len(price) == 1:
                    price = price[0]
                    price = dedent_func(price.findNext('td').get_text().strip())
                    price = ''.join(re.sub(r"\s", "", price)).replace(',', '.')
                    price = price.replace('руб', '').strip()
                    return round(float(price), 2)
                elif len(price) >= 2:
                    for p in price:
                        if len(p.get_text().strip()) < 15:
                            price = p.findNext('td').get_text()
                            price = ''.join(re.sub(r"\s", "", price)).replace(',', '.')
                            price = price.replace('руб', '').strip()
                            return round(float(price), 2)
                else:
                    logger.error(f'{self.response.url} :: INVALID DATA START PRICE')
        except Exception as ex:
            logger.error(f'{self.response.url} :: ERROR start price auction {ex}')
            return None

    def step_price_AUCTION(self, table: str) -> float or None:
        """ :return step price !!!! auction"""
        try:
            # bs4 object
            block = self.get_lot_block(table=table)
            if block:
                step = block.find_all('td', string=re.compile('Шаг', re.IGNORECASE))
                if len(step) == 1:
                    step = step[0]
                    step = dedent_func(step.findNext('td').get_text().strip())
                    step = ''.join(re.sub(r"\s", "", step)).replace(',', '.')
                    step = step.replace('руб', '').strip()
                    return round(float(step), 2)
                elif len(step) >= 2:
                    for p in step:
                        if len(p.get_text().strip()) < 15:
                            price = p.findNext('td').get_text()
                            price = ''.join(re.sub(r"\s", "", price)).replace(',', '.')
                            price = price.replace('руб', '').strip()
                            return round(float(price), 2)
        except Exception as ex:
            logger.error(f'{self.response.url} :: ERROR step price {ex}')
            return None

    def get_period_table(self, table: str):
        """ :arg table -> parent table of lot
            :return period table
        """
        try:
            block = self.get_lot_block(table=table)
            if block:
                # find period table using class_
                table_1 = block.find("table", class_="views-table inner discount_int")
                if table_1:
                    table_1 = table_1
                else:
                    # if table not found, used string search
                    table_1 = block.find('th', string=re.compile("ата начала приема заявок", re.IGNORECASE))
                    if table_1:
                        table_1 = table_1.find_parent('table')
                if table_1:
                    _table = pd.read_html(str(table_1))
                    df = _table[0]
                    return df
                else:
                    logger.critical(f'{self.response.url} :: TABLE PERIODS NOT FOUND')
        except Exception as ex:
            logger.error(f'{self.response.url} :: INVALID DATA PERIODS OFFER {ex}')

    def start_date_request_offer(self, table: str):
        """ :return start date request  """
        try:
            table_period = self.get_period_table(table)
            start_date = table_period.iloc[0][0]
            return format_time(start_date)
        except Exception as ex:
            logger.error(f'{self.response.url} :: INVALID DATA START DATE TRADING OFFER {ex}')

    def end_date_request_offer(self, table: str):
        """ :return end date request """
        try:
            table_period = self.get_period_table(table)
            end_date = table_period.iloc[-1][1]
            return format_time(end_date)
        except Exception as ex:
            logger.error(f'{self.response.url} :: INVALID DATA END DATE TRADING {ex}')

    def start_date_trading_offer(self, table: str):
        """ :return start date trading - the same like s d r """
        return self.start_date_request_offer(table)

    def end_date_trading_offer(self, table: str):
        """ :return end date trading offer -> the same like end date request """
        return self.end_date_request_offer(table)

    def return_periods(self, table_):
        """ return periods  """
        check_value = int(10000000000000000000000)
        periods = list()
        df = self.get_period_table(table_)
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
                        'start_date_requests': format_time(start_date_request),
                        'end_date_requests': format_time(end_date_request),
                        'end_date_trading': format_time(end_date_trading),
                        'current_price': current_price_
                    }
                    periods.append(period)
                    if check_value < current_price_:
                        logger.critical(
                            f'{self.response.url} :: INVALID PRICE ON PERIOD - CURRENT PRICE HIGHER THAN PREVIUOS', df)
                    check_value = current_price_
            return periods
        except Exception as e:
            logger.error(f'{self.response.url} :: PERIODS ERROR {e}\n{df}', exc_info=True)
            return None

    def start_price_offer(self, table_):
        """ :return start price offer from period table """
        try:
            table_period = self.get_period_table(table_)
            current_price = table_period.iloc[0][2]
            if isinstance(current_price, str):
                current_price_ = make_float(current_price)
            elif isinstance(current_price, float64):
                current_price_ = round(float(current_price), 2)
            else:
                logger.error(f'{self.response.url} :: INVALID TYPE CURRENT PRICE')
                current_price_ = None
            return current_price_
        except Exception as ex:
            logger.error(f'{self.response.url} :: INVALID DATA END DATE TRADING {ex}')

    def table_lot_page_lot_info(self):
        """ return table with title "Information about trades" """
        table = self.soup.find('th', class_='table_header')
        if table:
            table = table.find_parent('table')
            return table
        else:
            logger.error(
                f'{self.response.url} :: ERROR function class Offer {self.table_lot_page_lot_info.__name__}')

    def start_price(self):
        """ return start price """
        if table := self.table_lot_page_lot_info():
            text = r'Начальная цена'
            start_price = table.find('td', string=text)
            if start_price:
                try:
                    start_price = start_price.findNextSibling('td').get_text()
                    start_price = re.sub(r'\.$', ' ', start_price)
                    return make_float(start_price)
                except Exception as e:
                    print(e)
                    logger.error(f'{self.response.url} :: ERROR function {self.start_price.__name__}')
        logger.error(f'{self.response.url} :: ERROR function {self.start_price.__name__} START PRICE')

    def step_price(self):
        """ return step price auction """
        if table := self.table_lot_page_lot_info():
            text = r'Шаг аукциона'
            step_price = table.find('td', string=re.compile(text, re.IGNORECASE))
            if step_price is not None:
                step_price = step_price.findNextSibling('td').get_text()
                step_price = re.sub(r'\.$', ' ', step_price)
                try:
                    return make_float(step_price)
                except Exception as e:
                    print(e)
                    logger.error(f'{self.response.url} :: ERROR function {self.start_price.__name__}')
