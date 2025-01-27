from mysql.connector import MySQLConnection, Error
from .utils.config import db_tables
from .python_mysql_dbconfig import read_db_config


class CrawlerZalogPipeline:
    def process_item(self, item, spider):

        for f in item.fields:
            if item == 'lot':
                item.setdefault(f, list())
            else:
                item.setdefault(f, None)
        return item


class ZalogSberConnect(object):
    def __init__(self):
        self.db_config = read_db_config()
        self.conn = MySQLConnection(**self.db_config, connect_timeout=600)

        self.curr = self.conn.cursor()
        self.set_wait_timeout(600)
        self.create_table()

    def set_wait_timeout(self, timeout):
        """Устанавливает wait_timeout для текущей сессии."""
        try:
            self.curr.execute(f"SET SESSION wait_timeout = {timeout};")
            print(f"Session wait_timeout set to {timeout} seconds.")
        except Error as err:
            print(f"Error setting wait_timeout: {err}")

    def create_table(self):
        self.curr.execute(f"""CREATE TABLE IF NOT EXISTS {db_tables['zalog_sber']}(
                            id bigint AUTO_INCREMENT PRIMARY KEY,
                            data_origin text COLLATE utf8mb4_unicode_ci,
                            trading_id varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
                            trading_link text COLLATE utf8mb4_unicode_ci NOT NULL,
                            trading_number varchar(255) COLLATE utf8mb4_unicode_ci,
                            trading_type varchar(32) COLLATE utf8mb4_unicode_ci,
                            trading_form text COLLATE utf8mb4_unicode_ci,
                            trading_org text COLLATE utf8mb4_unicode_ci,
                            trading_org_contacts text COLLATE utf8mb4_bin,
                            status varchar(255) COLLATE utf8mb4_unicode_ci,
                            index_ varchar(12) COLLATE utf8mb4_unicode_ci,
                            address text COLLATE utf8mb4_unicode_ci,
                            detailed_address text COLLATE utf8mb4_unicode_ci,
                            encumbrance text COLLATE utf8mb4_unicode_ci,
                            description_encumbrance text COLLATE utf8mb4_unicode_ci,
                            lot_number bigint COLLATE utf8mb4_unicode_ci,
                            category mediumtext COLLATE utf8mb4_bin,
                            short_name mediumtext COLLATE utf8mb4_unicode_ci,
                            lot_info mediumtext COLLATE utf8mb4_unicode_ci,
                            property_information mediumtext COLLATE utf8mb4_unicode_ci,
                            start_date_requests timestamp,
                            end_date_requests timestamp,
                            start_date_trading timestamp,
                            end_date_trading timestamp,
                            quantity smallint COLLATE utf8mb4_unicode_ci,
                            unit smallint COLLATE utf8mb4_unicode_ci,
                            deposit double,
                            start_price double,
                            step_price double,
                            min_price double,
                            periods mediumtext COLLATE utf8mb4_bin,
                            files mediumtext COLLATE utf8mb4_bin,
                            created_at timestamp,
                            CONSTRAINT CK_{db_tables['zalog_sber']} UNIQUE (trading_id, trading_type, lot_number)

                                                                )

                            """)

    def store_db(self, item):
        print(f'store_db: {self.conn.is_connected()}')
        self.curr.execute(
            f"""insert into {db_tables['zalog_sber']}(data_origin,trading_id,trading_link,trading_number,trading_type,
    trading_form,trading_org,trading_org_contacts,status,index_,address,detailed_address,encumbrance,description_encumbrance,
    lot_number,category,short_name,lot_info,property_information,start_date_requests,end_date_requests,start_date_trading,end_date_trading,
    quantity,unit,deposit,start_price,step_price,min_price,periods,files,created_at) values (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,
    %s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s) ON DUPLICATE KEY UPDATE trading_id=VALUES(trading_id),
                                        data_origin=VALUES(data_origin),
                                        trading_link=VALUES(trading_link),
                                        trading_number=VALUES(trading_number),
                                        trading_type=VALUES(trading_type),
                                        trading_form=VALUES(trading_form),
                                        trading_org=VALUES(trading_org),
                                        trading_org_contacts=VALUES(trading_org_contacts),
                                        status=VALUES(status),
                                        index_=VALUES(index_),
                                        address=VALUES(address),
                                        detailed_address=VALUES(detailed_address),
                                        encumbrance=VALUES(encumbrance),
                                        description_encumbrance=VALUES(description_encumbrance),
                                        lot_number=VALUES(lot_number),
                                        category=VALUES(category),
                                        short_name=VALUES(short_name),
                                        lot_info=VALUES(lot_info),
                                        property_information=VALUES(property_information),
                                        start_date_requests=VALUES(start_date_requests),
                                        end_date_requests=VALUES(end_date_requests),
                                        start_date_trading=VALUES(start_date_trading),
                                        end_date_trading=VALUES(end_date_trading),
                                        quantity=VALUES(quantity),
                                        unit=VALUES(unit),
                                        deposit=VALUES(deposit),
                                        start_price=VALUES(start_price),
                                        step_price=VALUES(step_price),
                                        min_price=VALUES(min_price),
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
                item['trading_org_contacts'],
                item['status'],
                item['index'],
                item['address'],
                item['detailed_address'],
                item['encumbrance'],
                item['description_encumbrance'],
                item['lot_number'],
                item['category'],
                item['short_name'],
                item['lot_info'],
                item['property_information'],
                item['start_date_requests'],
                item['end_date_requests'],
                item['start_date_trading'],
                item['end_date_trading'],
                item['quantity'],
                item['unit'],
                item['deposit'],
                item['start_price'],
                item['step_price'],
                item['min_price'],
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

# class ZalogRossConnect(object):
#
#     def __init__(self):
#         self.db_config = read_db_config()
#         self.conn = MySQLConnection(**self.db_config)
#         self.curr = self.conn.cursor()
#         self.create_table()
#
#     def create_table(self):
#         self.curr.execute(f"""CREATE TABLE IF NOT EXISTS {db_tables['zalog_ross']}(
#                             id bigint AUTO_INCREMENT PRIMARY KEY,
#                             data_origin text COLLATE utf8mb4_unicode_ci,
#                             trading_id varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
#                             trading_link text COLLATE utf8mb4_unicode_ci NOT NULL,
#                             trading_number varchar(255) COLLATE utf8mb4_unicode_ci,
#                             trading_type varchar(32) COLLATE utf8mb4_unicode_ci,
#                             trading_form text COLLATE utf8mb4_unicode_ci,
#                             trading_org text COLLATE utf8mb4_unicode_ci,
#                             trading_org_contacts text COLLATE utf8mb4_bin,
#                             status varchar(255) COLLATE utf8mb4_unicode_ci,
#                             index_ varchar(12) COLLATE utf8mb4_unicode_ci,
#                             address text COLLATE utf8mb4_unicode_ci,
#                             detailed_address text COLLATE utf8mb4_unicode_ci,
#                             encumbrance varchar(32) COLLATE utf8mb4_unicode_ci,
#                             description_encumbrance text COLLATE utf8mb4_unicode_ci,
#                             lot_number bigint COLLATE utf8mb4_unicode_ci,
#                             category mediumtext COLLATE utf8mb4_bin,
#                             short_name mediumtext COLLATE utf8mb4_unicode_ci,
#                             lot_info mediumtext COLLATE utf8mb4_unicode_ci,
#                             property_information mediumtext COLLATE utf8mb4_unicode_ci,
#                             start_date_requests timestamp,
#                             end_date_requests timestamp,
#                             start_date_trading timestamp,
#                             end_date_trading timestamp,
#                             quantity smallint COLLATE utf8mb4_unicode_ci,
#                             unit smallint COLLATE utf8mb4_unicode_ci,
#                             deposit double,
#                             start_price double,
#                             step_price double,
#                             min_price double,
#                             periods mediumtext COLLATE utf8mb4_bin,
#                             files mediumtext COLLATE utf8mb4_bin,
#                             created_at timestamp,
#                             CONSTRAINT CK_{db_tables['zalog_ross']} UNIQUE (trading_id, trading_type, lot_number)
#
#                                                                 )
#
#                             """)
#
#     def store_db(self, item):
#         self.curr.execute(
#             f"""insert into {db_tables['zalog_ross']}(data_origin,trading_id,trading_link,trading_number,trading_type,
#     trading_form,trading_org,trading_org_contacts,status,index_,address,detailed_address,encumbrance,description_encumbrance,
#     lot_number,category,short_name,lot_info,property_information,start_date_requests,end_date_requests,start_date_trading,end_date_trading,
#     quantity,unit,deposit,start_price,step_price,min_price,periods,files,created_at) values (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,
#     %s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s) ON DUPLICATE KEY UPDATE trading_id=VALUES(trading_id),
#                                         data_origin=VALUES(data_origin),
#                                         trading_link=VALUES(trading_link),
#                                         trading_number=VALUES(trading_number),
#                                         trading_type=VALUES(trading_type),
#                                         trading_form=VALUES(trading_form),
#                                         trading_org=VALUES(trading_org),
#                                         trading_org_contacts=VALUES(trading_org_contacts),
#                                         status=VALUES(status),
#                                         index_=VALUES(index_),
#                                         address=VALUES(address),
#                                         detailed_address=VALUES(detailed_address),
#                                         encumbrance=VALUES(encumbrance),
#                                         description_encumbrance=VALUES(description_encumbrance),
#                                         lot_number=VALUES(lot_number),
#                                         category=VALUES(category),
#                                         short_name=VALUES(short_name),
#                                         lot_info=VALUES(lot_info),
#                                         property_information=VALUES(property_information),
#                                         start_date_requests=VALUES(start_date_requests),
#                                         end_date_requests=VALUES(end_date_requests),
#                                         start_date_trading=VALUES(start_date_trading),
#                                         end_date_trading=VALUES(end_date_trading),
#                                         quantity=VALUES(quantity),
#                                         unit=VALUES(unit),
#                                         deposit=VALUES(deposit),
#                                         start_price=VALUES(start_price),
#                                         step_price=VALUES(step_price),
#                                         min_price=VALUES(min_price),
#                                         periods=VALUES(periods),
#                                         files=VALUES(files),
#                                         created_at=VALUES(created_at)
#                                         """,
#             (
#                 item['data_origin'],
#                 item['trading_id'],
#                 item['trading_link'],
#                 item['trading_number'],
#                 item['trading_type'],
#                 item['trading_form'],
#                 item['trading_org'],
#                 item['trading_org_contacts'],
#                 item['status'],
#                 item['index'],
#                 item['address'],
#                 item['detailed_address'],
#                 item['encumbrance'],
#                 item['description_encumbrance'],
#                 item['lot_number'],
#                 item['category'],
#                 item['short_name'],
#                 item['lot_info'],
#                 item['property_information'],
#                 item['start_date_requests'],
#                 item['end_date_requests'],
#                 item['start_date_trading'],
#                 item['end_date_trading'],
#                 item['quantity'],
#                 item['unit'],
#                 item['deposit'],
#                 item['start_price'],
#                 item['step_price'],
#                 item['min_price'],
#                 item['periods'],
#                 item['files'],
#                 item['created_at']
#
#             ))
#
#         self.conn.commit()
#
#     def process_item(self, item, spider):
#         self.store_db(item)
#         try:
#             return item
#         except Error as error:
#             return error
