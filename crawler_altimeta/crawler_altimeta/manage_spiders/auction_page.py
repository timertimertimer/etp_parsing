from ..locators.locator_lot_page import LocatorLotPage
from ..locators.locators_trade_page import LocatorTradePage
from ..utils.work_with_text_and_number import dedent_func, get_lot_number, make_float, cut_lot_number, \
    delete_extra_symbols
from ..utils.working_with_time import format_time_auction
from bs4 import BeautifulSoup as BS
import re
import logging

logger = logging.getLogger(__name__)


class AucPage:
    def __init__(self, response_):
        self.response = response_
        self.loc = LocatorTradePage
        self.loc_lot = LocatorLotPage
        self.soup = BS(str(self.response.text).replace('&lt;', '<').replace('&gt;', '>'), features='lxml')

    def start_date_request_auc(self):
        """ get and return start date request  auction """
        date = self.response.xpath(self.loc.start_date_request_loc).get()
        date = BS(str(date), features='lxml').get_text()
        return format_time_auction(date)

    def end_date_request_auc(self):
        """ get and return end date request  auction """
        date = self.response.xpath(self.loc.end_date_request_loc).get()
        date = BS(str(date), features='lxml').get_text()
        return format_time_auction(date)

    def start_date_trading_auc(self):
        """ get and return start date trading  auction """
        date = self.response.xpath(self.loc.start_date_trading_loc).get()
        if date is None:
            date = self.response.xpath(self.loc.end_date_trading_loc).get()
            date = BS(str(date), features='lxml').get_text()
        date = BS(str(date), features='lxml').get_text()
        return format_time_auction(date)

    def end_date_trading_auc(self):
        """ get and return end date trading auction """
        date = self.response.xpath(self.loc.end_date_trading_loc).get()
        date = BS(str(date), features='lxml').get_text()
        return format_time_auction(date)

    def get_all_lot_tables(self):
        """ fetch all lotstables) on page and return list with tables(lot info) on page """
        tables_all = self.response.xpath(self.loc_lot.get_all_table).getall()
        return tables_all

    def get_status(self, table_):
        """ :arg table_ -> current table from iteration
            :return short name (text)
            """
        table = BS(str(table_), features='lxml')
        status = table.find('tbody').find('td', string=re.compile('татус торгов'))
        if status is not None:
            status = dedent_func(status.findNext('td').get_text().strip().lower())
            active = ('идет прием заявок', 'идет приём заявок', 'идёт приём заявок', 'идёт приём заявок (приостановлены)')
            pending = ('объявлены', 'объявлены (приостановлены)')
            ended = ('прием заявок завершен', 'приём заявок завершен (приостановлены)',
                     'в стадии проведения', 'подводятся итоги', 'подводятся итоги (приостановлены)', 'торги отменены (приостановлены)',
                     'торги завершены', 'торги отменены', 'приём заявок завершен', 'торги завершены (приостановлены)')
            if status in active:
                return 'active'
            elif status in pending:
                return 'pending'
            elif status in ended:
                return 'ended'
            else:
                logger.error(f'{str(self.response.text)[:200]} :: !!!! ERROR !!!! STATUS !!!! ERROR WITH TEXT '
                             f'{self.response.url}')
        else:
            logger.error(f'{str(self.response.text)[:200]} :: !!!! ERROR !!!! STATUS !!!! {self.response.url}')

    def get_th_of_table(self, table_):
        """ :return title of lot information """
        table = BS(str(table_), features='lxml')
        th = table.find('th').get_text()
        try:
            return th
        except Exception as e:
            logger.error(f'{self.response.url} :: ERROR LOT TITLE {e}', exc_info=True)

    @get_lot_number
    def get_lot_number(self, table_):
        """ :return lot number """
        return self.get_th_of_table(table_)

    def get_short_name(self, table_):
        """ :arg table_ -> current table from iteration
            :return short name (text)
            """
        table = BS(str(table_), features='lxml')
        # first search <td> field with short name information
        short_name = table.find('tbody').find('td', string=re.compile('редмет торгов'))
        if short_name is not None:
            return short_name.findNext('td').get_text().strip().replace("'", "\"")
        else:
            short_name = re.split(r':', self.get_th_of_table(table_), maxsplit=1)
            if len(short_name) == 2:
                return dedent_func(short_name[1].strip())
            else:
                return None

    @staticmethod
    def get_lot_info(table_):
        """ :arg table_ -> current table from iteration
            :return lot info (text)
            """
        table = BS(str(table_), features='lxml')
        lot_info = table.find('tbody').find('td', string=re.compile(r'ведения об имуществе \(предприятии\) должника'))
        if lot_info is not None:
            return lot_info.findNext('td').get_text().strip().replace("'", "\"")

    @staticmethod
    def get_property_info(table_):
        """ :arg table_ -> current table from iteration
            :return property info (text)
            """
        table = BS(str(table_), features='lxml')
        property_info = table.find('tbody').find('td',
                                                 string=re.compile(r'орядок ознакомления с имуществом \(предприятием\)'))
        if property_info is not None:
            return property_info.findNext('td').get_text().strip().replace("'", "\"")

    def get_start_price(self, table_):
        """ :arg table_ current iterated table with lot info
             :return start_price of lot """
        table = BS(str(table_), features='lxml')
        start_price = table.find('tbody').find('td', string=re.compile('ачальная цена продажи имущес'))
        if start_price is not None:
            start_price = start_price.findNext('td').get_text().strip().replace("'", "\"")
            if len(start_price) < 60 and re.match(r'^\d+', start_price):
                start_price = start_price
            else:
                start_price = self.response.xpath('//td[contains(., "руб, НДС не облагается")]').get()
                start_price = BS(str(start_price), features='lxml').get_text()
            try:
                return make_float(start_price)
            except ValueError as e:
                logger.error(f'{self.response.url} ::: ERROR {e} ::: START PRICE', exc_info=True)
                return None

    def get_step_price(self, table_):
        """ :arg table_ current iterated table with lot info
                     :return start_price of lot """
        table = BS(str(table_), features='lxml')
        step_price = table.find('tbody').find('td', string=re.compile('еличина повышения начальной це'))
        if step_price is not None:
            step_price = step_price.findNext('td').get_text().strip()
            step = re.split(r'\(', step_price, maxsplit=1)[0].replace(',', '.')
            step = ''.join(re.findall(r'(^\d+)\.?', step))
            try:
                step = float(self.get_start_price(table_)) * float(step) / 100 if self.get_start_price(
                    table_) else None
                return round(step, 2)
            except ValueError as e:
                logger.error(f'{self.response.url} ::: ERROR {e} ::: STEP PRICE', exc_info=True)
                return None

