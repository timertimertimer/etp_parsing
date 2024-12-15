# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from mysql.connector import MySQLConnection, Error

from crawler_altimeta.python_mysql_dbconfig import read_db_config
from .utils.config import tables


class CrawlerAltimetaPipeline:
    def process_item(self, item, spider):

        for f in item.fields:
            if item == 'lot':
                item.setdefault(f, list())
            else:
                item.setdefault(f, None)
        return item


class Connect:
    def __init__(self):
        self.db_config = read_db_config()
        self.conn = MySQLConnection(**self.db_config)
        self.curr = self.conn.cursor()


class AtcTradeDbConnect(Connect):
    def __init__(self):
        super(AtcTradeDbConnect, self).__init__()
        self.create_table()

    def create_table(self):
        self.curr.execute(f"""CREATE TABLE IF NOT EXISTS {tables['table_atctrade']}(
                            id bigint AUTO_INCREMENT PRIMARY KEY,
                            data_origin text COLLATE utf8mb4_unicode_ci,
                            trading_id varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
                            trading_link text COLLATE utf8mb4_unicode_ci NOT NULL,
                            trading_number varchar(255) COLLATE utf8mb4_unicode_ci,
                            trading_type varchar(32) COLLATE utf8mb4_unicode_ci,
                            trading_form text COLLATE utf8mb4_unicode_ci,
                            trading_org text COLLATE utf8mb4_unicode_ci,
                            trading_org_inn text(12) COLLATE utf8mb4_unicode_ci,
                            trading_org_contacts text COLLATE utf8mb4_bin,
                            msg_number varchar(255) COLLATE utf8mb4_unicode_ci,
                            case_number varchar(255) COLLATE utf8mb4_unicode_ci,
                            debtor_inn text(12) COLLATE utf8mb4_unicode_ci,
                            arbit_manager text COLLATE utf8mb4_unicode_ci,
                            arbit_manager_inn text(12) COLLATE utf8mb4_unicode_ci,
                            arbit_manager_org text COLLATE utf8mb4_unicode_ci,
                            status varchar(255) COLLATE utf8mb4_unicode_ci,
                            lot_id varchar(255) COLLATE utf8mb4_unicode_ci,
                            lot_link text COLLATE utf8mb4_unicode_ci,
                            lot_number smallint COLLATE utf8mb4_unicode_ci,
                            short_name mediumtext COLLATE utf8mb4_unicode_ci,
                            lot_info mediumtext COLLATE utf8mb4_unicode_ci,
                            property_information mediumtext COLLATE utf8mb4_unicode_ci,
                            start_date_requests timestamp,
                            end_date_requests timestamp,
                            start_date_trading timestamp,
                            end_date_trading timestamp,
                            start_price double,
                            step_price double,
                            periods mediumtext COLLATE utf8mb4_bin,
                            files mediumtext COLLATE utf8mb4_bin,
                            created_at timestamp,
                            CONSTRAINT CK_{tables['table_atctrade']} UNIQUE (trading_id, trading_type, lot_number)

                                                                )

                            """)

    def store_db(self, item):
        self.curr.execute(
            f"""insert into {tables['table_atctrade']}(data_origin,trading_id,trading_link,trading_number,trading_type,
    trading_form,trading_org,trading_org_inn,trading_org_contacts,msg_number,case_number,debtor_inn,arbit_manager,
    arbit_manager_inn,arbit_manager_org,status,lot_id,lot_link,lot_number,short_name,lot_info,property_information,
    start_date_requests,end_date_requests,start_date_trading,end_date_trading,start_price,step_price,periods,files,
    created_at) values (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,
    %s) ON DUPLICATE KEY UPDATE trading_id=VALUES(trading_id),
                                        data_origin=VALUES(data_origin),
                                        trading_link=VALUES(trading_link),
                                        trading_number=VALUES(trading_number),
                                        trading_type=VALUES(trading_type),
                                        trading_form=VALUES(trading_form),
                                        trading_org=VALUES(trading_org),
                                        trading_org_inn=VALUES(trading_org_inn),
                                        trading_org_contacts=VALUES(trading_org_contacts),
                                        msg_number=VALUES(msg_number),
                                        case_number = VALUES(case_number),
                                        debtor_inn = VALUES(debtor_inn),
                                        arbit_manager = VALUES(arbit_manager),
                                        arbit_manager_inn = VALUES(arbit_manager_inn),
                                        arbit_manager_org=VALUES(arbit_manager_org),
                                        status=VALUES(status),
                                        lot_id=VALUES(lot_id),
                                        lot_link=VALUES(lot_link),
                                        lot_number=VALUES(lot_number),
                                        short_name=VALUES(short_name),
                                        lot_info=VALUES(lot_info),
                                        property_information=VALUES(property_information),
                                        start_date_requests=VALUES(start_date_requests),
                                        end_date_requests=VALUES(end_date_requests), 
                                        start_date_trading=VALUES(start_date_trading), 
                                        end_date_trading=VALUES(end_date_trading),
                                        start_price=VALUES(start_price), 
                                        step_price=VALUES(step_price),
                                        periods=VALUES(periods), 
                                        files=VALUES(files),
                                        created_at=VALUES(created_at)
                                        """,
            (
                item['data_origin'],
                item['trading_id'],
                item['trading_link'],
                item['trading_number'],
                item['trading_type'],
                item['trading_form'],
                item['trading_org'],
                item['trading_org_inn'],
                item['trading_org_contacts'],
                item['msg_number'],
                item['case_number'],
                item['debtor_inn'],
                item['arbit_manager'],
                item['arbit_manager_inn'],
                item['arbit_manager_org'],
                item['status'],
                item['lot_id'],
                item['lot_link'],
                item['lot_number'],
                item['short_name'],
                item['lot_info'],
                item['property_information'],
                item['start_date_requests'],
                item['end_date_requests'],
                item['start_date_trading'],
                item['end_date_trading'],
                item['start_price'],
                item['step_price'],
                item['periods'],
                item['files'],
                item['created_at']

            ))

        self.conn.commit()

    def process_item(self, item, spider):
        self.store_db(item)
        try:
            return item
        except Error as error:
            return error


