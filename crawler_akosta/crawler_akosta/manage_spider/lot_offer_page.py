from bs4 import BeautifulSoup as BS
import logging
import re
import unicodedata
import pandas as pd

from general_utils import dedent_func, format_time

logger = logging.getLogger(__name__)


class LotOfferPage:

    def __init__(self, _response):
        self.response = _response
        self.soup = BS(str(self.response.body.decode('utf-8')).replace('&lt;', '<').replace('&gt;', '>'),
                       features='lxml')

    def get_start_price(self):
        """ return start price offer NOT from periods"""
        try:
            start_price = self.soup.find('label', string=re.compile('Начальная стоимость', re.IGNORECASE)).parent
            start_price = start_price.get_text().strip().split(':', maxsplit=1)[-1].strip()
            start_price = dedent_func(unicodedata.normalize("NFKD", start_price)).replace(',', '.')
            start_price = re.sub(r'.$', '',
                                 ''.join([p for p in re.sub(r'\s', '', start_price) if p.isdigit() or p == '.'])).strip()
            return start_price
        except Exception as ex:
            logger.error(f'{self.response.url} :: INVALID DATA START PRICE OFFER \n {ex}')

    def return_period_pagination(self):
        """ return number of pages with periods """
        try:
            pag = self.soup.find('span', class_='ui-paginator-current').get_text()
            n1 = ''.join(re.findall(r'of.+', pag))
            n1 = ''.join([x for x in n1 if x.isdigit()])
            if re.match(r'\d+', n1):
                return int(n1)
        except Exception as e:
            logger.error(f'{self.response} :: ERROR RETURN NUMBER OF PAGES  {e}')

    def get_period_table(self):
        """ :return table pandas """
        try:
            thead = self.soup.find('thead', id='formMain:dataRSList_head').parent
            if thead:
                thead.thead.decompose()
                table = pd.read_html(re.sub(r',', '.', str(thead)), header=None)
                if table:
                    return table[0]
        except Exception as e:
            logger.error(f'{self.response.url} :: INVALID DATA PERIOD TABLE {e}')
            return None

    def get_start_date_request(self, lst_period: list):
        """ :return end date trading """
        try:
            last_element: dict = lst_period[0]
            return last_element['start_date_requests']
        except Exception as e:
            logger.error(f'{self.response.url} :: ERROR END DATE TRADING {e}')

    def get_end_date_request(self, lst_period: list):
        """ :return end date trading """
        try:
            last_element: dict = lst_period[-1]
            return last_element['end_date_requests']
        except Exception as e:
            logger.error(f'{self.response.url} :: ERROR END DATE TRADING {e}')

    def return_periods(self):
        """return list object with all periods of lot(offer)"""
        check_value = 10000000000000000000000
        periods = list()
        tbody_periods = self.get_period_table()
        for p in range(len(tbody_periods)):
            start = tbody_periods.iloc[p][0]
            end = tbody_periods.iloc[p][1]
            price_ = tbody_periods.iloc[p][2]
            price_ = re.sub(r'Руб.?', '', price_, re.IGNORECASE)
            try:
                if isinstance(price_, str):
                    price = ''.join(re.sub(r"\s", "", price_)).replace(',', '.')
                    price = round(float(price), 2)
                else:
                    price = round(float(price_), 2)
                if check_value < price:
                    logger.critical(
                        f'{self.response.url} :: INVALID PRICE ON PERIOD - CURRENT PRICE HIGHER THAN PREVIUOS')
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

    def return_next_periods(self):
        """ return period from page number 2 or higher then extend list with periods from first page """
        periods = list()
        soup = BS(str(self.response.text), 'html.parser')
        soup_new = BS(dedent_func(soup.get_text()), 'lxml')
        for tr in soup_new.find_all('tr'):
            td = tr.find_all('td')
            start = td[0].get_text()
            end = td[1].get_text()
            price_ = td[2].get_text()
            price_ = re.sub(r'Руб.?', '', price_, re.IGNORECASE)
            price = ''.join(re.sub(r"\s", "", price_)).replace(',', '.')
            price = round(float(price), 2)
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
                logger.error(f'{self.response.url} :: ERROR PERIOD NEXT PAGE')
        return periods



    def get_refresh_form_j_idt55(self):
        """ return time for stop request  or None if not exists """
        try:
            tag_html=self.soup.find('div', id='formMain:opRefreshStatus_content')
            if tag_html:
                _value = tag_html.find(attrs={"name": "formMain:j_idt55"})
                if _value:
                    _value = _value['value']
                return str(_value)
            else:
                return None
        except Exception as ex:
            logger.error(f'{self.response.url} :: ERROR FORM j_idt55, {ex}')