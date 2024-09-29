# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html
import os
import re
from pathlib import Path
from random import choice

import icu
import json
import logging
import requests
import pymysql.cursors
from datetime import datetime
from bs4 import BeautifulSoup
from icecream import ic

from crawler_ruTrade24.config import etp_folder, createTable_query, db_connect, base_dir, path_user_agent, \
    path_to_socks5, relative_path, path_absolute
from crawler_ruTrade24.python_mysql_dbconfig import read_db_config

DB_CONNECT = read_db_config()

with open(f'{path_user_agent}', 'r') as f:
    lines = f.readlines()
agent_list = [i.replace('\\n', '').strip() for i in lines]

with open(f'{path_to_socks5}', 'r') as f:
    lines = f.readlines()
socks_list = [i.replace('\\n', '').strip() for i in lines]


class CrawlerRutarde24Pipeline:
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
            self.included.append(
                '%s' % ('_'.join([str(val) for val in list(entry)])))
        print('Yep')

        self.file = open('items.json', 'w', encoding='utf-8')
        self.file.write('[')

    def close_spider(self, spider):
        self.file.write(']')
        self.file.close()

        self.cursor.close()

    def process_item(self, item, spider):
        items = item
        for i in range(len(items['lot_number'])):
            item = self.cloning(i, items)

            item = self.cleaning(item)
            # self.checking(item)

            self.downloading_files(item)

            self.add_to_db(item)

            line = json.dumps(dict(item), ensure_ascii=False) + ", "
            self.file.write(line)
        return

    def cloning(self, index, items):
        item = {}
        for field in items.keys():
            item[field] = items[field]

        item['lot_number'] = item['lot_number'][index]
        item['short_name'] = item['short_name'][index]
        item['periods'] = item['periods'][index]
        item['files'] = [item['files'][0], item['files'][1][index]]

        if 'start_price' in item.keys():
            item['start_price'] = item['start_price'][index]
        if 'step_price' in item.keys():
            item['step_price'] = item['step_price'][index]

        return item

    def cleaning(self, item):
        item['trading_id'] = self.cleaning_tradingId(item)
        item['trading_number'] = self.cleaning_tradingNumber(item)
        item['trading_type'] = self.cleaning_tradingType(item)
        item['trading_form'] = self.cleaning_tradingForm(item)
        item['trading_org'] = self.cleaning_tradingOrg(item)
        item['trading_org_inn'] = self.cleaning_tradingOrgInn(item)
        item['trading_org_contacts'] = self.cleaning_tradingOrgContacts(item)

        item['msg_number'] = self.cleaning_msgNumber(item)
        item['case_number'] = self.cleaning_caseNumber(item)
        item['debtor_inn'] = self.cleaning_debtorInn(item)

        item['arbit_manager'] = self.cleaning_arbitManager(item)
        item['arbit_manager_inn'] = self.cleaning_arbitManagerInn(item)

        item['status'] = self.cleaning_status(item)

        item['lot_id'] = None
        item['lot_link'] = None
        item['lot_number'] = self.cleaning_lotNumber(item)

        item['lot_info'] = None
        item['property_information'] = None

        item['periods'] = self.cleaning_periods(item)

        item['start_date_requests'] = self.cleaning_startDateRequests(item)
        item['end_date_requests'] = self.cleaning_endDateRequests(item)
        item['start_date_trading'] = self.cleaning_startDateTrading(item)
        item['end_date_trading'] = self.cleaning_endDateTrading(item)

        item['start_price'] = self.cleaning_startPrice(item)
        item['step_price'] = self.cleaning_stepPrice(item)

        item['files'] = self.cleaning_files(item)

        return item

    def cleaning_tradingId(self, item):
        trading_id = None

        if not str.isdigit(item['trading_id'].split('/')[-1]):
            self.logger.warning(
                'Площадка: ru-trade24.ru. ' +
                'Cсылка: %s. ' % ''.join(item['trading_link']) +
                'Значение trading_id не число. ' +
                'Полученое значение: \'%s\'.' % ''.join(
                    item['trading_id']).split('/')[-1],

            )
        else:
            trading_id = item['trading_id'].split('/')[-1]

        return trading_id

    def cleaning_tradingNumber(self, item):
        if 'trading_number' not in item.keys():
            self.logger.warning(
                'Площадка: ru-trade24.ru. ' +
                'Cсылка: %s. ' % ''.join(item['trading_link']) +
                'Значение trading_number не получено при парсинге.',
                exc_info=True
            )
            return None

        trading_number = None

        if not str.isdigit(item['trading_number'].split()[-1]):
            self.logger.warning(
                'Площадка: ru-trade24.ru. ' +
                'Cсылка: %s. ' % ''.join(item['trading_link']) +
                'Значение trading_number не число. ' +
                'Полученое значение: \'%s\'.' % item['trading_number'],
                exc_info=True
            )
        else:
            trading_number = item['trading_number'].split()[-1]

        return trading_number

    def cleaning_tradingType(self, item):
        if 'trading_type' not in item.keys():
            self.logger.warning(
                'Площадка: ru-trade24.ru. ' +
                'Cсылка: %s. ' % ''.join(item['trading_link']) +
                'Значение trading_type не получено при парсинге.',
                exc_info=True
            )
            return None

        trading_type = None

        if item['trading_type'] in [
            'Публичное предложение'
        ]:

            trading_type = 'offer'

        elif item['trading_type'] in [
            'Открытый аукцион',
            'Торги на повышение'
        ]:

            trading_type = 'auction'

        if trading_type is None:
            self.logger.warning(
                'Площадка: ru-trade24.ru. ' +
                'Cсылка: %s. ' % ''.join(item['trading_link']) +
                'Значение trading_type не присвоено. ' +
                'Полученое значение: \'%s\'.' % item['trading_type'],
                exc_info=True
            )

        return trading_type

    def cleaning_tradingForm(self, item):
        if 'trading_form' not in item.keys():
            self.logger.warning(
                'Площадка: ru-trade24.ru. ' +
                'Cсылка: %s. ' % item['trading_link'] +
                'Значение trading_form не получено при парсинге.',
                exc_info=True
            )

        trading_form = None

        if item['trading_form'] in [
            'Открытый аукцион',
            'Торги на повышение',
            'Конкурс',
            'Публичное предложение'
        ]:
            trading_form = 'open'

        if trading_form is None:
            self.logger.warning(
                'Площадка: ru-trade24.ru. ' +
                'Cсылка: %s. ' % item['trading_link'] +
                'Значение trading_form не присвоено. ' +
                'Полученое значение: \'%s\'.' % item['trading_form'],
                exc_info=True
            )

        return trading_form

    def cleaning_tradingOrg(self, item):
        if 'trading_org' not in item.keys():
            self.logger.warning(
                'Площадка: ru-trade24.ru. ' +
                'Cсылка: %s. ' % item['trading_link'] +
                'Значение trading_org не получено при парсинге.',
                exc_info=True
            )

        trading_org = None

        result = []
        for field in item['trading_org']:
            if field == '':
                continue
            result.append(field)

        # ?

        trading_org = ' '.join(result)

        return trading_org

    def cleaning_tradingOrgInn(self, item):
        if 'trading_org_inn' not in item.keys():
            self.logger.warning(
                'Площадка: ru-trade24.ru. ' +
                'Cсылка: %s. ' % item['trading_link'] +
                'Значение trading_org_inn не получено при парсинге.',
                exc_info=True
            )

        trading_org_inn = None

        if not str.isdigit(item['trading_org_inn']):
            self.logger.warning(
                'Площадка: ru-trade24.ru. ' +
                'Cсылка: %s. ' % item['trading_link'] +
                'Значение trading_org_inn не число. ' +
                'Полученое значение: \'%s\'.' % item['trading_org_inn'],
                exc_info=True
            )
        else:
            trading_org_inn = item['trading_org_inn']

        return trading_org_inn

    def cleaning_tradingOrgContacts(self, item):
        trading_org_contacts = {'email': self.validation_email(
            item), 'phone': self.validation_phone(item)}

        return trading_org_contacts

    def validation_email(self, item):
        email_str = item['trading_org_contacts'][1]

        if '@' in email_str:
            return email_str

        self.logger.warning(
            'Площадка: ru-trade24.ru. ' +
            'Cсылка: %s. ' % item['trading_link'] +
            'Значение email поля trading_org_contacts не прошло валидация.' +
            'Полученое значение: \'%s\'.' % email_str,
            exc_info=True
        )
        return ''

    def validation_phone(self, item):
        phone_str = item['trading_org_contacts'][0]

        rule = re.compile(
            r'^((8|\+7)[\- ]?)?(\(?\d{3,4}\)?[\- ]?)?[\d\- ]{5,10}$')

        phone_str = phone_str.replace(" ", "").replace("(", '').replace(")", '').replace("–", "").replace('-',
                                                                                                          '').replace(
            "/", ",").replace(";", ",").replace("тел.", "")
        for np in phone_str.split(","):
            if not rule.search(np):
                self.logger.warning(
                    'Площадка: ru-trade24.ru. ' +
                    'Cсылка: %s. ' % item['trading_link'] +
                    'Значение phone поля trading_org_contacts не прошло валидация.' +
                    'Полученое значение: \'%s\'.' % phone_str,
                    exc_info=True
                )

                return ''

        return phone_str

    def cleaning_msgNumber(self, item):
        if 'msg_number' not in item.keys():
            self.logger.warning(
                'Площадка: ru-trade24.ru. ' +
                'Cсылка: %s. ' % item['trading_link'] +
                'Значение msg_number не получено при парсинге.',
                stacklevel=2
            )
            return None

        msg_number = None

        if str.isdigit(item['msg_number']):
            msg_number = item['msg_number']
        elif str.isdigit(item['msg_number'].split('; ')[0]) and len(item['msg_number'].split('; ')[0]) == 7:
            msg_number = item['msg_number'].split('; ')[0]
        elif str.isdigit(item['msg_number'].split()[0]) and len(item['msg_number'].split()[0]) == 7:
            msg_number = item['msg_number'].split()[0]
        elif len(item['msg_number'].split()) >= 2 and str.isdigit(item['msg_number'].split()[1]) and len(
                item['msg_number'].split()[1]) == 7:
            msg_number = item['msg_number'].split()[1]

        else:
            self.logger.warning(
                'Площадка: ru-trade24.ru. ' +
                'Cсылка: %s. ' % item['trading_link'] +
                'Значение msg_number не число. ' +
                'Полученое значение: \'%s\'.' % item['msg_number'].split('; ')[
                    0],
                stacklevel=2
            )

        return msg_number

    def cleaning_caseNumber(self, item):
        if 'case_number' not in item.keys():
            self.logger.warning(
                'Площадка: ru-trade24.ru. ' +
                'Cсылка: %s. ' % item['trading_link'] +
                'Значение case_number не получено при парсинге.',
                stacklevel=2
            )
            return None

        case_number = None

        if '№' in item['case_number']:
            case_number = item['case_number'][2:]
        else:
            case_number = item['case_number']

        return case_number

    def cleaning_debtorInn(self, item):
        if 'debtor_inn' not in item.keys():
            self.logger.warning(
                'Площадка: ru-trade24.ru. ' +
                'Cсылка: %s. ' % item['trading_link'] +
                'Значение debtor_inn не получено при парсинге.',
                exc_info=True
            )
            return None

        debtor_inn = None

        if not str.isdigit(item['debtor_inn']):
            self.logger.warning(
                'Площадка: ru-trade24.ru. ' +
                'Cсылка: %s. ' % item['trading_link'] +
                'Значение debtor_inn не число. ' +
                'Полученое значение: \'%s\'.' % item['debtor_inn'],
                exc_info=True
            )
        else:
            debtor_inn = item['debtor_inn']

        return debtor_inn

    def cleaning_arbitManager(self, item):
        if 'arbit_manager' not in item.keys():
            self.logger.warning(
                'Площадка: ru-trade24.ru. ' +
                'Cсылка: %s. ' % item['trading_link'] +
                'Значение arbit_manager не получено при парсинге.',
                exc_info=True
            )

        arbit_manager = None

        # ?

        arbit_manger = ' '.join(item['arbit_manager'])

        return arbit_manger

    def cleaning_arbitManagerInn(self, item):
        if 'arbit_manager_inn' not in item.keys():
            self.logger.warning(
                'Площадка: ru-trade24.ru. ' +
                'Cсылка: %s. ' % item['trading_link'] +
                'Значение arbit_manager_inn не получено при парсинге.',
                exc_info=True
            )
            return None

        arbit_manager_inn = None

        if not str.isdigit(item['arbit_manager_inn']):
            self.logger.warning(
                'Площадка: ru-trade24.ru. ' +
                'Cсылка: %s. ' % item['trading_link'] +
                'Значение arbit_manager_inn не число. ' +
                'Полученое значение: \'%s\'.' % item['arbit_manager_inn'],
                exc_info=True
            )
        else:
            arbit_manager_inn = item['arbit_manager_inn']

        return arbit_manager_inn

    def cleaning_status(self, item):
        if 'status' not in item.keys():
            self.logger.warning(
                'Площадка: ru-trade24.ru. ' +
                'Cсылка: %s. ' % item['trading_link'] +
                'Значение status не получено при парсинге.',
                exc_info=True
            )
            return None

        status = None

        if item['status'] in [
            'Идет прием заявок'
        ]:

            status = 'active'

        elif item['status'] in [
            'Торги объявлены'
        ]:

            status = 'pending'

        elif item['status'] in [
            'Торги отменены',
            'Торги завершены',
            'Идет подведение итогов',
            'Торги проводятся',
            'Прием заявок окончен',
            'Торги приостановлены'
        ]:

            status = 'ended'

        if status is None:
            self.logger.warning(
                'Площадка: ru-trade24.ru. ' +
                'Cсылка: %s. ' % item['trading_link'] +
                'Значение status не присвоено. ' +
                'Полученое значение: \'%s\'.' % item['status'],
                exc_info=True
            )

        return status

    def cleaning_lotNumber(self, item):
        if 'lot_number' not in item.keys():
            self.logger.warning(
                'Площадка: tenderstandart. ' +
                'Cсылка: %s. ' % item['lot_link'] +
                'Значение lot_number не получено при парсинге.',
                exc_info=True
            )

        lot_number = None

        if not str.isdigit(item['lot_number'].split()[-1]):
            self.logger.warning(
                'Площадка: ru-trade24.ru. ' +
                'Cсылка: %s. ' % item['trading_link'] +
                'Значение lot_number не присвоено. ' +
                'Полученое значение: \'%s\'.' % item['lot_number'],
                exc_info=True
            )
        else:
            lot_number = item['lot_number'].split()[-1]

        return lot_number

    def cleaning_startDateRequests(self, item):
        try:
            return self.cleaning_date(item['start_date_requests'])
        except:
            self.logger.warning(
                'Площадка: ru-trade24.ru. ' +
                'Cсылка: %s. ' % item['trading_link'] +
                'Неверный формат поля start_date_requests. ' +
                'Полученое значение: \'%s\'.' % item['start_date_requests'],
                exc_info=True
            )

    def cleaning_endDateRequests(self, item):
        try:
            return self.cleaning_date(item['end_date_requests'])
        except:
            self.logger.warning(
                'Площадка: ru-trade24.ru. ' +
                'Cсылка: %s. ' % item['trading_link'] +
                'Неверный формат поля end_date_requests. ' +
                'Полученое значение: \'%s\'.' % item['end_date_requests'],
                exc_info=True
            )

    def cleaning_startDateTrading(self, item):
        if 'start_date_trading' in item.keys():
            try:
                return self.cleaning_date(item['start_date_trading'])
            except:
                self.logger.warning(
                    'Площадка: ru-trade24.ru. ' +
                    'Cсылка: %s. ' % item['trading_link'] +
                    'Неверный формат поля start_date_trading. ' +
                    'Полученое значение: \'%s\'.' % item['start_date_trading'],
                    exc_info=True
                )
        if 'periods' in item.keys() and len(item['periods']) != 0:
            return item['periods'][0]['start_date_requests']

        return None

    def cleaning_endDateTrading(self, item):
        if 'end_date_trading' in item.keys():
            try:
                templ = ''.join(item['end_date_trading'])
                if 'не позднее' in templ:
                    templ = ''.join(re.findall(r'\d{1,2}.\d{1,2}.\d{2,4}', templ))

                clean_ = ''.join([x for x in templ if
                                  x.isdigit() or x == '.' or x == ':' or x == ' ' or x == '/' or x == '\\' or x == '|'])
                clean_ = re.sub(r'\D{5}.+', '', clean_)
                return self.cleaning_date(clean_)
            except:
                self.logger.warning(
                    'Площадка: ru-trade24.ru. ' +
                    'Cсылка: %s. ' % item['trading_link'] +
                    'Неверный формат поля end_date_trading. ' +
                    'Полученое значение: \'%s\'.' % item['end_date_trading'],
                    exc_info=True
                )
        if item['periods'] is not None:
            try:
                return item['periods'][-1]['end_date_requests']
            except:
                return list()

        return None

    def cleaning_date(self, date_str):
        for templ in [
            '%d.%m.%Y %H:%M',
            '%d.%m.%Y в %H:%M',
            '%d.%m.%Y %H %M',
            '%d.%m.%Y',
            '%d.%m.%Y до %H:%M',
            '%d/%m/%Y',
            '%d.%m.%Y %H-%M',
            '%d.%m.%Y по времени завершения торгов на сайте электронной площадки',
            '%d.%m.%Y %H.%M',
            '%d.%m.%Y %H/%M',
            '%d.%m.%Y %H\%M',
            '%d.%m.%Y г. в %H:%M ч.',
            '%d.%m.%Y %H|%M',
            '%d.%m.%Yг. в %H:%M',
            '%d.%m.%Y по окончании проведения торгов',
            '%d.%m.%Y%H:%M',
            '%d.%m.%Y %H:%M (при условии, что к участию в торгах не допущен ни один заявитель или допущен только один '
            'участник), при участии в торгах двух и более лиц, дата и время подведения результатов торгов '
            'определяется в соответствии с регламентом электронной площадки.',
            '%d.%m.%Y в %H.%M',
            # '%d %B %Y %H:%M',
            '%d.%m.%Y, в %H час. %M мин.'
        ]:
            try:
                return datetime.strptime(date_str, templ).strftime("%Y-%m-%d %H:%M:%S")
            except:
                continue


        f = icu.SimpleDateFormat('dd MMMM yyyy kk:mm', icu.Locale('ru'))
        dt = datetime.fromtimestamp(int(f.parse(date_str)))
        return dt.strftime("%Y-%m-%d %H:%M:%S")

    def cleaning_altDate(self, date_str):
        return datetime.strptime(date_str, "%d.%m.%Y %H:%M:%S").strftime("%Y-%m-%d %H:%M:%S")

    def cleaning_startPrice(self, item):
        if 'periods' in item.keys() and len(item['periods']) != 0:
            return item['periods'][0]['current_price']
        if 'start_price' in item.keys():
            return self.cleaning_price(item['start_price'])

    def cleaning_stepPrice(self, item):
        if 'step_price' not in item.keys():
            return None
        return self.cleaning_price(item['step_price'])

    def cleaning_price(self, price_str):
        return float(price_str.replace(",", ".").replace(" ", "").replace("руб.", "").replace(u'\xa0', u''))

    def cleaning_periods(self, item):
        if 'periods' not in item.keys():
            return []

        parser = BeautifulSoup(item['periods'], 'html.parser')

        periods = []
        for table in parser.select('.price-periods'):
            periods.append({
                "start_date_requests": self.cleaning_altDate(
                    table.select('td')[0].get_text().strip().split(' по ')[0][2:]),
                "end_date_requests": self.cleaning_altDate(
                    table.select('td')[0].get_text().strip().split(' по ')[1].split(' - ')[0]),
                "end_date_trading": self.cleaning_altDate(
                    table.select('td')[0].get_text().strip().split(' по ')[1].split(' - ')[0]),
                "current_price": self.cleaning_price(
                    table.select('td')[0].get_text().strip().split(' по ')[1].split(' - ')[1])
            })

        # if len(periods) == 0: return None
        else:
            return periods

    def cleaning_files(self, item):
        files = {
            'general': [],
            'lot': []
        }

        if 'files' in item.keys():
            files['general'] = self.cleaning_filesOnPage(
                item['files'][0], item)
            files['lot'] = self.cleaning_filesOnPage(item['files'][1], item)

        return files

    def cleaning_filesOnPage(self, str_html, item):
        if str_html == '':
            return ''

        parser = BeautifulSoup(str_html, 'html.parser')

        files = []
        for child in parser.findChildren():
            if child.name == 'h4':
                break
            if child.name == 'div':
                continue

            a = child
            link = ''
            if a['class'][-1].split('--')[-1] in ['jpeg', 'jpg', 'png', 'JPG']:
                link = f'{relative_path}/%d/%02d/%s_%s' % (datetime.today().year, datetime.today().month,
                                                           '_'.join(
                                                               [item[field] for field in db_connect['unique_fields']]),
                                                           a.get_text().strip() + '.' + a['class'][-1].split('--')[-1])
                link = link.replace(' ', '_')

            files.append({
                'original_name': a.get_text().strip(),
                'link': link,
                'link_etp': 'http://www.ru-trade24.ru' + a['href']
            })

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

    def checking(self, item):
        report = 'Площадка: ru-trade24. Ссылка: %s. Номер лота: %s.\n' % (
            item['trading_link'], item['lot_number'])

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
            # 'lot_id',
            # 'lot_info',
            # 'lot_link',
            'lot_number',
            'msg_number',
            'periods',
            # 'property_information',
            'short_name',
            'start_date_requests',
            'start_date_trading',
            'start_price',
            'status',
            'step_price',
            'trading_form',
            'trading_id',
            'trading_link',
            'trading_number',
            'trading_org',
            'trading_org_contacts',
            'trading_org_inn',
            'trading_type'
        ]:

            if field == 'start_date_trading' and item['end_date_trading'] is not None:
                continue
            if field == 'end_date_trading' and item['start_date_trading'] is not None:
                continue
            if field == 'step_price' and item['trading_type'] != 'auction':
                continue
            if item[field] is None:
                is_print = True
                report += '\t%s = NULL\n' % field

        if is_print:
            self.logger.warning(report)

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
        unique_value = '_'.join([item[field]
                                 for field in db_connect['unique_fields']])

        if unique_value in self.included:
            query = ('UPDATE %s SET ' % db_connect['table_name'] + 'created_at = %s, '
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
                                                                   'trading_type = %s' + 'WHERE %s' % ' and '.join(
                ['%s=\'%s\'' % (field, item[field]) for field in db_connect['unique_fields']]))

        else:
            query = ('INSERT INTO %s (' % db_connect['table_name'] +
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
                     'VALUES ( %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, '
                     '%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)')

            self.included.append(
                '_'.join([item[field] for field in db_connect['unique_fields']]))

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
