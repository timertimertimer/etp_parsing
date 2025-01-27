from ..locators.locator_trades import LocatorOffer
import pandas as pd
from bs4 import BeautifulSoup as BS
import logging
from ..utils.working_with_time import format_time
import re

logger = logging.getLogger(__name__)


class OfferParse:
    def __init__(self, response_):
        self.response = response_
        self.loc = LocatorOffer
        self.soup = BS(str(self.response.body.decode('utf-8')).replace('&lt;', '<').replace('&gt;', '>'),
                       features='lxml')

    @property
    def get_organizer_div(self):
        """return div block with organizer info"""
        try:
            _div = self.response.xpath(self.loc.organizator_div_loc).get()
            if _div:
                return _div
            else:
                logger.error(f'{self.response.url} :: NO ORGANIZER DATA !!!!! ')
                return None
        except Exception as e:
            logger.error(f'{self.response.url} :: INVALID ORGANIZER DATA \n\n {e}')

    @property
    def get_arbitr_fieldset(self):
        """:return tag <fieldset> with arbitr or finance consultant info"""
        try:
            field = self.response.xpath(self.loc.arbitr_fieldset_loc).get()
            if field:
                return field
            else:
                logger.error(f'{self.response.url} :: NO ARBITR DATA !!!!! ')
                return None
        except Exception as e:
            logger.error(f'{self.response.url} :: INVALID DATA ARBITR MANAGER FIELD \n\n {e}')
            return None

    @property
    def get_debitor_info(self):
        """return block <fieldset> with all info about debitor? case number, msg_number"""
        try:
            field = self.response.xpath(self.loc.debitor_info_fieldset_loc).get()
            if field:
                return field
            else:
                logger.error(f'{self.response.url} :: NO DEBITOR DATA !!!!! ')
                return None
        except Exception as e:
            logger.error(f'{self.response.url} :: INVALID NO DEBITOR DATA \n\n {e}')
            return None

    @property
    def get_periods_table(self):
        """return all periods (tbody)"""
        try:
            table = self.response.xpath(self.loc.tbody_periods_loc).get()
            soup = BS(str(table), features='lxml')
            tag_head = soup.thead
            tag_head.decompose()
            tbody = pd.read_html(re.sub(r',', '.', str(soup)), header=None)
            return tbody[0]
        except:
            return None

    def get_period_table(self):
        """ return table with periods """
        try:
            table = self.soup.find('tbody', id="formMain:j_idt272_data").parent
            return table
        except Exception as ex:
            logger.error(f'{self.response.url} :: ERROR PERIOD TABLE {ex}')

    @property
    def return_periods(self):
        """return list object with all periods of lot(offer)"""
        check_value = 10000000000000000000000
        periods = list()
        tbody_periods = self.get_periods_table
        for p in range(len(tbody_periods)):
            start = tbody_periods.iloc[p][0]
            end = tbody_periods.iloc[p][1]
            price_ = tbody_periods.iloc[p][4]
            try:
                if isinstance(price_, str):
                    price = ''.join(re.sub(r"\s", "", price_)).replace(',', '.')
                    price = round(float(price), 2)
                else:
                    price = round(float(price_), 2)
                if check_value < price:
                    logger.critical(f'{self.response.url} :: INVALID PRICE ON PERIOD - CURRENT PRICE HIGHER THAN PREVIUOS')
                else:
                    check_value = price
            except:
                print(type(price_))
                logger.error(f'{self.response.url} Period Price - {price_} typeof - {type(price_)}')
                return None
            try:
                period = {
                    'start_date_requests': format_time(start),
                    'end_date_requests': format_time(end),
                    'end_date_trading': format_time(end),
                    'current_price': price
                }
                periods.append(period)
            except:
                continue
        return periods

    @property
    def start_date_request(self):
        """:return start_date_request of trade"""
        try:
            tbody_periods = self.get_periods_table
            return format_time(tbody_periods.iloc[0][0])
        except Exception as e:
            logger.error(f'{self.response.url} :: INVALID DATA START DATE REQUEST OFFER \n\n\n', e)
            return None

    @property
    def end_date_request(self):
        """:return end_date_request of trade"""
        try:
            tbody_periods = self.get_periods_table
            return format_time(tbody_periods.iloc[-1][1])
        except Exception as e:
            logger.error(f'{self.response.url} :: INVALID DATA END DATE REQUEST OFFER \n\n\n', e)
            return None

    @property
    def start_date_trading(self):
        return self.start_date_request

    @property
    def end_date_trading(self):
        return self.end_date_request

    @property
    def start_price_offer(self):
        """return start price of OFFER"""
        try:
            block_price = self.response.xpath(self.loc.start_price_offer_loc).get()
            block_price = BS(str(block_price), features='lxml').get_text()
            price = ''.join(re.sub(r"\s", "", block_price)).replace(',', '.')
            price = ''.join(re.sub(r"руб\.?$", "", price)).strip()
            return round(float(price), 2)
        except Exception as e:
            logger.error(f'{self.response.url} :: Invalid data start price OFFER\n\n\n\n', e)
            return None
