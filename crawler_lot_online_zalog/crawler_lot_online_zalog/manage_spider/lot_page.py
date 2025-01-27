from bs4 import BeautifulSoup as BS
import re
import pandas as pd
from ..utils.config import pattern_start_end_request, pattern_start_end_trading, pattern_start_end_trading2
from ..utils.post_data.common_data import data_address
from ..utils.working_with_text_cookies_num import dedent_func, return_normalize_text, delete_extra_symbols, \
    cut_lot_number, get_lot_number
import logging
from ..utils.check_inn_email_phone import CheckIfCorrectContactInfo
from ..utils.working_with_time import format_time, format_time_auction

logger = logging.getLogger(__name__)


class LotPage:

    def __init__(self, response_):
        self.response = response_
        self.soup = BS(str(self.response.body.decode('utf-8')).replace('&lt;', '<').replace('&gt;', '>'),
                       features='lxml')
        self.right_text_bar = self.soup.find('div', class_='tender')
        self.check = CheckIfCorrectContactInfo()

    def trading_type_text(self):
        """ return full text of trading type """
        try:
            tender = self.right_text_bar
            text = tender.br.previous_sibling
            text = dedent_func(text.strip().replace('\\xa0', ' '))
            return re.sub(r'\s+', ' ', text)
        except Exception as e:
            logger.error(f'{self.response.url} :: ERROR trading type full text\n{e}')

    def sort_trading_type(self):
        text = self.trading_type_text()
        offer = ['Продажа посредством публичного предложения']
        auction = ['Аукцион с открытой формой подачи предложений']
        if offer[0] in text:
            return 'offer'
        elif auction[0] in text:
            return 'auction'

    @property
    def trade_id(self):
        """using regular expression return trading id"""
        url_lot = self.response.url
        match = re.findall(r'\d{8,}', url_lot)
        if match:
            return ''.join(match)
        else:
            logger.error(f'{self.response.url} :: ERROR GETTING TRADE ID')
            return None

    def trading_number(self):
        """using regular expression fetch trading number from text inside right side bar of the page"""
        text = self.right_text_bar.get_text()
        pattern = r'Номер процедуры:\s.*?(\d+)\s?'
        pattern2 = r'Номер торгов:\s.*?(\d+)\s?'
        match = re.findall(pattern, str(text))
        if len(match) > 0:
            if 4 <= len(''.join(match)) < 20:
                return ''.join(match)
        elif match2 := re.findall(pattern2, str(text)):
            if len(match2) > 0:
                if 4 <= len(''.join(match)) < 20:
                    return ''.join(match)
        else:
            logger.error(f'{self.response.url} :: INVALID DATA TRADING NUMBER')
            return None

    def get_organizer_block(self):
        """ return block of code with organizer info """
        if org_block := self.soup.find('legend', string=re.compile('Организатор', re.IGNORECASE)):
            org_block = org_block.parent
            return org_block
        else:
            logger.error(f'{self.response.url} :: ERROR ORGANIZER BLOCK')
            return None

    def get_org_name(self):
        """ retun organizer name (naimenovanie) """
        if block := self.get_organizer_block():
            naimenovanie = block.find('label', string=re.compile('Наименование',
                                                                 re.IGNORECASE)).next_sibling.strip().replace(
                '\\xa0', ' ')
            return naimenovanie
        else:
            return block

    def get_org_email(self):
        """ return organizer email """
        if block := self.get_organizer_block():
            if email := block.find('label', string=re.compile('Электронная почта', re.IGNORECASE)):
                return self.check.check_email(email.next_sibling.strip().replace('\\xa0', ' '))
        else:
            return ''

    def get_org_phone(self):
        """ :return organizer phone """
        if block := self.get_organizer_block():
            if phone := block.find('label', string=re.compile('Телефон.?', re.IGNORECASE)):
                return self.check.check_phone(phone.next_sibling.strip().replace('\\xa0', ' '))
        else:
            return ''

    def get_full_org_contacts(self):
        """ join organizer email and phone in dictionary """
        return {'email': dedent_func(self.get_org_email()), 'phone': dedent_func(self.get_org_phone())}

    @delete_extra_symbols
    @cut_lot_number
    def short_name(self):
        """:return short name(field) of lot"""
        short_name_loc = '//h1'
        extra_check_short_name_loc = '.field-lot'
        h1 = self.response.xpath(short_name_loc).get()
        em = self.response.css(extra_check_short_name_loc).getall()
        try:
            soup = BS(str(h1), features='lxml')
            if len(em) == 2:
                match = re.split(',', soup.get_text(), maxsplit=2)
                match = list(map(lambda x: dedent_func(x), match))[-1]
                return ''.join(match)
            elif len(em) == 1:
                match = re.split(',', soup.get_text(), maxsplit=1)
                match = list(map(lambda x: dedent_func(x), match))[-1]
                return ''.join(match)
            else:
                return None
        except Exception as e:
            logger.error(f'{self.response.url} :{e}: ERROR SHORT NAME')
            return None

    @delete_extra_symbols
    @cut_lot_number
    def lot_info(self):
        """:return short name(field) of lot"""
        lot_info_loc = '//p[@class="field-description"][2]'
        p = self.response.xpath(lot_info_loc).get()
        try:
            if p:
                lot_info = dedent_func(BS(str(p), features='lxml').get_text())
                return lot_info
            else:
                return None
        except Exception as e:
            logger.error(f'{self.response.url} :{e}: ERROR LOT INFO')

    def property_info(self):
        """:return short name(field) of lot"""
        property_info_loc = '//div[@id="excurse-info"]'
        p = self.response.xpath(property_info_loc).get()
        try:
            if p:
                property_info = dedent_func(BS(str(p), features='lxml').get_text())
                return property_info
            else:
                return None
        except Exception as e:
            logger.error(f'{self.response.url} :{e}: ERROR PROPERTY INFO')

    def start_n_end_date_req_auc(self):
        """:return list with two dates of request using re pattern, info fetch from right side bar """
        try:
            text = dedent_func(self.right_text_bar.get_text().strip())

            match = ''.join(re.findall(pattern_start_end_request, text))
            if 31 < len(match) < 35:
                match = re.split(r'\s', match)
                return match
            else:

                logger.error(f'{self.response.url} :: INCORECT LEN OF START AND END DATE REQUEST TEXT')
                return None
        except Exception as e:
            logger.error(f'{self.response.url} :{e}: INCORECT DATA OF START AND END DATE REQUEST TEXT')
            return None

    def start_date_request_auc(self):
        """return start date requests. Get list with two date return first """
        try:
            start = self.start_n_end_date_req_auc()
            return format_time_auction(start[0] + ' ' + ' ' + start[1])
        except:
            logger.error(f'{self.response.url} :: INVALID DATA OF START  DATE REQUEST ')
            return None

    def end_date_request_auc(self):
        """return start date requests. Get list with two date return first """
        try:
            end = self.start_n_end_date_req_auc()
            return format_time_auction(end[-2] + ' ' + ' ' + end[-1])
        except:
            logger.error(f'{self.response.url} :: INVALID DATA OF END  DATE REQUEST ')
            return None

    def start_price(self):
        """return start price of OFFER"""
        try:
            start_price_offer_loc = '//div//p[@class="field-price"]//span[@class="price"]'
            block_price = self.response.xpath(start_price_offer_loc).get()
            block_price = BS(str(block_price), features='lxml').get_text()
            price = ''.join(re.sub(r"\s", "", block_price)).replace(',', '.')
            price = ''.join(re.sub(r"руб\.?$", "", price)).strip()
            return round(float(price), 2)
        except Exception as e:
            logger.error(f'{self.response.url} :: Invalid data start price OFFER\n\n\n\n', e)
            return None

    def step_price(self):
        """:return step price of auction"""
        try:
            text = dedent_func(self.right_text_bar.get_text().strip())
            if 'Шаг на понижение' in text:
                pattern_step = r'Шаг на повышение.*\d+.?\d+,?\d{1,2}?.*р?у?б?.*Шаг'
                match_price = re.findall(pattern_step, text)
            else:
                pattern_step = r'Шаг на повышение.*\d+.?\d+,?\d{1,2}?.*р?у?б?.*Сумма'
                pattern1 = r'Шаг на повышение.*\d.*Сумма'
                pattern2 = r'Шаг аукциона.*\d+.?\d+,?\d{1,2}?.*р?у?б?.*Сумма'
                pattern3 = r'Шаг аукциона.*\d.*Сумма'
                pattern4 = r'Шаг.*\d.*Сумма'
                match_price = re.findall(pattern_step, text)
                if len(match_price) == 0:
                    match_price = re.findall(pattern4, text)
                if len(match_price) == 0:
                    match_price = re.findall(pattern1, text)
                if len(match_price) == 0:
                    match_price = re.findall(pattern2, text)
                if len(match_price) == 0:
                    match_price = re.findall(pattern3, text)
            if match_price:
                match_price = ''.join(filter(lambda x: x.isdigit() or x == ',' or x == '.', match_price[0]))
                match_price = re.sub(r'\D$', '', match_price).strip()
                return round(float(match_price.replace(',', '.')), 2)
        except Exception as e:
            logger.warning(f'{self.response.url} :: INVALID DATA STEP PRICE {e}')

    def get_deposit(self):
        """:return step price of auction"""
        try:
            text = dedent_func(self.right_text_bar.get_text().strip())
            pattern_step = r'Сумма задатка.{,30}р?у?б?\.'
            match_price = re.findall(pattern_step, text, re.IGNORECASE)
            match_price = ''.join(filter(lambda x: x.isdigit() or x == ',' or x == '.', match_price[0]))
            match_price = re.sub(r'\D$', '', match_price).strip()
            return round(float(match_price.replace(',', '.')), 2)
        except Exception as e:
            return None

    @get_lot_number
    def lot_number(self):
        """:return text if exist with lot number, after decorator fetch lot number or asign 1"""
        lot_number_css_loc = '.field-lot:nth-child(2)'
        lot_number = self.response.css(lot_number_css_loc).get()
        if lot_number:
            return dedent_func(BS(str(lot_number), features='lxml').get_text())
        else:
            return ''


    def start_n_end_date_trading_auc(self):
        """:return list with two dates of request using re pattern, info fetch from right side bar """
        try:
            text = dedent_func(self.right_text_bar.get_text().strip())

            match = ''.join(re.findall(pattern_start_end_trading, text))
            if 31 < len(match) < 35:
                match = re.split(r'\s', match)
                return match
            elif len(match) < 30:
                match = ''.join(re.findall(pattern_start_end_trading2, text))
                if 31 < len(match) < 35:
                    match = re.split(r'\s', match)
                    return match
                else:
                    logger.error(f'{self.response.url} :: INCORECT LEN OF START AND END DATE TRADING TEXT')
                    return None
        except Exception as e:
            logger.error(f'{self.response.url} :{e}: INCORECT DATA OF START AND END DATE TRADING TEXT')
            return None

    def start_date_trading_auc(self):
        """return start date requests. Get list with two date return first """
        try:
            start = self.start_n_end_date_trading_auc()
            return format_time_auction(start[0] + ' ' + ' ' + start[1])
        except:
            logger.error(f'{self.response.url} :: INVALID DATA OF START  DATE TRADING ')
            return None

    def end_date_trading_auc(self):
        """return start date requests. Get list with two date return first """
        try:
            end = self.start_n_end_date_trading_auc()
            return format_time_auction(end[-2] + ' ' + ' ' + end[-1])
        except:
            logger.error(f'{self.response.url} :: INVALID DATA OF END  DATE TRADING ')
            return None

    # OFFER PERIOD TABLE
    @property
    def get_periods_table(self):
        """return all periods (tbody)"""
        try:
            tbody_periods_loc = '//table[contains(., "Величина изменения")]'
            table = self.response.xpath(tbody_periods_loc).get()
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
                    logger.critical(
                        f'{self.response.url} :: INVALID PRICE ON PERIOD - CURRENT PRICE HIGHER THAN PREVIUOS')
                else:
                    check_value = price
            except:
                logger.error(f'{self.response.url} Period Price - {price_} typeof - {type(price_)}')
                return None
            try:
                period = {
                    'start_date_requests': format_time_auction(start),
                    'end_date_requests': format_time_auction(end),
                    'end_date_trading': format_time_auction(end),
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
            return format_time_auction(tbody_periods.iloc[0][0])
        except Exception as e:
            logger.error(f'{self.response.url} :: INVALID DATA START DATE REQUEST OFFER \n\n\n', e)
            return None

    @property
    def end_date_request(self):
        """:return end_date_request of trade"""
        try:
            tbody_periods = self.get_periods_table
            return format_time_auction(tbody_periods.iloc[-1][1])
        except Exception as e:
            logger.error(f'{self.response.url} :: INVALID DATA END DATE REQUEST OFFER \n\n\n', e)
            return None

    @property
    def start_date_trading(self):
        return self.start_date_request

    @property
    def end_date_trading(self):
        return self.end_date_request

    def retrun_category(self, category, subcat):
        """ :arg subcat -> english presentation """
        if category == 'movable_property':
            if subcat == 'equipment':
                return {'classification': 'Оборудование'}
            elif subcat == 'others':
                return {'classification': 'Прочее имущество'}
            elif subcat == 'cars':
                return {'classification': 'Транспорт/спецтехника'}
        elif category == 'not_movable_property':
            if subcat == 'homes':
                return {'classification': 'Жилая недвижимость'}
            elif subcat == 'ground':
                return {'classification': 'Земельные участки для размещения/застройки'}
            elif subcat == 'others':
                return {'classification': 'Иное'}
            elif subcat == 'commercial':
                return {'classification': 'Коммерческая недвижимость'}
        elif category == 'financial_assets':
            if subcat == 'agreements':
                return {'classification': 'Договоры, соглашения, права пользования'}
            elif subcat == 'material':
                return {'classification': 'Нематериальные активы'}
            elif subcat == 'securities':
                return {'classification': 'Ценные бумаги'}
            elif subcat == 'cesia':
                return {'classification': 'Цессии'}