class AukcionCenterDbConnect(object):

    def __init__(self):
        self.db_config = read_db_config()
        self.conn = MySQLConnection(**self.db_config)
        self.curr = self.conn.cursor()
        self.create_table()

    def create_table(self):
        self.curr.execute(f"""CREATE TABLE IF NOT EXISTS {tables['table_aukcioncenter']}(
                            id bigint AUTO_INCREMENT PRIMARY KEY,
                            data_origin text COLLATE utf8mb4_unicode_ci,
                            trading_id varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
                            trading_link text COLLATE utf8mb4_unicode_ci NOT NULL,
                            trading_number varchar(255) COLLATE utf8mb4_unicode_ci,
                            trading_type varchar(32) COLLATE utf8mb4_unicode_ci,
                            trading_form text COLLATE utf8mb4_unicode_ci,
                            trading_org text COLLATE utf8mb4_unicode_ci,
                            trading_org_inn text(12) COLLATE utf8mb4_unicode_ci,
                            trading_org_contacts text COLLATE utf8mb4_bin,
                            msg_number varchar(255) COLLATE utf8mb4_unicode_ci,
                            case_number varchar(255) COLLATE utf8mb4_unicode_ci,
                            debtor_inn text(12) COLLATE utf8mb4_unicode_ci,
                            arbit_manager text COLLATE utf8mb4_unicode_ci,
                            arbit_manager_inn text(12) COLLATE utf8mb4_unicode_ci,
                            arbit_manager_org text COLLATE utf8mb4_unicode_ci,
                            status varchar(255) COLLATE utf8mb4_unicode_ci,
                            lot_id varchar(255) COLLATE utf8mb4_unicode_ci,
                            lot_link text COLLATE utf8mb4_unicode_ci,
                            lot_number smallint COLLATE utf8mb4_unicode_ci,
                            short_name mediumtext COLLATE utf8mb4_unicode_ci,
                            lot_info mediumtext COLLATE utf8mb4_unicode_ci,
                            property_information mediumtext COLLATE utf8mb4_unicode_ci,
                            start_date_requests timestamp,
                            end_date_requests timestamp,
                            start_date_trading timestamp,
                            end_date_trading timestamp,
                            start_price double,
                            step_price double,
                            periods mediumtext COLLATE utf8mb4_bin,
                            files mediumtext COLLATE utf8mb4_bin,
                            created_at timestamp,
                            CONSTRAINT CK_{tables['table_aukcioncenter']} UNIQUE (trading_id, trading_type, lot_number)

                                                                )

                            """)

    def store_db(self, item):
        self.curr.execute(
            f"""insert into {tables['table_aukcioncenter']}(data_origin,trading_id,trading_link,trading_number,trading_type,
    trading_form,trading_org,trading_org_inn,trading_org_contacts,msg_number,case_number,debtor_inn,arbit_manager,
    arbit_manager_inn,arbit_manager_org,status,lot_id,lot_link,lot_number,short_name,lot_info,property_information,
    start_date_requests,end_date_requests,start_date_trading,end_date_trading,start_price,step_price,periods,files,
    created_at) values (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,
    %s) ON DUPLICATE KEY UPDATE trading_id=VALUES(trading_id),
                                        data_origin=VALUES(data_origin),
                                        trading_link=VALUES(trading_link),
                                        trading_number=VALUES(trading_number),
                                        trading_type=VALUES(trading_type),
                                        trading_form=VALUES(trading_form),
                                        trading_org=VALUES(trading_org),
                                        trading_org_inn=VALUES(trading_org_inn),
                                        trading_org_contacts=VALUES(trading_org_contacts),
                                        msg_number=VALUES(msg_number),
                                        case_number = VALUES(case_number),
                                        debtor_inn = VALUES(debtor_inn),
                                        arbit_manager = VALUES(arbit_manager),
                                        arbit_manager_inn = VALUES(arbit_manager_inn),
                                        arbit_manager_org=VALUES(arbit_manager_org),
                                        status=VALUES(status),
                                        lot_id=VALUES(lot_id),
                                        lot_link=VALUES(lot_link),
                                        lot_number=VALUES(lot_number),
                                        short_name=VALUES(short_name),
                                        lot_info=VALUES(lot_info),
                                        property_information=VALUES(property_information),
                                        start_date_requests=VALUES(start_date_requests),
                                        end_date_requests=VALUES(end_date_requests), 
                                        start_date_trading=VALUES(start_date_trading), 
                                        end_date_trading=VALUES(end_date_trading),
                                        start_price=VALUES(start_price), 
                                        step_price=VALUES(step_price),
                                        periods=VALUES(periods), 
                                        files=VALUES(files),
                                        created_at=VALUES(created_at)
                                        """,
            (
                item['data_origin'],
                item['trading_id'],
                item['trading_link'],
                item['trading_number'],
                item['trading_type'],
                item['trading_form'],
                item['trading_org'],
                item['trading_org_inn'],
                item['trading_org_contacts'],
                item['msg_number'],
                item['case_number'],
                item['debtor_inn'],
                item['arbit_manager'],
                item['arbit_manager_inn'],
                item['arbit_manager_org'],
                item['status'],
                item['lot_id'],
                item['lot_link'],
                item['lot_number'],
                item['short_name'],
                item['lot_info'],
                item['property_information'],
                item['start_date_requests'],
                item['end_date_requests'],
                item['start_date_trading'],
                item['end_date_trading'],
                item['start_price'],
                item['step_price'],
                item['periods'],
                item['files'],
                item['created_at']

            ))

        self.conn.commit()

    def process_item(self, item, spider):
        self.store_db(item)
        try:
            return item
        except Error as error:
            return error


