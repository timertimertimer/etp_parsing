# -*- coding: utf-8 -*-
import mysql
from mysql.connector import MySQLConnection
import logging

from general_utils import read_db_config

logger = logging.getLogger(__name__)


class CrawlerMsgFedresursPipeline:

    def process_item(self, item, spider):
        for f in item.fields:
            if item == 'lots':
                item.setdefault(f, list())
            else:
                item.setdefault(f, None)
        return item


class CrawlerDbConnect(object):

    def __init__(self):
        self.db_config = read_db_config()
        self.conn = MySQLConnection(**self.db_config)
        self.curr = self.conn.cursor()
        self.create_table()

    def create_table(self):
        self.curr.execute(f"""CREATE TABLE IF NOT EXISTS {table}(
                           id bigint AUTO_INCREMENT PRIMARY KEY,
                           message_link varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
                           message_type varchar(255) COLLATE utf8mb4_unicode_ci,
                           message_number varchar(12) COLLATE utf8mb4_unicode_ci NOT NULL,
                           publish_date varchar(255) COLLATE utf8mb4_unicode_ci,
                           debtor_inn varchar(12) COLLATE utf8mb4_unicode_ci,
                           debtor_name text COLLATE utf8mb4_unicode_ci,
                           debtor_address text COLLATE utf8mb4_unicode_ci,
                           case_number varchar(255) COLLATE utf8mb4_unicode_ci,
                           canceled_message varchar(20) COLLATE utf8mb4_unicode_ci,
                           announced_message varchar(20) COLLATE utf8mb4_unicode_ci,
                           modified_message varchar(20) COLLATE utf8mb4_unicode_ci,
                           lots mediumtext COLLATE utf8mb4_bin,
                           files mediumtext COLLATE utf8mb4_bin,
                           created_at timestamp,
                           CONSTRAINT CK_{table} UNIQUE (message_link, message_type, message_number)

                                                               )

                           """)

    def store_db(self, item):
        self.curr.execute(
            f"""insert into {table}(message_link, message_type, message_number, publish_date, debtor_inn, debtor_name,
                                    debtor_address, case_number, canceled_message, announced_message, 
                                    modified_message, lots, files, created_at) 
               values (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s) ON DUPLICATE KEY UPDATE 
                                       message_link=VALUES(message_link),
                                       message_type=VALUES(message_type),
                                       message_number=VALUES(message_number),
                                       publish_date=VALUES(publish_date),
                                       debtor_inn=VALUES(debtor_inn),
                                       debtor_name=VALUES(debtor_name),
                                       debtor_address=VALUES(debtor_address),
                                       case_number=VALUES(case_number),
                                       canceled_message=VALUES(canceled_message),
                                       announced_message=VALUES(announced_message),
                                       modified_message=VALUES(modified_message),
                                       lots=VALUES(lots),
                                       files=VALUES(files),
                                       created_at=VALUES(created_at)
                                       """,
            (
                item['message_link'],
                item['message_type'],
                item['message_number'],
                item['publish_date'],
                item['debtor_inn'],
                item['debtor_name'],
                item['debtor_address'],
                item['case_number'],
                item['canceled_message'],
                item['announced_message'],
                item['modified_message'],
                item['lots'],
                item['files'],
                item['created_at']

            ))

        self.conn.commit()

    def process_item(self, item, spider):
        self.store_db(item)
        try:
            return item
        except mysql.connector.Error as error:
            logger.error(f'{error}\n {item}')
