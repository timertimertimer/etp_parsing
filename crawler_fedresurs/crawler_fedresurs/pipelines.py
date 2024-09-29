# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html
import mysql.connector
from crawler_fedresurs.utils.config import TABLE_ARBITR, TABLE_DEBITR, TABLE_ORGANIZER
from crawler_fedresurs.utils.connect_for_change_status import SetValueDb


class CrawlerFedresursPipeline:

    def process_item(self, item, spider):

        for f in item.fields:
            if item == 'lot':
                item.setdefault(f, list())
            else:
                item.setdefault(f, None)
        return item


class DbConnectOrganizer:

    def __init__(self):
        self.setvalue = SetValueDb()
        self.create_table()

    def create_table(self):
        self.setvalue.mycursor.execute(f"""CREATE TABLE IF NOT EXISTS {TABLE_ORGANIZER}(
                        id bigint AUTO_INCREMENT PRIMARY KEY,
                        item_type varchar(32) COLLATE utf8mb4_unicode_ci,
                        organizer_link text COLLATE utf8mb4_unicode_ci NOT NULL,
                        short_name varchar(255) COLLATE utf8mb4_unicode_ci,
                        full_name text COLLATE utf8mb4_unicode_ci,
                        address text COLLATE utf8mb4_unicode_ci,
                        phone varchar(255) COLLATE utf8mb4_unicode_ci,
                        region text COLLATE utf8mb4_unicode_ci,
                        inn varchar(12) COLLATE utf8mb4_unicode_ci,
                        kpp varchar(255) COLLATE utf8mb4_unicode_ci,
                        ogrn varchar(255) COLLATE utf8mb4_unicode_ci,
                        legal_form text COLLATE utf8mb4_unicode_ci,
                        created_at timestamp,
                        CONSTRAINT CK_{TABLE_ORGANIZER} UNIQUE (item_type, inn)

                                                            )

                        """)

    def store_db(self, item):
        self.setvalue.mycursor.execute(
            f"""insert into {TABLE_ORGANIZER}(item_type, organizer_link, short_name, full_name, address, phone, region,
                                inn, kpp, ogrn, legal_form, created_at) 
            values (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s) ON DUPLICATE KEY UPDATE 
                                    item_type=VALUES(item_type),
                                    organizer_link=VALUES(organizer_link),
                                    short_name=VALUES(short_name),
                                    full_name=VALUES(full_name),
                                    address=VALUES(address),
                                    phone=VALUES(phone),
                                    region=VALUES(region),
                                    inn=VALUES(inn),
                                    created_at=VALUES(created_at),
                                    ogrn=VALUES(ogrn),
                                    kpp=VALUES(kpp),
                                    legal_form=VALUES(legal_form)
                                    """,
            (
                item['item_type'],
                item['link'],
                item['short_name'],
                item['full_name'],
                item['address'],
                item['phone'],
                item['region'],
                item['inn'],
                item['kpp'],
                item['ogrn'],
                item['legal_form'],
                item['created_at']

            ))

        self.setvalue.mydb.commit()

    def process_item(self, item, spider):
        self.store_db(item)
        try:
            return item
        except mysql.connector.Error as error:
            return error


class ManageTaskTable:
    def __init__(self):
        self.setvalue = SetValueDb()

    def process_item(self, item, spider):

        for f in item.fields:
            if f == 'item_transfer' and len(item['item_transfer']) > 0:
                self.setvalue.change_status_organizer(type_=item['item_type2'],
                                                      string=item['item_transfer'], status='done')
                if item['links_count'] == 1:
                    self.setvalue.get_and_set_id_organizer(inn_=item['inn'], type_=item['item_type2'],
                                                           string=item['item_transfer'], table_=TABLE_ORGANIZER)

        return item