class AusibDbConnect(object):

    def __init__(self):
        self.db_config = read_db_config()
        self.conn = MySQLConnection(**self.db_config)
        self.curr = self.conn.cursor()
        self.create_table()

    def create_table(self):
        self.curr.execute(f"""CREATE TABLE IF NOT EXISTS {tables['table_ausib']}(
                            id bigint AUTO_INCREMENT PRIMARY KEY,
                            data_origin text COLLATE utf8mb4_unicode_ci,
                            trading_id varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
                            trading_link text COLLATE utf8mb4_unicode_ci NOT NULL,
                            trading_number varchar(255) COLLATE utf8mb4_unicode_ci,
                            trading_type varchar(32) COLLATE utf8mb4_unicode_ci,
                            trading_form text COLLATE utf8mb4_unicode_ci,
                            trading_org text COLLATE utf8mb4_unicode_ci,
                            trading_org_inn text(12) COLLATE utf8mb4_unicode_ci,
                            trading_org_contacts text COLLATE utf8mb4_bin,
                            msg_number varchar(255) COLLATE utf8mb4_unicode_ci,
                            case_number varchar(255) COLLATE utf8mb4_unicode_ci,
                            debtor_inn text(12) COLLATE utf8mb4_unicode_ci,
                            arbit_manager text COLLATE utf8mb4_unicode_ci,
                            arbit_manager_inn text(12) COLLATE utf8mb4_unicode_ci,
                            arbit_manager_org text COLLATE utf8mb4_unicode_ci,
                            status varchar(255) COLLATE utf8mb4_unicode_ci,
                            lot_id varchar(255) COLLATE utf8mb4_unicode_ci,
                            lot_link text COLLATE utf8mb4_unicode_ci,
                            lot_number smallint COLLATE utf8mb4_unicode_ci,
                            short_name mediumtext COLLATE utf8mb4_unicode_ci,
                            lot_info mediumtext COLLATE utf8mb4_unicode_ci,
                            property_information mediumtext COLLATE utf8mb4_unicode_ci,
                            start_date_requests timestamp,
                            end_date_requests timestamp,
                            start_date_trading timestamp,
                            end_date_trading timestamp,
                            start_price double,
                            step_price double,
                            periods mediumtext COLLATE utf8mb4_bin,
                            files mediumtext COLLATE utf8mb4_bin,
                            created_at timestamp,
                            CONSTRAINT CK_{tables['table_ausib']} UNIQUE (trading_id, trading_type, lot_number)

                                                                )

                            """)

    def store_db(self, item):
        self.curr.execute(
            f"""insert into {tables['table_ausib']}(data_origin,trading_id,trading_link,trading_number,trading_type,
    trading_form,trading_org,trading_org_inn,trading_org_contacts,msg_number,case_number,debtor_inn,arbit_manager,
    arbit_manager_inn,arbit_manager_org,status,lot_id,lot_link,lot_number,short_name,lot_info,property_information,
    start_date_requests,end_date_requests,start_date_trading,end_date_trading,start_price,step_price,periods,files,
    created_at) values (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,
    %s) ON DUPLICATE KEY UPDATE trading_id=VALUES(trading_id),
                                        data_origin=VALUES(data_origin),
                                        trading_link=VALUES(trading_link),
                                        trading_number=VALUES(trading_number),
                                        trading_type=VALUES(trading_type),
                                        trading_form=VALUES(trading_form),
                                        trading_org=VALUES(trading_org),
                                        trading_org_inn=VALUES(trading_org_inn),
                                        trading_org_contacts=VALUES(trading_org_contacts),
                                        msg_number=VALUES(msg_number),
                                        case_number = VALUES(case_number),
                                        debtor_inn = VALUES(debtor_inn),
                                        arbit_manager = VALUES(arbit_manager),
                                        arbit_manager_inn = VALUES(arbit_manager_inn),
                                        arbit_manager_org=VALUES(arbit_manager_org),
                                        status=VALUES(status),
                                        lot_id=VALUES(lot_id),
                                        lot_link=VALUES(lot_link),
                                        lot_number=VALUES(lot_number),
                                        short_name=VALUES(short_name),
                                        lot_info=VALUES(lot_info),
                                        property_information=VALUES(property_information),
                                        start_date_requests=VALUES(start_date_requests),
                                        end_date_requests=VALUES(end_date_requests), 
                                        start_date_trading=VALUES(start_date_trading), 
                                        end_date_trading=VALUES(end_date_trading),
                                        start_price=VALUES(start_price), 
                                        step_price=VALUES(step_price),
                                        periods=VALUES(periods), 
                                        files=VALUES(files),
                                        created_at=VALUES(created_at)
                                        """,
            (
                item['data_origin'],
                item['trading_id'],
                item['trading_link'],
                item['trading_number'],
                item['trading_type'],
                item['trading_form'],
                item['trading_org'],
                item['trading_org_inn'],
                item['trading_org_contacts'],
                item['msg_number'],
                item['case_number'],
                item['debtor_inn'],
                item['arbit_manager'],
                item['arbit_manager_inn'],
                item['arbit_manager_org'],
                item['status'],
                item['lot_id'],
                item['lot_link'],
                item['lot_number'],
                item['short_name'],
                item['lot_info'],
                item['property_information'],
                item['start_date_requests'],
                item['end_date_requests'],
                item['start_date_trading'],
                item['end_date_trading'],
                item['start_price'],
                item['step_price'],
                item['periods'],
                item['files'],
                item['created_at']

            ))

        self.conn.commit()

    def process_item(self, item, spider):
        self.store_db(item)
        try:
            return item
        except Error as error:
            return error


