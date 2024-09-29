import logging
import re

from bs4 import BeautifulSoup as BS

from .finished_section import MAIN_URL
from ..utils.work_with_text_and_number import dedent_func, make_float, random_float_value
from ..utils.working_with_time import format_time
from ..utils.working_with_url import UrlConfig

logger = logging.getLogger(__name__)


class LotPage:

    def __init__(self, response_):
        self.response = response_
        self.url = UrlConfig()
        self.soup = BS(
            str(self.response.body.decode('utf-8')).replace('&lt;', '<').replace('&gt;', '>').replace('&amp;', '&'),
            features='lxml')

    @staticmethod
    def get_data_origin():
        """ return 1-st point - data origin """
        return MAIN_URL

    def get_trading_id(self):
        """ return 2-nd point - trading id"""
        return self.url.retrun_value_of_param(self.response.url, 'notificationId')

    def get_trading_link(self):
        """ return 3-d point - trading link"""
        return self.response.url

    def get_trading_number(self):
        """ return 4-th point trading number """
        string = self.get_string_with_lot_number()
        if string:
            trading_number = ''.join(re.findall(r'\d{4,}/\d+/\d+', string))
            return trading_number

    def get_trading_type(self):
        """ return 5-th (a) point trading type """
        string = self.get_string_with_lot_number()
        auction = 'auction'
        offer = 'offer'
        compet = 'competition'
        if string:
            trading_type = re.findall(r'\s\(.*\)', string)[0]
            trading_type = ''.join(trading_type).replace('(', '').replace(')', '').strip()
            if trading_type:
                trading_type = re.sub(r'\s+', ' ', trading_type).strip().lower()
                if 'ткрытый аукцион' in trading_type or 'укцион' in trading_type:
                    return auction
                elif 'убличное предложение' in trading_type:
                    return offer
                elif 'продажа посредством публичного предложения' in trading_type or 'продажа посредством публичного' in trading_type:
                    return offer
                elif 'родажа обращенного в собственность государства имущества стоимостью более 100 тыс' in trading_type:
                    return offer
                elif 'родажа обращенного в собственность государства имущества стоимостью не более 100 тыс' in trading_type:
                    return offer
                elif 'ткрытый конкурс' in trading_type or 'онкурс' in trading_type:
                    return compet
                elif 'родажа без объявления цены' in trading_type:
                    return compet
                else:
                    logger.error(f'{self.response.url} :: INVALID DATA TRADING TYPE')

    @property
    def get_trading_form(self):
        """ return 5-th (b) trading form """
        return "open"

    def get_category(self):
        """ return category (d2) """
        try:
            td_category = self.soup.find('td', string=re.compile('Тип имущества', re.IGNORECASE))
            if td_category:
                text_cat = td_category.findNext('td').parent.find_all('td')[1].get_text()
                if ',' in text_cat:
                    lst_category = re.split(r',', text_cat)
                    return {'classification': lst_category}
                else:
                    return {'classification': [text_cat]}
        except Exception as ex:
            logger.error(f'{self.response.url} :{ex}: ERROR CATEGORY', exc_info=True)

    def get_index(self):
        """ return index (d1) """

    def get_address(self):
        """ return address (d3)"""
        try:
            td_address = self.soup.find('td', string=re.compile('Место нахождения имущества', re.IGNORECASE))
            td_address_2 = self.soup.find('td', string=re.compile('Место нахождения:', re.IGNORECASE))
            if td_address:
                return dedent_func(td_address.findNext('td').parent.find_all('td')[1].get_text().strip())
            elif td_address_2:
                return dedent_func(td_address_2.findNext('td').parent.find_all('td')[1].get_text().strip())
        except Exception as ex:
            logger.error(f'{self.response.url} :{ex}: ERROR ADDRESS', exc_info=True)

    def get_detailed_address(self):
        """ return detailed_address (d4)"""
        try:
            td_address = self.soup.find('td', string=re.compile('Детальное местоположение', re.IGNORECASE))
            td_address1 = self.soup.find('td', string=re.compile('Детальное местонахождение', re.IGNORECASE))
            if td_address:
                return dedent_func(td_address.findNext('td').parent.find_all('td')[1].get_text().strip())
            elif td_address1:
                return dedent_func(td_address1.findNext('td').parent.find_all('td')[1].get_text().strip())
        except Exception as ex:
            logger.error(f'{self.response.url} :{ex}: ERROR DETAILED ADDRESS', exc_info=True)

    def get_encumbrance(self):
        """ return encumbrance (d5)"""
        try:
            td_encumbrance = self.soup.find('label', string=re.compile('Обременение', re.IGNORECASE))
            td_encumbrance_2 = self.soup.find('label', string=re.compile('Наличие обременения', re.IGNORECASE))
            if td_encumbrance:
                return dedent_func(td_encumbrance.findNext('td').parent.find_all('td')[1].get_text().strip())
            elif td_encumbrance_2:
                return dedent_func(td_encumbrance_2.findNext('td').parent.find_all('td')[1].get_text().strip())
        except Exception as ex:
            logger.error(f'{self.response.url} :{ex}: ERROR ENCUMBRANCE', exc_info=True)

    def get_description_encumbrance(self):
        """ return description_encumbrance (d6)"""
        try:
            description_encumbrance = self.soup.find('label', string=re.compile('Описание обременения', re.IGNORECASE))
            description_encumbrance_2 = self.soup.find('label',
                                                       string=re.compile('Сведения об обременении', re.IGNORECASE))
            if description_encumbrance:
                return dedent_func(description_encumbrance.findNext('td').parent.find_all('td')[1].get_text().strip())
            elif description_encumbrance_2:
                return dedent_func(description_encumbrance_2.findNext('td').parent.find_all('td')[1].get_text().strip())
        except Exception as ex:
            logger.error(f'{self.response.url} :{ex}: ERROR description_encumbrance', exc_info=True)

    def get_lot_number(self):
        """ return lot number """
        string = self.get_string_with_lot_number()
        lot_number = re.findall(r'Лот.+\d+', string, re.IGNORECASE)
        lot_number = ''.join(re.findall(r'\d+$', ''.join(lot_number)))
        if lot_number.isdigit():
            return lot_number
        else:
            logger.error(f'{self.response.url} :: INVALID DATA LOT NUMBER')

    def get_short_name(self):
        """ return short name  """
        try:
            td_short_name = self.soup.find('label',
                                           string=re.compile('Наименование и характеристик.? имуществ.?',
                                                             re.IGNORECASE))
            td_short_name_2 = self.soup.find('label',
                                             string=re.compile('Сведения о заложенном имуществе:?', re.IGNORECASE))
            td_short_name_3 = self.soup.find('label', string=re.compile('Сведения об имуществе:', re.IGNORECASE))
            td_short_name_4 = self.soup.find('label', string=re.compile('Наименование и характеристики имущества:',
                                                                        re.IGNORECASE))
            td_short_name_5 = self.soup.find('label',
                                             string=re.compile('Наименование,? количество и характеристика имущества:',
                                                               re.IGNORECASE))
            if td_short_name:
                return td_short_name.findNext('td').parent.find_all('td')[1].get_text().strip()
            elif td_short_name_2:
                return td_short_name_2.findNext('td').parent.find_all('td')[1].get_text().strip()
            elif td_short_name_3:
                return td_short_name_3.findNext('td').parent.find_all('td')[1].get_text().strip()
            elif td_short_name_4:
                return td_short_name_4.findNext('td').parent.find_all('td')[1].get_text().strip()
            elif td_short_name_5:
                return td_short_name_5.findNext('td').parent.find_all('td')[1].get_text().strip()
        except Exception as ex:
            logger.error(f'{self.response.url} :{ex}:: ERROR SHORT NAME')

    def get_lot_info(self):
        """ return lot info """

    def property_information(self, lot_link):
        """ return property info """
        try:
            td_property_info = self.soup.find('label',
                                              string=re.compile('Порядок ознакомления покупателей с условиями договора',
                                                                re.IGNORECASE))

            td_property_info2 = self.soup.find('label',
                                               string=re.compile('Сроки, время ознакомления покупателя с имуществом:',
                                                                 re.IGNORECASE))
            if td_property_info:
                return td_property_info.findNext('td').parent.find_all('td')[1].get_text().strip()
            elif td_property_info2:
                return td_property_info2.findNext('td').parent.find_all('td')[1].get_text().strip()
        except Exception as e:
            logger.error(f'{lot_link} :: ERROR PROPERTY INFO {e}')

    def get_start_date_requests(self):
        """ return start date request """

    def get_end_date_requests(self):
        """ return end date request """

    def get_start_date_trading(self):
        """ retun start date trading """

    def get_end_date_trading(self):
        """ return end date trading """

    def get_quantity(self):
        """ retutn quantity (d8) """

    def get_unit(self):
        """ return unit (d9) """

    def get_deposit(self):
        """ retun deposit (d7) """
        try:
            deposit = self.soup.find('label', string=re.compile('Размер задатка', re.IGNORECASE))
            if deposit:
                td_deposit = deposit.findNext('td')
                if len(td_deposit) > 0:
                    text_ = dedent_func(td_deposit.get_text().strip())
                    if re.match(r'\d+', str(text_)):
                        return make_float(text_)
        except Exception as ex:
            logger.error(f'{self.response.url} :{ex}:: ERROR DEPOSIT')

    def get_min_price(self, lot_link):
        """ return min_price (d10) """
        try:
            min_price = self.soup.find('label', string=re.compile('Минимальная цена', re.IGNORECASE))
            if min_price:
                td_price = min_price.findNext('td')
                return make_float(dedent_func(td_price.get_text()))
        except Exception as e:
            logger.error(f'{lot_link} :: ERROR min price\n{e}')

    def get_start_price(self, trading_type):
        """ return start price """
        try:
            start_price = self.soup.find('label', string=re.compile('Начальная цена', re.IGNORECASE))
            start_price_2 = self.soup.find('label',
                                           string=re.compile('Начальная продажная цена имущества', re.IGNORECASE))
            if start_price:
                td_price = start_price.findNext('td')
                return make_float(dedent_func(td_price.get_text()))
            elif start_price_2:
                td_price = start_price_2.findNext('td')
                return make_float(dedent_func(td_price.get_text()))
            elif trading_type == 'competition':
                return 0
            else:
                return None
        except Exception as ex:
            logger.error(f'{self.response.url} :{ex}:: ERROR START PRICE')

    def get_step_price(self, lot_link):
        """ return step price """
        try:
            step_price1 = self.soup.find('label', string=re.compile('Шаг аукциона', re.IGNORECASE))
            if step_price1:
                td_price = step_price1.findNext('td')
                return make_float(dedent_func(td_price.get_text()))
            elif step_price2 := self.soup.find('label',
                                               string=re.compile('Величина снижения начальной цены', re.IGNORECASE)):
                td_price1 = step_price2.findNext('td')
                return make_float(dedent_func(td_price1.get_text()))
        except Exception as e:
            logger.error(f'{lot_link} :: ERROR step price\n{e}')

    def get_periods(self):
        """ return periods """

    def get_files(self):
        """ return files """

    def created_at_time(self):
        """ return created time of lot """

    # EXTRA METHODS
    def get_string_with_lot_number(self):
        """ get tag <a> where text contains lot number, trading number, trading type and form """
        try:
            pattern_string = ''.join(re.findall(r'/restricted.+\d+$', str(self.response.url))).replace('?', '.')
            string_div = self.soup.find('a', href=re.compile(pattern_string))
            if string_div:
                string_div = string_div.parent
                string = string_div.find_all('a')[-1].get_text()
                return string
        except Exception as ex:
            logger.error(f'{self.response.url} :: ERROR GETTING STRING WITH TRADING NUMBER {ex}')

    def get_a_trading_page(self):
        """get link to trading page ( tag a of tab) """
        general_page = self.soup.find_all('a', string=re.compile(r'\s?^Общие\s?$', re.IGNORECASE))
        if len(general_page) > 0:
            return general_page
        else:
            logger.error(f'{self.response.url} :: ERROR TAB TO GENERAL PAGE NOT FOUND')
            return None

    def get_id_trading_page(self):
        """ fetch id of traing page tab """
        if general_page := self.get_a_trading_page():
            if isinstance(general_page, list):
                if len(general_page) > 1:
                    general_page = general_page[0].split()
                for x in general_page:
                    if x := x.get('id'):
                        return x
                    else:
                        logger.error(f'{self.response.url} :: ERROR GETTING ID TAB TRADING PAGE')
                        return None

    def get_link_to_trading_page(self):
        """ after get tag <a> fetch using regular exp link to trading page """
        if general_page := self.get_a_trading_page():
            if isinstance(general_page, list):
                if len(general_page) > 1:
                    general_page = general_page[0].split()
                for x in general_page:
                    string = (x['onclick'])
                    search_str = re.findall(r'\?wicket:interface=:\d+.+link::IBehaviorListener:\d+:.?\d+', string)
                    return MAIN_URL + ''.join(search_str) + '&random=' + random_float_value()

    def start_date_request_extra(self, url_lot):
        """ return start date request  """
        try:
            start = self.soup.find('label', string=re.compile('Дата и время публикации извещения:', re.IGNORECASE))
            if start:
                start = start.findNext('td').get_text().strip()
            if len(start) > 7:
                return format_time(start)
        except Exception as e:
            logger.error(f'{url_lot} :{e}: ERROR START DATE REQUEST lot_section')
            with open(f'start_date_request_bankrot_extra.txt', 'w') as f:
                f.write(self.soup.text)
            return None
