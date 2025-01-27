import re

from .libraries import *
import logging

logger = logging.getLogger(__name__)


class Auction:

    def __init__(self, response_):
        self.response = response_
        self.soup = soup(self.response)

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
                    return format_time_auction(start)
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
                    return format_time_auction(end)
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
                                return format_time_auction(start_trading)
                            except Exception as e:
                                print(e)
                                logger.error(f'{self.response.url} :: ERROR function {self.start_date_requests.__name__}')
            elif len(start_trading) == 1:
                try:
                    start_trading = start_trading[0]
                    start_trading = start_trading.findNextSibling('td').get_text().replace('-', ' ')
                    start_trading = re.sub(r'\s+', ' ', start_trading)
                    try:
                        return format_time_auction(start_trading)
                    except Exception as e:
                        print(e)
                        logger.error(f'{self.response.url} :: ERROR function {self.start_date_requests.__name__}')
                except Exception as e:
                    print(e)