class EtpProfitRuDbConnect(object):

    def __init__(self):
        self.db_config = read_db_config()
        self.conn = MySQLConnection(**self.db_config)
        self.curr = self.conn.cursor()
        self.create_table()

    def create_table(self):
        self.curr.execute(f"""CREATE TABLE IF NOT EXISTS {tables['table_etp_profit_ru']}(
                            id bigint AUTO_INCREMENT PRIMARY KEY,
                            data_origin text COLLATE utf8mb4_unicode_ci,
                            trading_id varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
                            trading_link text COLLATE utf8mb4_unicode_ci NOT NULL,
                            trading_number varchar(255) COLLATE utf8mb4_unicode_ci,
                            trading_type varchar(32) COLLATE utf8mb4_unicode_ci,
                            trading_form text COLLATE utf8mb4_unicode_ci,
                            trading_org text COLLATE utf8mb4_unicode_ci,
                            trading_org_inn text(12) COLLATE utf8mb4_unicode_ci,
                            trading_org_contacts text COLLATE utf8mb4_bin,
                            msg_number varchar(255) COLLATE utf8mb4_unicode_ci,
                            case_number varchar(255) COLLATE utf8mb4_unicode_ci,
                            debtor_inn text(12) COLLATE utf8mb4_unicode_ci,
                            arbit_manager text COLLATE utf8mb4_unicode_ci,
                            arbit_manager_inn text(12) COLLATE utf8mb4_unicode_ci,
                            arbit_manager_org text COLLATE utf8mb4_unicode_ci,
                            status varchar(255) COLLATE utf8mb4_unicode_ci,
                            lot_id varchar(255) COLLATE utf8mb4_unicode_ci,
                            lot_link text COLLATE utf8mb4_unicode_ci,
                            lot_number smallint COLLATE utf8mb4_unicode_ci,
                            short_name mediumtext COLLATE utf8mb4_unicode_ci,
                            lot_info mediumtext COLLATE utf8mb4_unicode_ci,
                            property_information mediumtext COLLATE utf8mb4_unicode_ci,
                            start_date_requests timestamp,
                            end_date_requests timestamp,
                            start_date_trading timestamp,
                            end_date_trading timestamp,
                            start_price double,
                            step_price double,
                            periods mediumtext COLLATE utf8mb4_bin,
                            files mediumtext COLLATE utf8mb4_bin,
                            created_at timestamp,
                            CONSTRAINT CK_{tables['table_etp_profit_ru']} UNIQUE (trading_id, trading_type, lot_number)

                                                                )

                            """)

    def store_db(self, item):
        self.curr.execute(
            f"""insert into {tables['table_etp_profit_ru']}(data_origin,trading_id,trading_link,trading_number,trading_type,
    trading_form,trading_org,trading_org_inn,trading_org_contacts,msg_number,case_number,debtor_inn,arbit_manager,
    arbit_manager_inn,arbit_manager_org,status,lot_id,lot_link,lot_number,short_name,lot_info,property_information,
    start_date_requests,end_date_requests,start_date_trading,end_date_trading,start_price,step_price,periods,files,
    created_at) values (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,
    %s) ON DUPLICATE KEY UPDATE trading_id=VALUES(trading_id),
                                        data_origin=VALUES(data_origin),
                                        trading_link=VALUES(trading_link),
                                        trading_number=VALUES(trading_number),
                                        trading_type=VALUES(trading_type),
                                        trading_form=VALUES(trading_form),
                                        trading_org=VALUES(trading_org),
                                        trading_org_inn=VALUES(trading_org_inn),
                                        trading_org_contacts=VALUES(trading_org_contacts),
                                        msg_number=VALUES(msg_number),
                                        case_number = VALUES(case_number),
                                        debtor_inn = VALUES(debtor_inn),
                                        arbit_manager = VALUES(arbit_manager),
                                        arbit_manager_inn = VALUES(arbit_manager_inn),
                                        arbit_manager_org=VALUES(arbit_manager_org),
                                        status=VALUES(status),
                                        lot_id=VALUES(lot_id),
                                        lot_link=VALUES(lot_link),
                                        lot_number=VALUES(lot_number),
                                        short_name=VALUES(short_name),
                                        lot_info=VALUES(lot_info),
                                        property_information=VALUES(property_information),
                                        start_date_requests=VALUES(start_date_requests),
                                        end_date_requests=VALUES(end_date_requests), 
                                        start_date_trading=VALUES(start_date_trading), 
                                        end_date_trading=VALUES(end_date_trading),
                                        start_price=VALUES(start_price), 
                                        step_price=VALUES(step_price),
                                        periods=VALUES(periods), 
                                        files=VALUES(files),
                                        created_at=VALUES(created_at)
                                        """,
            (
                item['data_origin'],
                item['trading_id'],
                item['trading_link'],
                item['trading_number'],
                item['trading_type'],
                item['trading_form'],
                item['trading_org'],
                item['trading_org_inn'],
                item['trading_org_contacts'],
                item['msg_number'],
                item['case_number'],
                item['debtor_inn'],
                item['arbit_manager'],
                item['arbit_manager_inn'],
                item['arbit_manager_org'],
                item['status'],
                item['lot_id'],
                item['lot_link'],
                item['lot_number'],
                item['short_name'],
                item['lot_info'],
                item['property_information'],
                item['start_date_requests'],
                item['end_date_requests'],
                item['start_date_trading'],
                item['end_date_trading'],
                item['start_price'],
                item['step_price'],
                item['periods'],
                item['files'],
                item['created_at']

            ))

        self.conn.commit()

    def process_item(self, item, spider):
        self.store_db(item)
        try:
            return item
        except Error as error:
            return error