class DbConnectArbitr:

    def __init__(self):
        self.setvalue = SetValueDb()
        self.create_table()

    def create_table(self):
        self.setvalue.mycursor.execute(f"""CREATE TABLE IF NOT EXISTS {TABLE_ARBITR}(
                        id bigint AUTO_INCREMENT PRIMARY KEY,
                        arbitrator_link text COLLATE utf8mb4_unicode_ci NOT NULL,
                        full_name varchar(255) COLLATE utf8mb4_unicode_ci,
                        inn varchar(12) COLLATE utf8mb4_unicode_ci,
                        registration_number varchar(255) COLLATE utf8mb4_unicode_ci,
                        registration_date varchar(255) COLLATE utf8mb4_unicode_ci,
                        sro varchar(255) COLLATE utf8mb4_unicode_ci,
                        entry_date varchar(255) COLLATE utf8mb4_unicode_ci,
                        created_at timestamp,
                        CONSTRAINT CK_{TABLE_ARBITR} UNIQUE (full_name, inn)

                                                            )

                        """)

    def store_db(self, item):
        self.setvalue.mycursor.execute(
            f"""insert into {TABLE_ARBITR}(arbitrator_link,full_name,inn,registration_number,registration_date,sro,entry_date,created_at) 
            values (%s,%s,%s,%s,%s,%s,%s,%s) ON DUPLICATE KEY UPDATE arbitrator_link=VALUES(arbitrator_link),
                                    full_name=VALUES(full_name),
                                    inn=VALUES(inn),
                                    registration_number=VALUES(registration_number),
                                    registration_date=VALUES(registration_date),
                                    sro=VALUES(sro),
                                    entry_date=VALUES(entry_date),
                                    created_at=VALUES(created_at)
                                    """,
            (
                item['link'],
                item['full_name'],
                item['inn'],
                item['registration_number'],
                item['registration_date'],
                item['sro'],
                item['entry_date'],
                item['created_at']

            ))

        self.setvalue.mydb.commit()

    def process_item(self, item, spider):
        self.store_db(item)
        try:
            return item
        except mysql.connector.Error as error:
            return error


class ManageTaskTableArbitr:
    def __init__(self):
        self.setvalue = SetValueDb()

    def process_item(self, item, spider):

        for f in item.fields:
            if f == 'item_transfer' and len(item['item_transfer']) > 0:
                self.setvalue.change_status_organizer(type_=item['item_type'],
                                                      string=item['item_transfer'], status='done')
                if item['links_count'] == 1:
                    self.setvalue.get_and_set_id_organizer(inn_=item['inn'],
                                                           string=item['item_transfer'], type_=item['item_type'],
                                                           table_=TABLE_ARBITR)

        return item


class DbConnectDebitor:

    def __init__(self):
        self.setvalue = SetValueDb()
        self.create_table()

    def create_table(self):
        self.setvalue.mycursor.execute(f"""CREATE TABLE IF NOT EXISTS {TABLE_DEBITR}(
                        id bigint AUTO_INCREMENT PRIMARY KEY,
                        debtor_link text COLLATE utf8mb4_unicode_ci NOT NULL,
                        full_name varchar(255) COLLATE utf8mb4_unicode_ci,
                        category text COLLATE utf8mb4_unicode_ci,
                        region text COLLATE utf8mb4_unicode_ci,
                        address varchar(255) COLLATE utf8mb4_unicode_ci,
                        inn varchar(12) COLLATE utf8mb4_unicode_ci,
                        ogrn varchar(255) COLLATE utf8mb4_unicode_ci,
                        created_at timestamp,
                        CONSTRAINT CK_{TABLE_DEBITR} UNIQUE (full_name, inn)

                                                            )

                        """)

    def store_db(self, item):
        self.setvalue.mycursor.execute(
            f"""insert into {TABLE_DEBITR}(debtor_link, full_name,category,region,address,inn,ogrn,created_at) 
            values (%s,%s,%s,%s,%s,%s,%s,%s) ON DUPLICATE KEY UPDATE debtor_link=VALUES(debtor_link),
                                    full_name=VALUES(full_name),
                                    category=VALUES(category),
                                    region=VALUES(region),
                                    address=VALUES(address),
                                    inn=VALUES(inn),
                                    ogrn=VALUES(ogrn),
                                    created_at=VALUES(created_at)
                                    """,
            (
                item['link'],
                item['full_name'],
                item['category'],
                item['region'],
                item['address'],
                item['inn'],
                item['ogrn'],
                item['created_at']

            ))

        self.setvalue.mydb.commit()

    def process_item(self, item, spider):
        self.store_db(item)
        try:
            return item
        except mysql.connector.Error as error:
            return error


class ManageTaskTableDebitor:
    def __init__(self):
        self.setvalue = SetValueDb()

    def process_item(self, item, spider):

        for f in item.fields:
            if f == 'item_transfer' and len(item['item_transfer']) > 0:
                self.setvalue.change_status_organizer(type_=item['item_type'],
                                                      string=item['item_transfer'], status='done')
                if item['links_count'] == 1:
                    self.setvalue.get_and_set_id_organizer(inn_=item['inn'],
                                                           string=item['item_transfer'], type_=item['item_type'],
                                                           table_=TABLE_DEBITR)

        return item
