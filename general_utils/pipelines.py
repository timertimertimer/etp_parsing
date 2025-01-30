import logging
from mysql.connector import MySQLConnection, Error, ProgrammingError, OperationalError

from .location import Region
from .python_mysql_dbconfig import read_db_config

logger = logging.getLogger(__name__)


class BasePipeline:
    def __init__(self, table_name: str, unique_co: list[str]):
        self.curr = None
        self.conn = None
        self.db_config = read_db_config()
        self.table_name = table_name
        self.unique_co = unique_co
        self.create_connection()
        self.create_table()

    @classmethod
    def from_crawler(cls, crawler):
        with_domain = getattr(crawler.spider, 'domain', '')
        table_name = crawler.settings.get(
            "TABLE_NAME",
            f'lots_{crawler.spider.name}' + (
                f'_{with_domain}' if with_domain and with_domain not in crawler.spider.name else ''
            )
        )
        return cls(
            table_name=table_name,
            unique_co=crawler.settings.get("UNIQUE_CO", ['trading_id']),
        )

    def create_connection(self):
        logger.info(f'Creating connection. Table {self.table_name}')
        self.conn = MySQLConnection(**self.db_config)
        self.curr = self.conn.cursor()
        self.set_wait_timeout(1800)

    def set_wait_timeout(self, timeout):
        """Устанавливает wait_timeout для текущей сессии."""
        try:
            self.curr.execute(f"SET SESSION wait_timeout = {timeout};")
            logger.info(f"Session wait_timeout set to {timeout} seconds.")
        except Error as err:
            logger.warning(f"Error setting wait_timeout: {err}")

    def create_table(self):
        pass

    def store_db(self, item):
        pass

    def process_item(self, item, spider):
        for f in item.fields:
            if item == 'lot':
                item.setdefault(f, list())
            else:
                item.setdefault(f, None)
        for _ in range(5):
            try:
                self.store_db(item)
                break
            except (ProgrammingError, OperationalError) as e:
                if 'MySQL Connection not available' in e.args[1] or 'Lost connection to MySQL server' in e.args[1]:
                    self.create_connection()
                    self.store_db(item)
            except Exception as e:
                logger.error(e)
        try:
            return item
        except Error as error:
            return error

    def spider_closed(self, spider):
        Region.save_new_regions_to_db()


class ETPBankruptPipeline(BasePipeline):
    def create_table(self):
        self.curr.execute(
            f"""CREATE TABLE IF NOT EXISTS {self.table_name}(
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
                address varchar(255) COLLATE utf8mb4_unicode_ci,
                region varchar(255) COLLATE utf8mb4_unicode_ci,
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
                CONSTRAINT CK_{self.table_name} UNIQUE ({', '.join(self.unique_co)}))
                """
        )
        logger.info(f'Table {self.table_name} created')

    def store_db(self, item):
        self.curr.execute(
            f"""insert into {self.table_name}(data_origin,trading_id,trading_link,trading_number,trading_type,
trading_form,trading_org,trading_org_inn,trading_org_contacts,msg_number,case_number,debtor_inn,address,region,arbit_manager,
arbit_manager_inn,arbit_manager_org,status,lot_id,lot_link,lot_number,short_name,lot_info,property_information,
start_date_requests,end_date_requests,start_date_trading,end_date_trading,start_price,step_price,periods,files,
created_at) values (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,
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
                                    address = VALUES(address),
                                    region = VALUES(region),
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
                item['address'],
                item['region'],
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


class ETPNonBankruptPipeline(BasePipeline):
    def create_table(self):
        self.curr.execute(f"""CREATE TABLE IF NOT EXISTS {self.table_name}(
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
                                address varchar(255) COLLATE utf8mb4_unicode_ci,
                                region varchar(255) COLLATE utf8mb4_unicode_ci,
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
                                CONSTRAINT CK_{self.table_name} UNIQUE ({', '.join(self.unique_co)}))
        """)

    def store_db(self, item):
        self.curr.execute(
            f"""insert into {self.table_name}(data_origin,trading_id,trading_link,trading_number,trading_type,
            trading_form,trading_org,trading_org_contacts,status,index_,address,region,encumbrance,description_encumbrance,
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
                                                region=VALUES(region),
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
                item['region'],
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