class PtpCentrRuDbConnect(object):

    def __init__(self):
        self.db_config = read_db_config()
        self.conn = MySQLConnection(**self.db_config)
        self.curr = self.conn.cursor()
        self.create_table()

    def create_table(self):
        self.curr.execute(f"""CREATE TABLE IF NOT EXISTS {tables['table_ptp_center']}(
                            id bigint AUTO_INCREMENT PRIMARY KEY,
                            data_origin text COLLATE utf8mb4_unicode_ci,
                            trading_id varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
                            trading_link text COLLATE utf8mb4_unicode_ci NOT NULL,
                            trading_number varchar(255) COLLATE utf8mb4_unicode_ci,
                            trading_type varchar(32) COLLATE utf8mb4_unicode_ci,
                            trading_form text COLLATE utf8mb4_unicode_ci,
                            trading_org text COLLATE utf8mb4_unicode_ci,
                            trading_org_inn text(12) COLLATE utf8mb4_unicode_ci,
                            trading_org_contacts text COLLATE utf8mb4_bin,
                            msg_number varchar(255) COLLATE utf8mb4_unicode_ci,
                            case_number varchar(255) COLLATE utf8mb4_unicode_ci,
                            debtor_inn text(12) COLLATE utf8mb4_unicode_ci,
                            arbit_manager text COLLATE utf8mb4_unicode_ci,
                            arbit_manager_inn text(12) COLLATE utf8mb4_unicode_ci,
                            arbit_manager_org text COLLATE utf8mb4_unicode_ci,
                            status varchar(255) COLLATE utf8mb4_unicode_ci,
                            lot_id varchar(255) COLLATE utf8mb4_unicode_ci,
                            lot_link text COLLATE utf8mb4_unicode_ci,
                            lot_number smallint COLLATE utf8mb4_unicode_ci,
                            short_name mediumtext COLLATE utf8mb4_unicode_ci,
                            lot_info mediumtext COLLATE utf8mb4_unicode_ci,
                            property_information mediumtext COLLATE utf8mb4_unicode_ci,
                            start_date_requests timestamp,
                            end_date_requests timestamp,
                            start_date_trading timestamp,
                            end_date_trading timestamp,
                            start_price double,
                            step_price double,
                            periods mediumtext COLLATE utf8mb4_bin,
                            files mediumtext COLLATE utf8mb4_bin,
                            created_at timestamp,
                            CONSTRAINT CK_{tables['table_ptp_center']} UNIQUE (trading_id, trading_type, lot_number)

                                                                )

                            """)

    def store_db(self, item):
        self.curr.execute(
            f"""insert into {tables['table_ptp_center']}(data_origin,trading_id,trading_link,trading_number,trading_type,
    trading_form,trading_org,trading_org_inn,trading_org_contacts,msg_number,case_number,debtor_inn,arbit_manager,
    arbit_manager_inn,arbit_manager_org,status,lot_id,lot_link,lot_number,short_name,lot_info,property_information,
    start_date_requests,end_date_requests,start_date_trading,end_date_trading,start_price,step_price,periods,files,
    created_at) values (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,
    %s) ON DUPLICATE KEY UPDATE trading_id=VALUES(trading_id),
                                        data_origin=VALUES(data_origin),
                                        trading_link=VALUES(trading_link),
                                        trading_number=VALUES(trading_number),
                                        trading_type=VALUES(trading_type),
                                        trading_form=VALUES(trading_form),
                                        trading_org=VALUES(trading_org),
                                        trading_org_inn=VALUES(trading_org_inn),
                                        trading_org_contacts=VALUES(trading_org_contacts),
                                        msg_number=VALUES(msg_number),
                                        case_number = VALUES(case_number),
                                        debtor_inn = VALUES(debtor_inn),
                                        arbit_manager = VALUES(arbit_manager),
                                        arbit_manager_inn = VALUES(arbit_manager_inn),
                                        arbit_manager_org=VALUES(arbit_manager_org),
                                        status=VALUES(status),
                                        lot_id=VALUES(lot_id),
                                        lot_link=VALUES(lot_link),
                                        lot_number=VALUES(lot_number),
                                        short_name=VALUES(short_name),
                                        lot_info=VALUES(lot_info),
                                        property_information=VALUES(property_information),
                                        start_date_requests=VALUES(start_date_requests),
                                        end_date_requests=VALUES(end_date_requests), 
                                        start_date_trading=VALUES(start_date_trading), 
                                        end_date_trading=VALUES(end_date_trading),
                                        start_price=VALUES(start_price), 
                                        step_price=VALUES(step_price),
                                        periods=VALUES(periods), 
                                        files=VALUES(files),
                                        created_at=VALUES(created_at)
                                        """,
            (
                item['data_origin'],
                item['trading_id'],
                item['trading_link'],
                item['trading_number'],
                item['trading_type'],
                item['trading_form'],
                item['trading_org'],
                item['trading_org_inn'],
                item['trading_org_contacts'],
                item['msg_number'],
                item['case_number'],
                item['debtor_inn'],
                item['arbit_manager'],
                item['arbit_manager_inn'],
                item['arbit_manager_org'],
                item['status'],
                item['lot_id'],
                item['lot_link'],
                item['lot_number'],
                item['short_name'],
                item['lot_info'],
                item['property_information'],
                item['start_date_requests'],
                item['end_date_requests'],
                item['start_date_trading'],
                item['end_date_trading'],
                item['start_price'],
                item['step_price'],
                item['periods'],
                item['files'],
                item['created_at']

            ))

        self.conn.commit()

    def process_item(self, item, spider):
        self.store_db(item)
        try:
            return item
        except Error as error:
            return error


class RegtorgDbConnect(object):

    def __init__(self):
        self.db_config = read_db_config()
        self.conn = MySQLConnection(**self.db_config)
        self.curr = self.conn.cursor()
        self.create_table()

    def create_table(self):
        self.curr.execute(f"""CREATE TABLE IF NOT EXISTS {tables['table_regtorg']}(
                            id bigint AUTO_INCREMENT PRIMARY KEY,
                            data_origin text COLLATE utf8mb4_unicode_ci,
                            trading_id varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
                            trading_link text COLLATE utf8mb4_unicode_ci NOT NULL,
                            trading_number varchar(255) COLLATE utf8mb4_unicode_ci,
                            trading_type varchar(32) COLLATE utf8mb4_unicode_ci,
                            trading_form text COLLATE utf8mb4_unicode_ci,
                            trading_org text COLLATE utf8mb4_unicode_ci,
                            trading_org_inn text(12) COLLATE utf8mb4_unicode_ci,
                            trading_org_contacts text COLLATE utf8mb4_bin,
                            msg_number varchar(255) COLLATE utf8mb4_unicode_ci,
                            case_number varchar(255) COLLATE utf8mb4_unicode_ci,
                            debtor_inn text(12) COLLATE utf8mb4_unicode_ci,
                            arbit_manager text COLLATE utf8mb4_unicode_ci,
                            arbit_manager_inn text(12) COLLATE utf8mb4_unicode_ci,
                            arbit_manager_org text COLLATE utf8mb4_unicode_ci,
                            status varchar(255) COLLATE utf8mb4_unicode_ci,
                            lot_id varchar(255) COLLATE utf8mb4_unicode_ci,
                            lot_link text COLLATE utf8mb4_unicode_ci,
                            lot_number smallint COLLATE utf8mb4_unicode_ci,
                            short_name mediumtext COLLATE utf8mb4_unicode_ci,
                            lot_info mediumtext COLLATE utf8mb4_unicode_ci,
                            property_information mediumtext COLLATE utf8mb4_unicode_ci,
                            start_date_requests timestamp,
                            end_date_requests timestamp,
                            start_date_trading timestamp,
                            end_date_trading timestamp,
                            start_price double,
                            step_price double,
                            periods mediumtext COLLATE utf8mb4_bin,
                            files mediumtext COLLATE utf8mb4_bin,
                            created_at timestamp,
                            CONSTRAINT CK_{tables['table_regtorg']} UNIQUE (trading_id, trading_type, lot_number)

                                                                )

                            """)

    def store_db(self, item):
        self.curr.execute(
            f"""insert into {tables['table_regtorg']}(data_origin,trading_id,trading_link,trading_number,trading_type,
    trading_form,trading_org,trading_org_inn,trading_org_contacts,msg_number,case_number,debtor_inn,arbit_manager,
    arbit_manager_inn,arbit_manager_org,status,lot_id,lot_link,lot_number,short_name,lot_info,property_information,
    start_date_requests,end_date_requests,start_date_trading,end_date_trading,start_price,step_price,periods,files,
    created_at) values (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,
    %s) ON DUPLICATE KEY UPDATE trading_id=VALUES(trading_id),
                                        data_origin=VALUES(data_origin),
                                        trading_link=VALUES(trading_link),
                                        trading_number=VALUES(trading_number),
                                        trading_type=VALUES(trading_type),
                                        trading_form=VALUES(trading_form),
                                        trading_org=VALUES(trading_org),
                                        trading_org_inn=VALUES(trading_org_inn),
                                        trading_org_contacts=VALUES(trading_org_contacts),
                                        msg_number=VALUES(msg_number),
                                        case_number = VALUES(case_number),
                                        debtor_inn = VALUES(debtor_inn),
                                        arbit_manager = VALUES(arbit_manager),
                                        arbit_manager_inn = VALUES(arbit_manager_inn),
                                        arbit_manager_org=VALUES(arbit_manager_org),
                                        status=VALUES(status),
                                        lot_id=VALUES(lot_id),
                                        lot_link=VALUES(lot_link),
                                        lot_number=VALUES(lot_number),
                                        short_name=VALUES(short_name),
                                        lot_info=VALUES(lot_info),
                                        property_information=VALUES(property_information),
                                        start_date_requests=VALUES(start_date_requests),
                                        end_date_requests=VALUES(end_date_requests), 
                                        start_date_trading=VALUES(start_date_trading), 
                                        end_date_trading=VALUES(end_date_trading),
                                        start_price=VALUES(start_price), 
                                        step_price=VALUES(step_price),
                                        periods=VALUES(periods), 
                                        files=VALUES(files),
                                        created_at=VALUES(created_at)
                                        """,
            (
                item['data_origin'],
                item['trading_id'],
                item['trading_link'],
                item['trading_number'],
                item['trading_type'],
                item['trading_form'],
                item['trading_org'],
                item['trading_org_inn'],
                item['trading_org_contacts'],
                item['msg_number'],
                item['case_number'],
                item['debtor_inn'],
                item['arbit_manager'],
                item['arbit_manager_inn'],
                item['arbit_manager_org'],
                item['status'],
                item['lot_id'],
                item['lot_link'],
                item['lot_number'],
                item['short_name'],
                item['lot_info'],
                item['property_information'],
                item['start_date_requests'],
                item['end_date_requests'],
                item['start_date_trading'],
                item['end_date_trading'],
                item['start_price'],
                item['step_price'],
                item['periods'],
                item['files'],
                item['created_at']

            ))

        self.conn.commit()

    def process_item(self, item, spider):
        self.store_db(item)
        try:
            return item
        except Error as error:
            return error


