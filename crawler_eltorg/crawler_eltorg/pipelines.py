# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html

import os
import re
import json
from pathlib import Path
from random import choice

import pymysql
import logging
import requests
from datetime import datetime
from bs4 import BeautifulSoup
from icecream import ic

from crawler_eltorg.python_mysql_dbconfig import read_db_config
from crawler_eltorg.config import db_connect, createTable_query, base_dir, etp_folder, path_user_agent, path_to_socks5, \
    path_absolute, relative_path

DB_CONNECT = read_db_config()
with open(f'{path_user_agent}', 'r') as f:
    lines = f.readlines()
agent_list = [i.replace('\\n', '').strip() for i in lines]

with open(f'{path_to_socks5}', 'r') as f:
    lines = f.readlines()
socks_list = [i.replace('\\n', '').strip() for i in lines]


class CrawlerEltorgPipeline:
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

        self.file = open('items.json', 'w')
        # self.file.write('[')

    def close_spider(self, spider):
        # self.file.write(']')
        self.file.close()

    def process_item(self, item, spider):
        item = self.cleaning(item)
        self.downloading_files(item)
        # self.checking(item)

        self.add_to_db(item)

        # line = json.dumps(dict(item), ensure_ascii=False) + ",\n"
        # self.file.write(line)
        return

    def cleaning(self, item):
        item['trading_id'] = self.cleaning_tradingId(item)
        item['trading_link'] = self.cleaning_tradingLink(item)
        item['trading_number'] = self.cleaning_tradingNumber(item)
        item['trading_type'] = self.cleaning_tradingType(item)
        item['trading_form'] = self.cleaning_tradingForm(item)
        item['trading_org_contacts'] = self.cleaning_tradingOrgContacts(item)
        item['trading_org_inn'] = None

        item['msg_number'] = self.cleaning_msgNumber(item)
        item['debtor_inn'] = self.cleaning_debtorInn(item)

        item['arbit_manager'] = self.cleaning_arbitManager(item)
        item['arbit_manager_inn'] = self.cleaning_arbitManagerInn(item)
        item['arbit_manager_org'] = self.cleaning_arbitManagerOrg(item)

        item['status'] = self.cleaning_status(item)

        item['lot_id'] = self.cleaning_lotId(item)
        item['lot_number'] = self.cleaning_lotNumber(item)
        item['lot_info'] = self.cleaning_lotInfo(item)

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

        if not str.isdigit(item['trading_id'].split("=")[-1]):
            self.logger.warning(
                'Площадка: el-torg. ' +
                'Cсылка: %s. ' % item['trading_link'] +
                'Значение trading_id не число. ' +
                'Полученое значение: \'%s\'.' % item['trading_id'].split("=")[-1],
                exc_info=1
            )
        else:
            trading_id = item['trading_id'].split("=")[-1]

        return trading_id

    def cleaning_tradingLink(self, item):
        return item['trading_link']

    def cleaning_tradingNumber(self, item):
        if 'trading_number' not in item.keys():
            self.logger.warning(
                'Площадка: el-torg. ' +
                'Cсылка: %s. ' % item['trading_link'] +
                'Значение trading_number не получено при парсинге.',
                exc_info=1
            )
            return None

        trading_number = None

        if not str.isdigit(item['trading_number'].split(" ")[-1]):
            self.logger.warning(
                'Площадка: el-torg. ' +
                'Cсылка: %s. ' % item['trading_link'] +
                'Значение trading_number не число. ' +
                'Полученое значение: \'%s\'.' % item['trading_number'].split(" ")[-1],
                exc_info=1
            )
        else:
            trading_number = item['trading_number'].split(" ")[-1]

        return trading_number

    def cleaning_tradingType(self, item):
        if 'trading_type' not in item.keys():
            self.logger.warning(
                'Площадка: el-torg. ' +
                'Cсылка: %s. ' % item['trading_link'] +
                'Значение trading_type не получено при парсинге.',
                exc_info=1
            )
            return None

        trading_type = None

        if item['trading_type'] in [
            'Публичное предложение',
            'Закрытое публичное предложение'
        ]:
            trading_type = "offer"

        elif item['trading_type'] in [
            'Аукцион с открытой формой представления цены',
            'Аукцион с закрытой формой представления цены',
            'Закрытый аукцион с открытой формой представления цены',
            'Закрытый аукцион с закрытой формой представления цены'
        ]:
            trading_type = "auction"

        elif item['trading_type'] in [
            'Конкурс с открытой формой представления цены',
            'Конкурс с закрытой формой представления цены',
            'Закрытый конкурс с открытой формой представления цены',
            'Закрытый конкурс с закрытой формой представления цены'
        ]:
            trading_type = "competition"

        if trading_type is None: self.logger.warning(
            'Площадка: el-torg. ' +
            'Cсылка: %s. ' % item['trading_link'] +
            'Значение trading_type не присвоено. ' +
            'Полученое значение: \'%s\'.' % item['trading_type'],
            exc_info=True
        )

        return trading_type

    def cleaning_tradingForm(self, item):
        if 'trading_form' not in item.keys():
            self.logger.warning(
                'Площадка: el-torg. ' +
                'Cсылка: %s. ' % item['trading_link'] +
                'Значение trading_form не получено при парсинге.',
                exc_info=True
            )
            return None

        trading_form = None

        if item['trading_form'] in [
            'Аукцион с открытой формой представления цены',
            'Аукцион с закрытой формой представления цены',
            'Конкурс с открытой формой представления цены',
            'Конкурс с закрытой формой представления цены',
            'Публичное предложение'
        ]:
            trading_form = "open"

        elif item['trading_form'] in [
            'Закрытый аукцион с открытой формой представления цены',
            'Закрытый аукцион с закрытой формой представления цены',
            'Закрытый конкурс с открытой формой представления цены',
            'Закрытый конкурс с закрытой формой представления цены',
            'Закрытое публичное предложение'
        ]:
            trading_form = "closed"

        if trading_form is None: self.logger.warning(
            'Площадка: el-torg. ' +
            'Cсылка: %s. ' % item['trading_link'] +
            'Значение trading_form не присвоено. ' +
            'Полученое значение: \'%s\'.' % item['trading_form'],
            exc_info=True
        )

        return trading_form

    def cleaning_tradingOrgContacts(self, item):
        trading_org_contacts = {
            'phone': '',
            'email': ''
        }

        trading_org_contacts['phone'] = self.validation_phone(item)
        trading_org_contacts['email'] = self.validation_email(item)

        return trading_org_contacts

    def validation_phone(self, item):
        phone_str = item['trading_org_contacts'][0]
        if phone_str is None: return ''

        rule = re.compile(r'^((8|\+7)[\- ]?)?(\(?\d{3,4}\)?[\- ]?)?[\d\- ]{5,10}$')

        phone_str = phone_str.replace(" ", "").replace("(", '').replace(")", '').replace("–", "").replace('-',
                                                                                                          '').replace(
            "/", ",").replace(";", ",").replace("тел.", "")
        for np in phone_str.split(","):
            if not rule.search(np):
                self.logger.warning(
                    'Площадка: el-torg. ' +
                    'Cсылка: %s. ' % item['trading_link'] +
                    'Значение phone поля trading_org_contacts не прошло валидация.' +
                    'Полученое значение: \'%s\'.' % phone_str,
                    exc_info=True
                )

                return ''

        return phone_str

    def validation_email(self, item):
        email_str = item['trading_org_contacts'][1]
        if email_str is None: return ''

        if "@" in email_str: return email_str

        self.logger.warning(
            'Площадка: el-torg. ' +
            'Cсылка: %s. ' % item['trading_link'] +
            'Значение email поля trading_org_contacts не прошло валидация.' +
            'Полученое значение: \'%s\'.' % email_str,
            exc_info=True
        )
        return ''

    def cleaning_msgNumber(self, item):
        if 'msg_number' not in item.keys():
            self.logger.warning(
                'Площадка: el-torg. ' +
                'Cсылка: %s. ' % item['trading_link'] +
                'Значение msg_number не получено при парсинге.',
                exc_info=True
            )
            return None

        msg_number = None

        if not str.isdigit(item['msg_number']):
            self.logger.warning(
                'Площадка: el-torg. ' +
                'Cсылка: %s. ' % item['trading_link'] +
                'Значение msg_number не число. ' +
                'Полученое значение: \'%s\'.' % item['msg_number'],
                exc_info=True
            )
        else:
            msg_number = item['msg_number']

        return msg_number

    def cleaning_debtorInn(self, item):
        if 'debtor_inn' not in item.keys():
            self.logger.warning(
                'Площадка: el-torg. ' +
                'Cсылка: %s. ' % item['debtor_inn'] +
                'Значение debtor_inn не получено при парсинге.',
                exc_info=True
            )
            return None

        if not str.isdigit(item['debtor_inn']):
            self.logger.warning(
                'Площадка: el-torg. ' +
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
                'Площадка: el-torg. ' +
                'Cсылка: %s. ' % item['arbit_manager'] +
                'Значение arbit_manager не получено при парсинге.',
                exc_info=True
            )
            return None

        arbit_manager = item['arbit_manager']
        if len(list(set(item['arbit_manager']))) != 3: self.logger.warning(
            'Площадка: el-torg. ' +
            'Cсылка: %s. ' % item['trading_link'] +
            'Значение arbit_manager возможно неверно. ' +
            'Полученое значение: \'%s\'.' % item['arbit_manager'],
            exc_info=True
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
                'Площадка: el-torg. ' +
                'Cсылка: %s. ' % ''.join(item['arbit_manager_inn']) +
                'Значение arbit_manager_inn не получено при парсинге.',
                exc_info=True
            )
            return None

        arbit_manager_inn = None

        if not str.isdigit(item['arbit_manager_inn']):
            self.logger.warning(
                'Площадка: el-torg. ' +
                'Cсылка: %s. ' % ''.join(item['trading_link']) +
                'Значение arbit_manager_inn не число. ' +
                'Полученое значение: \'%s\'.' % ''.join(item['arbit_manager_inn']),
                exc_info=True
            )
        else:
            arbit_manager_inn = item['arbit_manager_inn']

        return arbit_manager_inn

    def cleaning_arbitManagerOrg(self, item):
        if 'arbit_manager_org' not in item.keys():
            self.logger.warning(
                'Площадка: el-torg. ' +
                'Cсылка: %s. ' % item['trading_link'] +
                'Значение arbit_manager_org не получено при парсинге.',
                exc_info=True
            )
            return None

        return item['arbit_manager_org']

    def cleaning_status(self, item):
        if 'status' not in item.keys():
            self.logger.warning(
                'Площадка: el-torg. ' +
                'Cсылка: %s. ' % item['trading_link'] +
                'Значение status не получено при парсинге.',
                exc_info=True
            )
            return None

        status = None

        if item['status'] == "Прием заявок":
            status = "active"
        elif item['status'] in [
            'Торги объявлены',
            'На рассмотрении'
        ]:
            status = "pending"
        elif item['status'] in [
            'Прием заявок завершен',
            'Идут торги',
            'Подведение итогов',
            'Торги завершены',
            'Торги не состоялись',
            'Торги приостановлены',
            'Торги отменены'
        ]:
            status = "ended"

        if status is None: self.logger.warning(
            'Площадка: el-torg. ' +
            'Cсылка: %s. ' % item['trading_link'] +
            'Значение status не присвоено. ' +
            'Полученое значение: \'%s\'.' % item['status'],
            exc_info=True
        )

        return status

    def cleaning_lotId(self, item):
        lot_id = None

        if not str.isdigit(item['lot_id'].split("=")[-1]):
            self.logger.warning(
                'Площадка: el-torg. ' +
                'Cсылка: %s. ' % item['lot_link'] +
                'Значение lot_id не число. ' +
                'Полученое значение: \'%s\'.' % item['lot_id'].split("=")[-1],
                exc_info=True
            )
        else:
            lot_id = item['lot_id'].split("=")[-1]

        return lot_id

    def cleaning_lotNumber(self, item):
        if 'lot_number' not in item.keys(): self.logger.warning(
            'Площадка: el-torg. ' +
            'Cсылка: %s. ' % item['lot_link'] +
            'Значение lot_number не получено при парсинге.',
            exc_info=True
        )

        lot_number = None

        if not str.isdigit(item['lot_number']):
            self.logger.warning(
                'Площадка: el-torg. ' +
                'Cсылка: %s. ' % item['lot_link'] +
                'Значение lot_number не число. ' +
                'Полученое значение: \'%s\'.' % item['lot_number'],
                exc_info=True
            )
        else:
            lot_number = item['lot_number']

        return lot_number

    def cleaning_lotInfo(self, item):
        if 'lot_info' not in item.keys():
            self.logger.warning(
                'Площадка: el-torg. ' +
                'Cсылка: %s. ' % item['trading_link'] +
                'Значение trading_number не получено при парсинге.',
                exc_info=True
            )
            return None

        return item['lot_info']

    def cleaning_date(self, date_str):
        return datetime.strptime(date_str, "%d.%m.%Y %H:%M").strftime("%Y-%m-%d %H:%M:%S")

    def cleaning_altDate(self, date_str):
        return datetime.strptime(date_str, "%d.%m.%Y %H:%M:%S").strftime("%Y-%m-%d %H:%M:%S")

    def cleaning_price(self, price_str):
        return float(price_str.replace(" ", "").replace("руб.", ""))

    def cleaning_startDateRequests(self, item):
        if 'start_date_requests' not in item.keys(): self.logger.warning(
            'Площадка: el-torg. ' +
            'Cсылка: %s. ' % item['lot_link'] +
            'Значение start_date_requests не получено при парсинге.',
            exc_info=True
        )

        try:
            return self.cleaning_altDate(item['start_date_requests'])
        except:
            self.logger.warning(
                'Площадка: ru-trade24.ru. ' +
                'Cсылка: %s. ' % item['trading_link'] +
                'Неверный формат поля start_date_requests. ' +
                'Полученое значение: \'%s\'.' % item['start_date_requests'],
                exc_info=True
            )

            return None

    def cleaning_endDateRequests(self, item):
        if 'end_date_requests' not in item.keys(): self.logger.warning(
            'Площадка: el-torg. ' +
            'Cсылка: %s. ' % item['lot_link'] +
            'Значение end_date_requests не получено при парсинге.',
            exc_info=True
        )

        try:
            return self.cleaning_altDate(item['end_date_requests'])
        except:
            self.logger.warning(
                'Площадка: el-torg.ru. ' +
                'Cсылка: %s. ' % item['trading_link'] +
                'Неверный формат поля end_date_requests. ' +
                'Полученое значение: \'%s\'.' % item['end_date_requests'],
                exc_info=True
            )

            return None

    def cleaning_periods(self, item):
        if 'periods' not in item.keys(): return []

        parser = BeautifulSoup(item['periods'], 'html.parser')
        periods = []

        for row in parser.select("tr")[1:]:
            period = {
                "start_date_requests": self.cleaning_date(row.select('td')[0].get_text().strip()),
                "end_date_requests": self.cleaning_date(row.select('td')[1].get_text().strip()),
                "end_date_trading": self.cleaning_date(row.select('td')[1].get_text().strip()),
                "current_price": self.cleaning_price(row.select('td')[-1].get_text().strip())
            }

            periods.append(period)

        return periods

    def cleaning_startDateTrading(self, item):
        if 'start_date_trading' in item.keys():
            try:
                return self.cleaning_altDate(item['start_date_trading'])
            except:
                self.logger.warning(
                    'Площадка: el-torg. ' +
                    'Cсылка: %s. ' % item['trading_link'] +
                    'Неверный формат поля start_date_trading. ' + \
                    'Полученое значение: \'%s\'.' % item['start_date_trading'],
                    exc_info=True
                )
        if 'periods' in item.keys() and len(item['periods']) != 0: return item['periods'][0]['start_date_requests']

        return None

    def cleaning_endDateTrading(self, item):
        if item['trading_type'] != 'offer': return None

        if 'end_date_trading' in item.keys():
            try:
                return self.cleaning_altDate(item['end_date_trading'])
            except:
                self.logger.warning(
                    'Площадка: el-torg. ' +
                    'Cсылка: %s. ' % item['trading_link'] +
                    'Неверный формат поля end_date_trading. ' + \
                    'Полученое значение: \'%s\'.' % item['end_date_trading'],
                    exc_info=True
                )
        if 'periods' in item.keys() and len(item['periods']) != 0: return item['periods'][0]['end_date_requests']

        return None

    def cleaning_startPrice(self, item):
        if 'start_price' not in item.keys():
            self.logger.warning(
                'Площадка: el-torg. ' +
                'Cсылка: %s. ' % item['lot_link'] +
                'Значение start_price не получено при парсинге.',
                exc_info=True
            )
            return None

        return self.cleaning_price(item['start_price'])

    def cleaning_stepPrice(self, item):
        if item['trading_type'] == 'offer': return None
        if 'step_price' not in item.keys():
            self.logger.warning(
                'Площадка: el-torg. ' +
                'Cсылка: %s. ' % item['lot_link'] +
                'Значение step_price не получено при парсинге.',
                exc_info=True
            )
            return None

        if self.cleaning_price(item['step_price']) == 0: return None

        return self.cleaning_price(item['step_price'])

    def cleaning_files(self, item):
        files = {
            'general': [],
            'lot': []
        }

        if 'files' in item.keys(): files['lot'] = self.cleaning_lotFiles(item['files'], item)
        files['general'] = self.cleaning_generalFiles(item)

        return files

    def cleaning_lotFiles(self, str_html, item):
        if str_html is None: return ''

        files = []
        for row in item['files']:
            parser = BeautifulSoup(row, 'html.parser')
            link = ''
            if parser.select_one('a').get_text().strip().split('.')[-1] in ['jpeg', 'jpg', 'png', 'JPG']:
                link = f'{relative_path}/%s/%02d/%s_%s' % (
                    datetime.today().year, datetime.today().month, item['lot_id'],
                    parser.select_one('a').get_text().strip())
                link = link.replace(' ', '_')

            _file = {
                'original_name': parser.select_one('a').get_text().strip(),
                'link': link,
                'link_etp': parser.select_one('a')['href']
            }

            files.append(_file)

        return files

    def cleaning_generalFiles(self, item):
        r = requests.get(item['trading_link'])
        if r.status_code == 500:
            self.logger.warning(
                'Площадка: el-torg. ' +
                'Cсылка: %s. ' % item['lot_link'] +
                'При переходе на страницу %s выдало ошибку 500.' % item['trading_link'],
                exc_info=True
            )

            return []

        parser = BeautifulSoup(r.text, 'html.parser')

        files = []
        for row in parser.select_one('a[name=docs_list]').findNextSibling('table').select('tr')[1:]:
            link = ''
            if row.select_one('a').get_text().strip().split('.')[-1] in ['jpeg', 'jpg', 'png', 'JPG']:
                link = f'{relative_path}/%s/%02d/%s_%s' % (
                    datetime.today().year, datetime.today().month, item['lot_id'],
                    row.select_one('a').get_text().strip())
                link = link.replace(' ', '_')

            _file = {
                'original_name': row.select_one('a').get_text().strip(),
                'link': link,
                'link_etp': row.select_one('a')['href']
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
        # relative_dir = '/%d/%02d/' % (datetime.today().year, datetime.today().month)
        #
        # for i in range(len(relative_dir[1:].split('/'))):
        #     if not os.path.exists(base_dir + etp_folder + '/' + '/'.join(relative_dir[1:].split('/')[:i + 1])):
        #         os.mkdir(base_dir + etp_folder + '/' + '/'.join(relative_dir[1:].split('/')[:i + 1]))
        #
        locate_dir = base_dir.replace('/downloads', '')
        # locate_dir = ''

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

        f = open(base_path + _file['link'], 'wb')
        f.write(r.content)
        f.close()

    def checking(self, item):
        report = 'Площадка: el-torg. Ссылка: %s.\n' % (item['lot_link'])

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
            'msg_number',
            'periods',
            'property_information',
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
            # 'trading_org_inn',
            'trading_type'
        ]:

            if field == 'start_date_trading' and item['end_date_trading'] is not None: continue
            if field == 'end_date_trading' and item['start_date_trading'] is not None: continue
            if field == 'step_price' and item['trading_type'] not in ['auction']: continue
            if item[field] is None:
                is_print = True
                report += '\t%s = NULL\n' % field

        if is_print: self.logger.warning(report)

    def add_to_db(self, item):
        unique_value = '_'.join([item[field] for field in db_connect['unique_fields']])

        if unique_value in self.included:
            query = ('UPDATE %s SET ' % db_connect['table_name'] +
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
                     'trading_type = %s' +
                     'WHERE %s' % ' and '.join(
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
