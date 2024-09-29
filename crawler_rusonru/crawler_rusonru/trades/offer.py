from .libraries import *
import logging

logger = logging.getLogger(__name__)


class OfferParse:

    def __init__(self, response_):
        self.response = response_
        self.soup = soup(self.response)

    def table_lot_page_lot_info(self):
        """ return table with title "Information about trades" """
        table = self.soup.find('th', string=re.compile('Информация о лоте', re.IGNORECASE))
        if table:
            table = table.find_parent('table')
            return table
        else:
            logger.error(
                f'{self.response.url} :: ERROR function class Offer {self.table_lot_page_lot_info.__name__}')

    def start_price(self):
        """ return start price """
        if table := self.table_lot_page_lot_info():
            text = r'Стартовая цена'
            start_price = table.find('td', string=re.compile(text, re.IGNORECASE))
            if start_price:
                start_price = start_price.findNextSibling('td').get_text()
                start_price = re.sub(r'\.$', ' ', start_price)
                try:
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

    def get_lot_number(self):
        """ return lot number """
        if table := self.table_lot_page_lot_info():
            text = 'Номер лота'
            lot_number = table.find('td', string=re.compile(text, re.IGNORECASE))
            if lot_number:
                lot_number = lot_number.findNextSibling('td').get_text()
                if re.match(r'\d+', lot_number):
                    return dedent_func(re.sub(r'\D', '', lot_number)).strip()

    @delete_extra_symbols
    @cut_lot_number
    def get_short_name(self):
        """ return short name without lot number """
        if table := self.table_lot_page_lot_info():
            text = 'Предмет торгов'
            short_name = table.find('td', string=re.compile(text, re.IGNORECASE)).findNextSibling('td').get_text()
            return dedent_func(short_name)

    @delete_extra_symbols
    @cut_lot_number
    def get_lot_info(self):
        """ return short name without lot number """
        if table := self.table_lot_page_lot_info():
            text = r'Cведения об имуществе \(предприятии\) должника'
            lot_info = table.find('td', string=re.compile(text, re.IGNORECASE))
            if lot_info:
                lot_info = lot_info.findNextSibling('td').get_text()
            return dedent_func(lot_info)

    def property_info(self):
        """ :return property inforamtion about lot """
        if table := self.table_lot_page_lot_info():
            text = 'Порядок ознакомления с имуществом должника'
            property_info = table.find('td', string=re.compile(text, re.IGNORECASE))
            if property_info:
                property_info = property_info.findNextSibling('td').get_text()
            return dedent_func(property_info)

    def get_period_table(self):
        """ find and return table with periods """
        table = self.soup.find('table', class_='views-table int_table')
        if table is None:
            table1 = self.soup.find('th',
                                    string=re.compile(r'Дата окончания приема заявок на интервале', re.IGNORECASE))
            if table1:
                table = table1.find_parents('table')
        if table:
            df = pd.read_html(str(table))
            return df[0]

    def return_periods(self):
        """ return periods """
        check_value = int(10000000000000000000000)
        periods = list()
        df = self.get_period_table()
        try:
            for t in range(len(df)):
                start_date_request = df.iloc[t][0]
                end_date_request = df.iloc[t][1]
                end_date_trading = df.iloc[t][1]
                current_price = df.iloc[t][3]
                if not re.match(r'nan', str(current_price), re.IGNORECASE):
                    if isinstance(current_price, str):
                        current_price_ = make_float(current_price)
                    elif isinstance(current_price, float64):
                        current_price_ = round(float(current_price), 2)
                    else:
                        logger.error(f'{self.response.url} :: INVALID TYPE CURRENT PRICE')
                        current_price_ = None
                    period = {
                        'start_date_requests': format_time_auction(
                            re.sub(r'\s+', ' ', start_date_request.replace('-', ' '))),
                        'end_date_requests': format_time_auction(
                            re.sub(r'\s+', ' ', end_date_request.replace('-', ' '))),
                        'end_date_trading': format_time_auction(
                            re.sub(r'\s+', ' ', end_date_trading.replace('-', ' '))),
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

    def start_date_requests(self):
        """ return start date requests offer """
        try:
            df = self.get_period_table()
            return format_time_auction(
                            re.sub(r'\s+', ' ', str(df.iloc[0][0]).replace('-', ' ')))
            logger.error(f'{self.response.url} :: ERROR START DATE REQUESTS OFFER (1)')
        except Exception as e:
            print(e)
            logger.error(f'{self.response.url} :: ERROR START DATE REQUESTS OFFER')

    def end_date_requests(self):
        """ return end date requests offer """
        try:
            df = self.get_period_table()
            return format_time_auction(
                            re.sub(r'\s+', ' ', str(df.iloc[-1][1]).replace('-', ' ')))
            logger.error(f'{self.response.url} :: ERROR END DATE REQUESTS OFFER (1)')
        except Exception as e:
            print(e)
            logger.error(f'{self.response.url} :: ERROR END DATE REQUESTS OFFER')

    def start_date_trading(self):
        """ the same like date requests(offer) """
        return self.start_date_requests()

    def end_date_trading(self):
        """ the same like date requests(offer) """
        return self.end_date_requests()