class SeltimDbConnect(object):
    def __init__(self):
        self.db_config = read_db_config()
        self.conn = MySQLConnection(**self.db_config)
        self.curr = self.conn.cursor()
        self.create_table()

    def create_table(self):
        self.curr.execute(f"""CREATE TABLE IF NOT EXISTS {tables['table_seltim']}(
                            id bigint AUTO_INCREMENT PRIMARY KEY,
                            data_origin text COLLATE utf8mb4_unicode_ci,
                            trading_id varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
                            trading_link text COLLATE utf8mb4_unicode_ci NOT NULL,
                            trading_number varchar(255) COLLATE utf8mb4_unicode_ci,
                            trading_type varchar(32) COLLATE utf8mb4_unicode_ci,
                            trading_form text COLLATE utf8mb4_unicode_ci,
                            trading_org text COLLATE utf8mb4_unicode_ci,
                            trading_org_inn text(12) COLLATE utf8mb4_unicode_ci,
                            trading_org_contacts text COLLATE utf8mb4_bin,
                            msg_number varchar(255) COLLATE utf8mb4_unicode_ci,
                            case_number varchar(255) COLLATE utf8mb4_unicode_ci,
                            debtor_inn text(12) COLLATE utf8mb4_unicode_ci,
                            arbit_manager text COLLATE utf8mb4_unicode_ci,
                            arbit_manager_inn text(12) COLLATE utf8mb4_unicode_ci,
                            arbit_manager_org text COLLATE utf8mb4_unicode_ci,
                            status varchar(255) COLLATE utf8mb4_unicode_ci,
                            lot_id varchar(255) COLLATE utf8mb4_unicode_ci,
                            lot_link text COLLATE utf8mb4_unicode_ci,
                            lot_number smallint COLLATE utf8mb4_unicode_ci,
                            short_name mediumtext COLLATE utf8mb4_unicode_ci,
                            lot_info mediumtext COLLATE utf8mb4_unicode_ci,
                            property_information mediumtext COLLATE utf8mb4_unicode_ci,
                            start_date_requests timestamp,
                            end_date_requests timestamp,
                            start_date_trading timestamp,
                            end_date_trading timestamp,
                            start_price double,
                            step_price double,
                            periods mediumtext COLLATE utf8mb4_bin,
                            files mediumtext COLLATE utf8mb4_bin,
                            created_at timestamp,
                            CONSTRAINT CK_{tables['table_seltim']} UNIQUE (trading_id, trading_type, lot_number)

                                                                )

                            """)

    def store_db(self, item):
        self.curr.execute(
            f"""insert into {tables['table_seltim']}(data_origin,trading_id,trading_link,trading_number,trading_type,
    trading_form,trading_org,trading_org_inn,trading_org_contacts,msg_number,case_number,debtor_inn,arbit_manager,
    arbit_manager_inn,arbit_manager_org,status,lot_id,lot_link,lot_number,short_name,lot_info,property_information,
    start_date_requests,end_date_requests,start_date_trading,end_date_trading,start_price,step_price,periods,files,
    created_at) values (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,
    %s) ON DUPLICATE KEY UPDATE trading_id=VALUES(trading_id),
                                        data_origin=VALUES(data_origin),
                                        trading_link=VALUES(trading_link),
                                        trading_number=VALUES(trading_number),
                                        trading_type=VALUES(trading_type),
                                        trading_form=VALUES(trading_form),
                                        trading_org=VALUES(trading_org),
                                        trading_org_inn=VALUES(trading_org_inn),
                                        trading_org_contacts=VALUES(trading_org_contacts),
                                        msg_number=VALUES(msg_number),
                                        case_number = VALUES(case_number),
                                        debtor_inn = VALUES(debtor_inn),
                                        arbit_manager = VALUES(arbit_manager),
                                        arbit_manager_inn = VALUES(arbit_manager_inn),
                                        arbit_manager_org=VALUES(arbit_manager_org),
                                        status=VALUES(status),
                                        lot_id=VALUES(lot_id),
                                        lot_link=VALUES(lot_link),
                                        lot_number=VALUES(lot_number),
                                        short_name=VALUES(short_name),
                                        lot_info=VALUES(lot_info),
                                        property_information=VALUES(property_information),
                                        start_date_requests=VALUES(start_date_requests),
                                        end_date_requests=VALUES(end_date_requests), 
                                        start_date_trading=VALUES(start_date_trading), 
                                        end_date_trading=VALUES(end_date_trading),
                                        start_price=VALUES(start_price), 
                                        step_price=VALUES(step_price),
                                        periods=VALUES(periods), 
                                        files=VALUES(files),
                                        created_at=VALUES(created_at)
                                        """,
            (
                item['data_origin'],
                item['trading_id'],
                item['trading_link'],
                item['trading_number'],
                item['trading_type'],
                item['trading_form'],
                item['trading_org'],
                item['trading_org_inn'],
                item['trading_org_contacts'],
                item['msg_number'],
                item['case_number'],
                item['debtor_inn'],
                item['arbit_manager'],
                item['arbit_manager_inn'],
                item['arbit_manager_org'],
                item['status'],
                item['lot_id'],
                item['lot_link'],
                item['lot_number'],
                item['short_name'],
                item['lot_info'],
                item['property_information'],
                item['start_date_requests'],
                item['end_date_requests'],
                item['start_date_trading'],
                item['end_date_trading'],
                item['start_price'],
                item['step_price'],
                item['periods'],
                item['files'],
                item['created_at']

            ))

        self.conn.commit()

    def process_item(self, item, spider):
        self.store_db(item)
        try:
            return item
        except Error as error:
            return error


