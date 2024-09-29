# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface

import os
import re
import json
import logging
from pathlib import Path
from random import choice

import requests
import pymysql.cursors
from datetime import datetime
from bs4 import BeautifulSoup
from icecream import ic

from crawler_eurtp.config import etp_folder, db_connect, base_dir, createTable_query, path_user_agent, path_to_socks5, \
    path_absolute, relative_path
from crawler_eurtp.python_mysql_dbconfig import read_db_config

DB_CONNECT = read_db_config()
with open(f'{path_user_agent}', 'r') as f:
    lines = f.readlines()
agent_list = [i.replace('\\n', '').strip() for i in lines]

with open(f'{path_to_socks5}', 'r') as f:
    lines = f.readlines()
socks_list = [i.replace('\\n', '').strip() for i in lines]


class CrawlerEurtpPipeline:
    included = []

    logger = logging.getLogger(__name__)

    def __init__(self, db, user, passwd, host):
        self.conn = pymysql.connect(db=db,
                                    user=user,
                                    passwd=passwd,
                                    host=host,
                                    charset='utf8mb4', use_unicode=True)
        self.cursor = self.conn.cursor()

    @classmethod
    def from_crawler(cls, crawler):
        db = DB_CONNECT['database']
        user = DB_CONNECT['user']
        passwd = DB_CONNECT['password']
        host = DB_CONNECT['host']
        return cls(db, user, passwd, host)

    def open_spider(self, spider):
        self.cursor.execute(createTable_query)
        self.conn.commit()

        query = 'SELECT %s FROM %s;' % (
            ', '.join(db_connect['unique_fields']),
            db_connect['table_name']
        )
        self.cursor.execute(query)
        self.conn.commit()

        mysql_included = self.cursor.fetchall()
        for entry in mysql_included:
            self.included.append('%s' % ('_'.join([str(val) for val in list(entry)])))

        self.file = open('items.json', 'w', encoding='utf-8')
        # self.file.write('[')

    def close_spider(self, spider):
        # self.file.write(']')
        self.file.close()

        self.cursor.close()

    def process_item(self, item, spider):
        item = self.cleaning(item)
        if datetime(2021, 1, 1) > datetime.strptime(item['start_date_requests'], "%Y-%m-%d %H:%M:%S"): return
        # self.checking(item)
        self.add_to_db(item)
        self.downloading_files(item)

        # line = json.dumps(dict(item), ensure_ascii=False) + ", "
        # self.file.write(line)
        return

    def cleaning(self, item):
        item['data_origin'] = self.cleaning_dataOrigin(item)

        item['trading_id'] = self.cleaning_tradingId(item)
        item['trading_link'] = self.cleaning_tradingLink(item)
        item['trading_number'] = self.cleaning_tradingNumber(item)

        item['trading_type'] = self.cleaning_tradingType(item)
        item['trading_form'] = self.cleaning_tradingForm(item)

        item['trading_org'] = self.cleaning_tradingOrg(item)
        item['trading_org_inn'] = None
        item['trading_org_contacts'] = self.cleaning_tradingOrgContacts(item)

        item['msg_number'] = None
        item['case_number'] = self.cleaning_caseNumber(item)
        item['debtor_inn'] = self.cleaning_debtorInn(item)

        item['arbit_manager'] = self.cleaning_arbitManager(item)
        item['arbit_manager_inn'] = self.cleaning_arbitManagerInn(item)
        item['arbit_manager_org'] = self.cleaning_arbitManagerOrg(item)

        item['status'] = None

        item['lot_id'] = self.cleaning_lotId(item)
        item['lot_link'] = self.cleaning_lotLink(item)
        item['lot_number'] = self.cleaning_lotNumber(item)

        item['short_name'] = self.cleaning_shortName(item)
        item['lot_info'] = self.cleaning_lotInfo(item)
        item['property_information'] = self.cleaning_propertyInformation(item)

        item['periods'] = self.cleaning_periods(item)

        item['start_date_requests'] = self.cleaning_startDateRequests(item)
        item['end_date_requests'] = self.cleaning_endDateRequests(item)
        item['start_date_trading'] = self.cleaning_startDateTrading(item)
        item['end_date_trading'] = self.cleaning_endDateTrading(item)

        item['start_price'] = self.cleaning_startPrice(item)
        item['step_price'] = self.cleaning_stepPrice(item)

        item['files'] = self.cleaning_files(item)

        return item

    def cleaning_dataOrigin(self, item):
        if 'data_origin' not in item.keys():
            self.logger.warning(
                'Площадка: eutrp.ru. ' +
                'Cсылка: %s. ' % item['trading_link'] +
                'Значение data_origin не получено при парсинге.',
                exc_info=1
            )

            return None

        return item['data_origin']

    def cleaning_tradingId(self, item):
        if 'trading_id' not in item.keys():
            self.logger.warning(
                'Площадка: eutrp.ru. ' +
                'Cсылка: %s. ' % item['trading_link'] +
                'Значение trading_id не получено при парсинге.',
                exc_info=1
            )

            return None

        trading_id = None

        if not str.isdigit(item['trading_id'].split('/')[-1]):
            self.logger.warning(
                'Площадка: eutrp.ru. ' +
                'Cсылка: %s. ' % item['trading_link'] +
                'Значение trading_id не число. ' +
                'Полученое значение: \'%s\'.' % item['trading_id'],
                exc_info=1
            )
        else:
            trading_id = item['trading_id'].split('/')[-1]

        return trading_id

    def cleaning_tradingLink(self, item):
        if 'trading_link' not in item.keys():
            self.logger.warning(
                'Площадка: eutrp.ru. ' +
                'Cсылка: %s. ' % item['trading_link'] +
                'Значение trading_link не получено при парсинге.',
                exc_info=1
            )

            return None

        return item['trading_link']

    def cleaning_tradingNumber(self, item):
        if 'trading_number' not in item.keys():
            self.logger.warning(
                'Площадка: eutrp.ru. ' +
                'Cсылка: %s. ' % item['trading_link'] +
                'Значение trading_number не получено при парсинге.',
                exc_info=1
            )

            return None

        trading_number = None

        if not str.isdigit(item['trading_number'].split('/')[-1]):
            self.logger.warning(
                'Площадка: eutrp.ru. ' +
                'Cсылка: %s. ' % item['trading_link'] +
                'Значение trading_number не число. ' +
                'Полученое значение: \'%s\'.' % item['trading_number'],
                exc_info=1
            )
        else:
            trading_number = item['trading_number'].split('/')[-1]

        return trading_number

    def cleaning_tradingType(self, item):
        if 'trading_type' not in item.keys():
            self.logger.warning(
                'Площадка: eutrp.ru. ' +
                'Cсылка: %s. ' % item['trading_link'] +
                'Значение trading_type не получено при парсинге.',
                exc_info=1
            )

            return None

        trading_type = None

        if item['trading_type'].strip() in [
            'Публичное предложение'
        ]:
            trading_type = 'offer'

        elif item['trading_type'].strip() in [
            'Открытый аукцион',
            'Закрытый аукцион',
            'Аукцион с закрытой формой представления цены'
        ]:
            trading_type = 'auction'

        elif item['trading_type'].strip() in [
            'Конкурс'
        ]:
            trading_type = 'competition'

        if trading_type is None: self.logger.warning(
            'Площадка: eutrp.ru. ' +
            'Cсылка: %s. ' % item['trading_link'] +
            'Значение trading_type не присвоено. ' +
            'Полученое значение: \'%s\'.' % item['trading_type'],
            exc_info=1
        )

        return trading_type

    def cleaning_tradingForm(self, item):
        if 'trading_form' not in item.keys():
            self.logger.warning(
                'Площадка: eutrp.ru. ' +
                'Cсылка: %s. ' % item['trading_link'] +
                'Значение trading_form не получено при парсинге.',
                exc_info=1
            )

            return None

        trading_form = None

        if item['trading_form'].strip() in [
            'Закрытый аукцион'
        ]:
            trading_form = 'closed'

        elif item['trading_form'].strip() in [
            'Публичное предложение',
            'Открытый аукцион',
            'Конкурс',
            'Аукцион с закрытой формой представления цены'
        ]:
            trading_form = 'open'

        if trading_form is None: self.logger.warning(
            'Площадка: eutrp.ru. ' +
            'Cсылка: %s. ' % item['trading_link'] +
            'Значение trading_form не присвоено. ' +
            'Полученое значение: \'%s\'.' % item['trading_form'],
            exc_info=1
        )

        return trading_form

    def cleaning_tradingOrg(self, item):
        if 'trading_org' not in item.keys():
            self.logger.warning(
                'Площадка: eutrp.ru. ' +
                'Cсылка: %s. ' % item['trading_link'] +
                'Значение trading_org не получено при парсинге.',
                exc_info=1
            )

            return None

        return item['trading_org']

    def cleaning_tradingOrgContacts(self, item):
        trading_org_contacts = {
            'email': '',
            'phone': ''
        }

        trading_org_contacts['email'] = self.validation_email(item)
        trading_org_contacts['phone'] = self.validation_phone(item)

        return trading_org_contacts

    def validation_email(self, item):
        email_str = item['trading_org_contacts'][1]
        if email_str is None: return ''

        if '@' not in email_str: return ''
        return email_str

    def validation_phone(self, item):
        phone_str = item['trading_org_contacts'][0]

        rule = re.compile(r'^((8|\+7)[\- ]?)?(\(?\d{3,4}\)?[\- ]?)?[\d\- ]{5,10}$')

        phone_str = phone_str.replace(" ", "").replace("(", '').replace(")", '').replace("–", "").replace('-',
                                                                                                          '').replace(
            "/", ",").replace(";", ",").replace("тел.", "").replace('.', '')
        for np in phone_str.split(","):
            if not rule.search(np):
                self.logger.warning(
                    'Площадка: eutrp.ru. ' +
                    'Cсылка: %s. ' % item['trading_link'] +
                    'Значение phone поля trading_org_contacts не прошло валидация.' +
                    'Полученое значение: \'%s\'.' % phone_str,
                    exc_info=1
                )

                return ''

        return phone_str

    def cleaning_caseNumber(self, item):
        if 'case_number' not in item.keys():
            self.logger.warning(
                'Площадка: eutrp.ru. ' +
                'Cсылка: %s. ' % item['trading_link'] +
                'Значение case_number не получено при парсинге.',
                exc_info=1
            )

            return None

        return item['case_number']

    def cleaning_debtorInn(self, item):
        debtor_inn = None
        if item['debtor_inn'][0] is not None: debtor_inn = item['debtor_inn'][0]
        if item['debtor_inn'][1] is not None: debtor_inn = item['debtor_inn'][1]
        if item['debtor_inn'][2] is not None: debtor_inn = item['debtor_inn'][2]

        if debtor_inn is None:
            self.logger.warning(
                'Площадка: eutrp.ru. ' +
                'Cсылка: %s. ' % item['trading_link'] +
                'Значение debtor_inn не получено при парсинге.',
                exc_info=1
            )

            return None

        if not str.isdigit(debtor_inn):
            self.logger.warning(
                'Площадка: eutrp.ru. ' +
                'Cсылка: %s. ' % item['trading_link'] +
                'Значение trading_id не число. ' +
                'Полученое значение: \'%s\'.' % item['debtor_inn'],
                exc_info=1
            )

            return None

        return debtor_inn

    def cleaning_arbitManager(self, item):
        if 'arbit_manager' not in item.keys():
            self.logger.warning(
                'Площадка: eutrp.ru. ' +
                'Cсылка: %s. ' % item['trading_link'] +
                'Значение arbit_manager не получено при парсинге.',
                exc_info=1
            )
            return None

        arbit_manager = item['arbit_manager']
        if len(list(set(item['arbit_manager']))) != 3: self.logger.warning(
            'Площадка: eutrp.ru. ' +
            'Cсылка: %s. ' % item['trading_link'] +
            'Значение arbit_manager возможно неверно. ' +
            'Полученое значение: \'%s\'.' % item['arbit_manager'],
            exc_info=1
        )

        result = []
        for part_name in arbit_manager:
            if part_name is None: continue
            result.append(part_name)

        arbit_manager = []
        for pn in result:
            for part_name in list(set(item['arbit_manager'])):
                if part_name == pn: arbit_manager.append(part_name)

        if len(result) == 0: return None

        return ' '.join(arbit_manager)

    def cleaning_arbitManagerInn(self, item):
        if 'arbit_manager_inn' not in item.keys():
            self.logger.warning(
                'Площадка: eutrp.ru. ' +
                'Cсылка: %s. ' % item['trading_link'] +
                'Значение arbit_manager_inn не получено при парсинге.',
                exc_info=1
            )
            return None

        arbit_manager_inn = None

        if not str.isdigit(item['arbit_manager_inn']):
            self.logger.warning(
                'Площадка: eutrp.ru. ' +
                'Cсылка: %s. ' % item['trading_link'] +
                'Значение arbit_manager_inn не число. ' +
                'Полученое значение: \'%s\'.' % item['arbit_manager_inn'],
                exc_info=1
            )
        else:
            arbit_manager_inn = item['arbit_manager_inn']

        return arbit_manager_inn

    def cleaning_arbitManagerOrg(self, item):
        if 'arbit_manager_org' not in item.keys():
            self.logger.warning(
                'Площадка: eutrp.ru. ' +
                'Cсылка: %s. ' % item['trading_link'] +
                'Значение arbit_manager_org не получено при парсинге.',
                exc_info=1
            )
            return None

        return item['arbit_manager_org']

    def cleaning_lotId(self, item):
        if 'lot_id' not in item.keys():
            self.logger.warning(
                'Площадка: eutrp.ru. ' +
                'Cсылка: %s. ' % item['lot_link'] +
                'Значение lot_id не получено при парсинге.',
                exc_info=1
            )

            return None

        lot_id = None

        if not str.isdigit(item['lot_id'].split('/')[-1]):
            self.logger.warning(
                'Площадка: eutrp.ru. ' +
                'Cсылка: %s. ' % item['trading_link'] +
                'Значение lot_id не число. ' +
                'Полученое значение: \'%s\'.' % item['lot_id'],
                exc_info=1
            )
        else:
            lot_id = item['lot_id'].split('/')[-1]

        return lot_id

    def cleaning_lotLink(self, item):
        if 'lot_link' not in item.keys():
            self.logger.warning(
                'Площадка: eutrp.ru. ' +
                'Cсылка: %s. ' % item['lot_link'] +
                'Значение lot_link не получено при парсинге.',
                exc_info=1
            )

            return None

        return item['lot_link']

    def cleaning_lotNumber(self, item):
        if 'lot_number' not in item.keys():
            self.logger.warning(
                'Площадка: eutrp.ru. ' +
                'Cсылка: %s. ' % item['lot_link'] +
                'Значение lot_number не получено при парсинге.',
                exc_info=1
            )

            return None

        lot_number = None

        if not str.isdigit(item['lot_number']):
            self.logger.warning(
                'Площадка: eutrp.ru. ' +
                'Cсылка: %s. ' % item['lot_link'] +
                'Значение lot_number не число. ' +
                'Полученое значение: \'%s\'.' % item['lot_number'],
                exc_info=1
            )
        else:
            lot_number = item['lot_number']

        return lot_number

    def cleaning_shortName(self, item):
        if 'short_name' not in item.keys():
            self.logger.warning(
                'Площадка: eutrp.ru. ' +
                'Cсылка: %s. ' % item['lot_link'] +
                'Значение short_name не получено при парсинге.',
                exc_info=1
            )

            return None

        return item['short_name']

    def cleaning_lotInfo(self, item):
        if 'lot_info' not in item.keys():
            self.logger.warning(
                'Площадка: eutrp.ru. ' +
                'Cсылка: %s. ' % item['lot_link'] +
                'Значение lot_info не получено при парсинге.',
                exc_info=1
            )

            return None

        return item['lot_info']

    def cleaning_propertyInformation(self, item):
        if 'property_information' not in item.keys():
            self.logger.warning(
                'Площадка: eutrp.ru. ' +
                'Cсылка: %s. ' % item['lot_link'] +
                'Значение property_information не получено при парсинге.',
                exc_info=1
            )

            return None

        return item['property_information']

    def cleaning_periods(self, item):
        if 'periods' not in item.keys(): return []

        periods = []
        for period_str in item['periods']:
            period_str = period_str.split(': ')
            period = {
                "start_date_requests": self.cleaning_date(period_str[0].split(' - ')[0]),
                "end_date_requests": self.cleaning_date(period_str[0].split(' - ')[1]),
                "end_date_trading": self.cleaning_date(period_str[0].split(' - ')[1]),
                "current_price": self.cleaning_price(period_str[-1])
            }

            periods.append(period)

        return periods

    def cleaning_date(self, date_str):
        return datetime.strptime(date_str, "%d.%m.%Y %H:%M:%S").strftime("%Y-%m-%d %H:%M:%S")

    def cleaning_price(self, price_str):
        if '%' in price_str: return None
        return float(price_str.replace(" ", "").replace("руб.", "").replace(',', '.'))

    def cleaning_startDateRequests(self, item):
        start_date_requests = None
        for arr_item in item['start_date_requests']:
            if arr_item is not None: start_date_requests = arr_item
        if start_date_requests is None and len(item['periods']) != 0: return item['periods'][0]['start_date_requests']

        if start_date_requests is None:
            self.logger.warning(
                'Площадка: eutrp.ru. ' +
                'Cсылка: %s. ' % item['trading_link'] +
                'Значение start_date_requests не получено при парсинге.',
                exc_info=1
            )
            return None

        try:
            return self.cleaning_date(start_date_requests)
        except:
            self.logger.warning(
                'Площадка: eutrp.ru. ' +
                'Cсылка: %s. ' % item['trading_link'] +
                'Неверный формат поля start_date_requests. ' +
                'Полученое значение: \'%s\'.' % item['start_date_requests'],
                exc_info=1
            )

            return None

    def cleaning_endDateRequests(self, item):
        end_date_requests = None
        for arr_item in item['end_date_requests']:
            if arr_item is not None: end_date_requests = arr_item
        if end_date_requests is None and len(item['periods']) != 0: return item['periods'][-1]['end_date_requests']

        if end_date_requests is None:
            self.logger.warning(
                'Площадка: promkonsalt. ' +
                'Cсылка: %s. ' % item['trading_link'] +
                'Значение end_date_requests не получено при парсинге.',
                exc_info=1
            )
            return None

        try:
            return self.cleaning_date(end_date_requests)
        except:
            self.logger.warning(
                'Площадка: promkonsalt. ' +
                'Cсылка: %s. ' % item['trading_link'] +
                'Неверный формат поля end_date_requests. ' +
                'Полученое значение: \'%s\'.' % item['end_date_requests'],
                exc_info=1
            )

            return None

    def cleaning_startDateTrading(self, item):
        start_date_trading = None
        for arr_item in item['start_date_trading']:
            if arr_item is not None: start_date_trading = arr_item
        if start_date_trading is None and len(item['periods']) != 0: return item['periods'][0]['start_date_requests']

        if start_date_trading is None:
            self.logger.warning(
                'Площадка: eutrp.ru. ' +
                'Cсылка: %s. ' % item['trading_link'] +
                'Значение start_date_trading не получено при парсинге.',
                exc_info=1
            )
            return None

        try:
            return self.cleaning_date(start_date_trading)
        except:
            self.logger.warning(
                'Площадка: eutrp.ru. ' +
                'Cсылка: %s. ' % item['trading_link'] +
                'Неверный формат поля start_date_trading. ' +
                'Полученое значение: \'%s\'.' % item['start_date_trading'],
                exc_info=1
            )

            return None

    def cleaning_endDateTrading(self, item):
        if item['trading_type'] == 'auction': return None
        if len(item['periods']) != 0: return item['periods'][-1]['end_date_requests']

        self.logger.warning(
            'Площадка: eutrp.ru. ' +
            'Cсылка: %s. ' % item['trading_link'] +
            'Значение end_date_trading не присвоено.',
            exc_info=1
        )

        return None

    def cleaning_startPrice(self, item):
        if 'start_price' not in item.keys():
            self.logger.warning(
                'Площадка: eutrp.ru. ' +
                'Cсылка: %s. ' % item['trading_link'] +
                'Значение start_price не получено при парсинге.',
                exc_info=1
            )

            return None

        return self.cleaning_price(item['start_price'])

    def cleaning_stepPrice(self, item):
        if item['trading_type'] == 'offer': return None

        if item['step_price'][0] is None and item['step_price'][1] is None and item['step_price'][2] is None:
            self.logger.warning(
                'Площадка: eutrp.ru. ' +
                'Cсылка: %s. ' % item['lot_link'] +
                'Значение step_price не получено при парсинге.',
                exc_info=1
            )

            return None

        if item['step_price'][1] is None and item['step_price'][2] is None:
            self.logger.warning(
                'Площадка: eutrp.ru. ' +
                'Cсылка: %s. ' % item['lot_link'] +
                'Значение шага step_price не получено при парсинге.',
                exc_info=1
            )

            return None

        if item['step_price'][0] == 'Проценты' and item['step_price'][1] is not None:
            return round(item['start_price'] * 0.01 * int(item['step_price'][1]), 2)
        elif item['step_price'][0] == 'Проценты' and item['step_price'][2] is not None:
            return round(item['start_price'] * 0.01 * int(item['step_price'][2]), 2)

        if item['step_price'][0] == 'Рубли' and item['step_price'][1] is not None:
            return self.cleaning_price(item['step_price'][1])
        elif item['step_price'][0] == 'Рубли' and item['step_price'][2] is not None:
            return self.cleaning_price(item['step_price'][2])

        else:
            self.logger.warning(
                'Площадка: eutrp.ru. ' +
                'Cсылка: %s. ' % item['lot_link'] +
                'Значение едениц шага step_price не обработано. ' +
                'Полученое значение: \'%s\'.' % item['step_price'][0],
                exc_info=1
            )

        return None

    def cleaning_files(self, item):
        files = {
            'general': [],
            'lot': []
        }

        files['general'] = self.cleaning_filesData(str(item['files'][0]), item)
        files['lot'] = self.cleaning_filesData(str(item['files'][1]), item)

        return files

    def cleaning_filesData(self, table_str, item):
        parser = BeautifulSoup(table_str, 'html.parser')

        files = []

        for row in parser.select('tr')[1:]:
            link = ''
            if row.select('td')[2].get_text().strip().split('.')[-1] in ['jpeg', 'jpg', 'png', 'JPG']:
                link = f'{relative_path}/%d/%02d/%s_%s' % (datetime.today().year, datetime.today().month,
                                                      '_'.join([item[field] for field in db_connect['unique_fields']]),
                                                      row.select('td')[2].get_text().strip())
                link = link.replace(' ', '_')

            _file = {
                'original_name': row.select('td')[2].get_text().strip(),
                'link': link,
                'link_etp': 'https://eurtp.ru' + row.select_one('a')['href']
            }

            files.append(_file)

        return files

    def return_year_now(self):
        year = str(datetime.now().year).strip()
        return year

    def return_month_now(self):
        month = str('{:0>2}'.format(datetime.now().month)).strip()
        return month

    def create_dir(self):
        return Path(f'{path_absolute}/{self.return_year_now()}/{self.return_month_now()}').mkdir(parents=True,
                                                                                                 exist_ok=True)

    def return_absolute_path(self):
        return f'{path_absolute}/{self.return_year_now()}/{self.return_month_now()}/'

    def downloading_files(self, item):
        locate_dir = ''

        if len(item['files']['general']) != 0:
            for _file in item['files']['general']:
                if _file['link'] == '': continue
                self.create_dir()
                self.download_file(locate_dir, _file)

        if len(item['files']['lot']) != 0:
            for _file in item['files']['lot']:
                if _file['link'] == '': continue
                self.create_dir()
                self.download_file(locate_dir, _file)

    def download_file(self, base_path, _file):
        if len(socks_list) > 0 and socks_list[0] != '':
            proxies = {
                'http': 'socks5://' + choice(socks_list),
                'https': 'socks5://' + choice(socks_list)

            }
        else:
            proxies = {
                "http": '',
                "https": '',
            }
        r = requests.get(_file['link_etp'], proxies=proxies)

        f = open(base_path + '/' + _file['link'], 'wb')
        f.write(r.content)
        f.close()

    def add_to_db(self, item):
        unique_value = '_'.join([item[field] for field in db_connect['unique_fields']])

        if unique_value in self.included:
            query = ('UPDATE %s SET ' % db_connect['table_name'] + \
                     'created_at = %s, '
                     'arbit_manager = %s, '
                     'arbit_manager_inn = %s, '
                     'arbit_manager_org = %s, '
                     'case_number = %s, '
                     'data_origin = %s, '
                     'debtor_inn = %s, '
                     'end_date_requests = %s, '
                     'end_date_trading = %s, '
                     'files = %s, '
                     'lot_id = %s, '
                     'lot_info = %s, '
                     'lot_link = %s, '
                     'lot_number = %s, '
                     'msg_number = %s, '
                     'periods = %s, '
                     'property_information = %s, '
                     'short_name = %s, '
                     'start_date_requests = %s, '
                     'start_date_trading = %s, '
                     'start_price = %s, '
                     'status = %s, '
                     'step_price = %s, '
                     'trading_form = %s, '
                     'trading_id = %s, '
                     'trading_link = %s, '
                     'trading_number = %s, '
                     'trading_org = %s, '
                     'trading_org_contacts = %s, '
                     'trading_org_inn = %s, '
                     'trading_type = %s' + \
                     'WHERE %s' % ' and '.join(
                        ['%s=\'%s\'' % (field, item[field]) for field in db_connect['unique_fields']]))

        else:
            query = ('INSERT INTO %s (' % db_connect['table_name'] + \
                     'created_at, '
                     'arbit_manager, '
                     'arbit_manager_inn, '
                     'arbit_manager_org, '
                     'case_number, '
                     'data_origin, '
                     'debtor_inn, '
                     'end_date_requests, '
                     'end_date_trading, '
                     'files, '
                     'lot_id, '
                     'lot_info, '
                     'lot_link, '
                     'lot_number, '
                     'msg_number, '
                     'periods, '
                     'property_information, '
                     'short_name, '
                     'start_date_requests, '
                     'start_date_trading, '
                     'start_price, '
                     'status, '
                     'step_price, '
                     'trading_form, '
                     'trading_id, '
                     'trading_link, '
                     'trading_number, '
                     'trading_org, '
                     'trading_org_contacts, '
                     'trading_org_inn, '
                     'trading_type)'
                     'VALUES ( %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)')

            self.included.append('_'.join([item[field] for field in db_connect['unique_fields']]))

        periods = None
        if item['periods'] is not None:
            periods = json.dumps(item['periods'], ensure_ascii=False)

        self.cursor.execute(query, (
            datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            item['arbit_manager'],
            item['arbit_manager_inn'],
            item['arbit_manager_org'],
            item['case_number'],
            item['data_origin'],
            item['debtor_inn'],
            item['end_date_requests'],
            item['end_date_trading'],
            json.dumps(item['files'], ensure_ascii=False),
            item['lot_id'],
            item['lot_info'],
            item['lot_link'],
            item['lot_number'],
            item['msg_number'],
            periods,
            item['property_information'],
            item['short_name'],
            item['start_date_requests'],
            item['start_date_trading'],
            item['start_price'],
            item['status'],
            item['step_price'],
            item['trading_form'],
            item['trading_id'],
            item['trading_link'],
            item['trading_number'],
            item['trading_org'],
            json.dumps(item['trading_org_contacts'], ensure_ascii=False),
            item['trading_org_inn'],
            item['trading_type'],
        ))
        self.conn.commit()

        return item

    def checking(self, item):
        report = 'Площадка: ru-trade24. Ссылка: %s. Номер лота: %s.\n' % (item['trading_link'], item['lot_number'])

        is_print = False

        for field in [
            'arbit_manager',
            'arbit_manager_inn',
            'arbit_manager_org',
            'case_number',
            'data_origin',
            'debtor_inn',
            'end_date_requests',
            'end_date_trading',
            'files',
            'lot_id',
            'lot_info',
            'lot_link',
            'lot_number',
            # 'msg_number',
            'periods',
            'property_information',
            'short_name',
            'start_date_requests',
            'start_date_trading',
            'start_price',
            # 'status',
            'step_price',
            'trading_form',
            'trading_id',
            'trading_link',
            'trading_number',
            'trading_org',
            'trading_org_contacts',
            # 'trading_org_inn',
            'trading_type'
        ]:

            if field == 'start_date_trading' and item['end_date_trading'] is not None: continue
            if field == 'end_date_trading' and item['start_date_trading'] is not None: continue
            if field == 'step_price' and item['trading_type'] != 'auction': continue
            if item[field] is None:
                is_print = True
                report += '\t%s = NULL\n' % field

        if is_print: self.logger.warning(report)
