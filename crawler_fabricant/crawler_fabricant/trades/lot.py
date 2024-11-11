import logging
from ..utils.work_with_text_and_number import *
from ..utils.working_with_time import get_time_data, format_time
from ..locators.locator_lot import LocatorLot
from ..spiders.fabricant import pd
from bs4 import BeautifulSoup as BS
from lxml import etree

logger = logging.getLogger(__name__)


class LotParse:
    def __init__(self, response, lot):
        self.response = response
        self.lot = lot
        self.loc = LocatorLot()
        self.bs = BS(lot, features='lxml')
        self.dom = etree.HTML(str(self.bs))

    @get_lot_number
    def get_lot_number(self):
        """return lot number"""
        return self.dom.xpath(self.loc.lot_number_loc)

    def get_short_name(self):
        """:return short name from lot html div sector"""
        try:
            short_name = self.dom.xpath(self.loc.short_name_loc) or self.dom.xpath(self.loc.short_name_loc2)
            return dedent_func(short_name)
        except:
            return None

    def property_info(self):
        """:return property info from lot html div sector"""
        return dedent_func(self.dom.xpath(self.loc.property_info_loc))

    def get_periods_table(self):
        """return list of periods tables"""
        try:
            periods = self.bs.find_all('table')
            return periods
        except:
            logger.error(f'{self.response.url} :: PERIODS NOT FOUND', exc_info=True)

    def start_date_request(self):
        """:arg html div with lot info"""
        lst_periods = self.get_all_periods()
        try:
            return lst_periods[0].get('start_date_requests')
        except:
            return None

    def end_date_request(self):
        """:arg html div with lot info"""
        lst_periods = self.get_all_periods()
        try:
            return lst_periods[-1].get('end_date_requests')
        except:
            return None

    def start_date_trading(self):
        """return function start date request"""
        return self.start_date_request()

    def end_date_trading(self):
        """:return function end_date_request"""
        return self.end_date_request()

    def start_price(self):
        """get start price offer lot"""
        lst_periods = self.get_all_periods()
        try:
            return lst_periods[0].get('current_price')
        except:
            logger.warning(f'{self.response.url} :: INVALID DATA START PRICE OFFER')
            return None

    def get_all_periods(self):
        """
        :arg html div with lot info
        :return list with dict values of offer periods"""
        try:
            periods = list()
            for table in self.get_periods_table():
                try:
                    table_ = pd.read_html(str(table))
                except:
                    pass
                try:
                    if len(table_[0]) < 7 and len(table_[0]) > 2:
                        start = table_[0][1][1]
                        end = table_[0][1][2]
                        price = table_[0][1][3]
                        period = {
                            'start_date_requests': get_time_data(start, 0, url=self.response.url),
                            'end_date_requests': get_time_data(end, 0, url=self.response.url),
                            'end_date_trading': get_time_data(end, 0, url=self.response.url),
                            'current_price': get_price(price)
                        }
                        periods.append(period)
                except:
                    continue
            return periods
        except:
            logger.error(f'{self.response.url} :: INVALID DATA PERIODS OFFER', exc_info=True)

    # AUCTION
    def start_req_auc(self):
        try:
            return format_time(self.dom.xpath(self.loc.start_request_auction))
        except Exception as e:
            print(e)
            return None

    def end_req_auc(self):
        try:
            return format_time(self.dom.xpath(self.loc.end_request_auction))
        except Exception as e:
            print(e)
            return None

    def start_trading_auc(self):
        try:
            return format_time(self.dom.xpath(self.loc.start_trading_auction))
        except Exception as e:
            print(e)
            return None

    def end_trading_auc(self):
        try:
            return format_time(self.dom.xpath(self.loc.end_date_trading_auc))
        except Exception as e:
            print(e)
            return None

    def start_price_auc(self):
        match = re.search(r'\d+\.\d{1,2}', self.dom.xpath(self.loc.start_price_auc).replace('\xa0', '').replace(',', '.'))
        try:
            if match:
                return float(match.group())
        except (ValueError, TypeError) as e:
            print(e)
            return None

    def step_price_auc(self):
        _div_step = self.dom.xpath(self.loc.step_price_auc)
        if _div_step:
            step = ''.join(re.findall(r'^\d*\,?\d+', _div_step.replace('\xa0', ''))).replace(',', '.')
            start_price = self.start_price_auc()

            try:
                step = float(step)
                return round(start_price * step / 100, 2)
            except (ValueError, TypeError):
                return None