class TorgiDvDbConnect(object):

    def __init__(self):
        self.db_config = read_db_config()
        self.conn = MySQLConnection(**self.db_config)
        self.curr = self.conn.cursor()
        self.create_table()

    def create_table(self):
        self.curr.execute(f"""CREATE TABLE IF NOT EXISTS {tables['table_torgidv']}(
                            id bigint AUTO_INCREMENT PRIMARY KEY,
                            data_origin text COLLATE utf8mb4_unicode_ci,
                            trading_id varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
                            trading_link text COLLATE utf8mb4_unicode_ci NOT NULL,
                            trading_number varchar(255) COLLATE utf8mb4_unicode_ci,
                            trading_type varchar(32) COLLATE utf8mb4_unicode_ci,
                            trading_form text COLLATE utf8mb4_unicode_ci,
                            trading_org text COLLATE utf8mb4_unicode_ci,
                            trading_org_inn text(12) COLLATE utf8mb4_unicode_ci,
                            trading_org_contacts text COLLATE utf8mb4_bin,
                            msg_number varchar(255) COLLATE utf8mb4_unicode_ci,
                            case_number varchar(255) COLLATE utf8mb4_unicode_ci,
                            debtor_inn text(12) COLLATE utf8mb4_unicode_ci,
                            arbit_manager text COLLATE utf8mb4_unicode_ci,
                            arbit_manager_inn text(12) COLLATE utf8mb4_unicode_ci,
                            arbit_manager_org text COLLATE utf8mb4_unicode_ci,
                            status varchar(255) COLLATE utf8mb4_unicode_ci,
                            lot_id varchar(255) COLLATE utf8mb4_unicode_ci,
                            lot_link text COLLATE utf8mb4_unicode_ci,
                            lot_number smallint COLLATE utf8mb4_unicode_ci,
                            short_name mediumtext COLLATE utf8mb4_unicode_ci,
                            lot_info mediumtext COLLATE utf8mb4_unicode_ci,
                            property_information mediumtext COLLATE utf8mb4_unicode_ci,
                            start_date_requests timestamp,
                            end_date_requests timestamp,
                            start_date_trading timestamp,
                            end_date_trading timestamp,
                            start_price double,
                            step_price double,
                            periods mediumtext COLLATE utf8mb4_bin,
                            files mediumtext COLLATE utf8mb4_bin,
                            created_at timestamp,
                            CONSTRAINT CK_{tables['table_torgidv']} UNIQUE (trading_id, trading_type, lot_number)

                                                                )

                            """)

    def store_db(self, item):
        self.curr.execute(
            f"""insert into {tables['table_torgidv']}(data_origin,trading_id,trading_link,trading_number,trading_type,
    trading_form,trading_org,trading_org_inn,trading_org_contacts,msg_number,case_number,debtor_inn,arbit_manager,
    arbit_manager_inn,arbit_manager_org,status,lot_id,lot_link,lot_number,short_name,lot_info,property_information,
    start_date_requests,end_date_requests,start_date_trading,end_date_trading,start_price,step_price,periods,files,
    created_at) values (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,
    %s) ON DUPLICATE KEY UPDATE trading_id=VALUES(trading_id),
                                        data_origin=VALUES(data_origin),
                                        trading_link=VALUES(trading_link),
                                        trading_number=VALUES(trading_number),
                                        trading_type=VALUES(trading_type),
                                        trading_form=VALUES(trading_form),
                                        trading_org=VALUES(trading_org),
                                        trading_org_inn=VALUES(trading_org_inn),
                                        trading_org_contacts=VALUES(trading_org_contacts),
                                        msg_number=VALUES(msg_number),
                                        case_number = VALUES(case_number),
                                        debtor_inn = VALUES(debtor_inn),
                                        arbit_manager = VALUES(arbit_manager),
                                        arbit_manager_inn = VALUES(arbit_manager_inn),
                                        arbit_manager_org=VALUES(arbit_manager_org),
                                        status=VALUES(status),
                                        lot_id=VALUES(lot_id),
                                        lot_link=VALUES(lot_link),
                                        lot_number=VALUES(lot_number),
                                        short_name=VALUES(short_name),
                                        lot_info=VALUES(lot_info),
                                        property_information=VALUES(property_information),
                                        start_date_requests=VALUES(start_date_requests),
                                        end_date_requests=VALUES(end_date_requests), 
                                        start_date_trading=VALUES(start_date_trading), 
                                        end_date_trading=VALUES(end_date_trading),
                                        start_price=VALUES(start_price), 
                                        step_price=VALUES(step_price),
                                        periods=VALUES(periods), 
                                        files=VALUES(files),
                                        created_at=VALUES(created_at)
                                        """,
            (
                item['data_origin'],
                item['trading_id'],
                item['trading_link'],
                item['trading_number'],
                item['trading_type'],
                item['trading_form'],
                item['trading_org'],
                item['trading_org_inn'],
                item['trading_org_contacts'],
                item['msg_number'],
                item['case_number'],
                item['debtor_inn'],
                item['arbit_manager'],
                item['arbit_manager_inn'],
                item['arbit_manager_org'],
                item['status'],
                item['lot_id'],
                item['lot_link'],
                item['lot_number'],
                item['short_name'],
                item['lot_info'],
                item['property_information'],
                item['start_date_requests'],
                item['end_date_requests'],
                item['start_date_trading'],
                item['end_date_trading'],
                item['start_price'],
                item['step_price'],
                item['periods'],
                item['files'],
                item['created_at']

            ))

        self.conn.commit()

    def process_item(self, item, spider):
        self.store_db(item)
        try:
            return item
        except Error as error:
            return error


class TradePlaceVetpDbConnect(object):

    def __init__(self):
        self.db_config = read_db_config()
        self.conn = MySQLConnection(**self.db_config)
        self.curr = self.conn.cursor()
        self.create_table()

    def create_table(self):
        self.curr.execute(f"""CREATE TABLE IF NOT EXISTS {tables['table_trade_place_vetp']}(
                            id bigint AUTO_INCREMENT PRIMARY KEY,
                            data_origin text COLLATE utf8mb4_unicode_ci,
                            trading_id varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
                            trading_link text COLLATE utf8mb4_unicode_ci NOT NULL,
                            trading_number varchar(255) COLLATE utf8mb4_unicode_ci,
                            trading_type varchar(32) COLLATE utf8mb4_unicode_ci,
                            trading_form text COLLATE utf8mb4_unicode_ci,
                            trading_org text COLLATE utf8mb4_unicode_ci,
                            trading_org_inn text(12) COLLATE utf8mb4_unicode_ci,
                            trading_org_contacts text COLLATE utf8mb4_bin,
                            msg_number varchar(255) COLLATE utf8mb4_unicode_ci,
                            case_number varchar(255) COLLATE utf8mb4_unicode_ci,
                            debtor_inn text(12) COLLATE utf8mb4_unicode_ci,
                            arbit_manager text COLLATE utf8mb4_unicode_ci,
                            arbit_manager_inn text(12) COLLATE utf8mb4_unicode_ci,
                            arbit_manager_org text COLLATE utf8mb4_unicode_ci,
                            status varchar(255) COLLATE utf8mb4_unicode_ci,
                            lot_id varchar(255) COLLATE utf8mb4_unicode_ci,
                            lot_link text COLLATE utf8mb4_unicode_ci,
                            lot_number smallint COLLATE utf8mb4_unicode_ci,
                            short_name mediumtext COLLATE utf8mb4_unicode_ci,
                            lot_info mediumtext COLLATE utf8mb4_unicode_ci,
                            property_information mediumtext COLLATE utf8mb4_unicode_ci,
                            start_date_requests timestamp,
                            end_date_requests timestamp,
                            start_date_trading timestamp,
                            end_date_trading timestamp,
                            start_price double,
                            step_price double,
                            periods mediumtext COLLATE utf8mb4_bin,
                            files mediumtext COLLATE utf8mb4_bin,
                            created_at timestamp,
                            CONSTRAINT CK_{tables['table_trade_place_vetp']} UNIQUE (trading_id, trading_type, lot_number)

                                                                )

                            """)

    def store_db(self, item):
        self.curr.execute(
            f"""insert into {tables['table_trade_place_vetp']}(data_origin,trading_id,trading_link,trading_number,trading_type,
    trading_form,trading_org,trading_org_inn,trading_org_contacts,msg_number,case_number,debtor_inn,arbit_manager,
    arbit_manager_inn,arbit_manager_org,status,lot_id,lot_link,lot_number,short_name,lot_info,property_information,
    start_date_requests,end_date_requests,start_date_trading,end_date_trading,start_price,step_price,periods,files,
    created_at) values (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,
    %s) ON DUPLICATE KEY UPDATE trading_id=VALUES(trading_id),
                                        data_origin=VALUES(data_origin),
                                        trading_link=VALUES(trading_link),
                                        trading_number=VALUES(trading_number),
                                        trading_type=VALUES(trading_type),
                                        trading_form=VALUES(trading_form),
                                        trading_org=VALUES(trading_org),
                                        trading_org_inn=VALUES(trading_org_inn),
                                        trading_org_contacts=VALUES(trading_org_contacts),
                                        msg_number=VALUES(msg_number),
                                        case_number = VALUES(case_number),
                                        debtor_inn = VALUES(debtor_inn),
                                        arbit_manager = VALUES(arbit_manager),
                                        arbit_manager_inn = VALUES(arbit_manager_inn),
                                        arbit_manager_org=VALUES(arbit_manager_org),
                                        status=VALUES(status),
                                        lot_id=VALUES(lot_id),
                                        lot_link=VALUES(lot_link),
                                        lot_number=VALUES(lot_number),
                                        short_name=VALUES(short_name),
                                        lot_info=VALUES(lot_info),
                                        property_information=VALUES(property_information),
                                        start_date_requests=VALUES(start_date_requests),
                                        end_date_requests=VALUES(end_date_requests), 
                                        start_date_trading=VALUES(start_date_trading), 
                                        end_date_trading=VALUES(end_date_trading),
                                        start_price=VALUES(start_price), 
                                        step_price=VALUES(step_price),
                                        periods=VALUES(periods), 
                                        files=VALUES(files),
                                        created_at=VALUES(created_at)
                                        """,
            (
                item['data_origin'],
                item['trading_id'],
                item['trading_link'],
                item['trading_number'],
                item['trading_type'],
                item['trading_form'],
                item['trading_org'],
                item['trading_org_inn'],
                item['trading_org_contacts'],
                item['msg_number'],
                item['case_number'],
                item['debtor_inn'],
                item['arbit_manager'],
                item['arbit_manager_inn'],
                item['arbit_manager_org'],
                item['status'],
                item['lot_id'],
                item['lot_link'],
                item['lot_number'],
                item['short_name'],
                item['lot_info'],
                item['property_information'],
                item['start_date_requests'],
                item['end_date_requests'],
                item['start_date_trading'],
                item['end_date_trading'],
                item['start_price'],
                item['step_price'],
                item['periods'],
                item['files'],
                item['created_at']

            ))

        self.conn.commit()

    def process_item(self, item, spider):
        self.store_db(item)
        try:
            return item
        except Error as error:
            return error
