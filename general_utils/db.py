import logging

from mysql.connector import MySQLConnection

from general_utils.config import format_parse_date
from general_utils.location import Region
from general_utils.python_mysql_dbconfig import read_db_config

logger = logging.getLogger(__name__)


class DBHelper:

    def __init__(self, table_name: str = None):
        self.db_config = read_db_config()
        self.conn = MySQLConnection(**self.db_config)
        self.curr = self.conn.cursor()
        self.table_name = table_name

    def get_latest_lot(self, keys: list[str] = None, day: int = 30) -> list or None:
        keys = keys or ['trading_link']
        try:
            self.curr.execute(
                f""" SELECT {", ".join(keys)} FROM {self.table_name} where created_at >= "{format_parse_date(day, '%Y-%m-%d %H:%M:%S')}" """
            )
            data = self.curr.fetchall()
            return data
        except Exception as e:
            logger.error(f'db.get_latest_lot ({self.table_name}) :: {e}')
            return list()

    def get_lots_by_table(self, table_name: str):
        try:
            self.curr.execute(f"SELECT * FROM {table_name}")
            data = self.curr.fetchall()
            return data
        except Exception as e:
            logger.error(f'db.get_lots_by_table ({table_name}) :: {e}')
            return list()

    def get_all_addresses(self):
        try:
            # Query to get all table names starting with 'lots_'
            self.curr.execute("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = DATABASE() 
                AND table_name LIKE 'lots_%'
            """)
            tables = self.curr.fetchall()

            # If no tables match, return an empty list
            if not tables:
                logger.info("No tables starting with 'lots_' found.")
                return []

            # Generate the dynamic SQL query to select non-null addresses from all 'lots_' tables
            queries = [
                f"SELECT address FROM {table[0]} WHERE address IS NOT NULL"
                for table in tables
            ]
            final_query = " UNION ALL ".join(queries)

            # Execute the dynamic query
            self.curr.execute(final_query)
            data = self.curr.fetchall()
            unique_addresses = list(set(address[0] for address in data))  # Extracting unique addresses from results
            return unique_addresses
        except Exception as e:
            logger.error(f'db.get_all_addresses :: {e}')
            return list()

    def update_regions(self):
        try:
            # Получаем список всех таблиц, начинающихся на 'lots_'
            self.curr.execute("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = DATABASE() 
                AND table_name LIKE 'lots_%'
            """)
            tables = self.curr.fetchall()

            if not tables:
                logger.info("No tables starting with 'lots_' found.")
                return

            for table in tables:
                table_name = table[0]

                # Получаем все уникальные адреса из таблицы
                self.curr.execute(f"SELECT DISTINCT address FROM {table_name} WHERE address IS NOT NULL")
                addresses = self.curr.fetchall()

                if not addresses:
                    continue

                for address in addresses:
                    address_value = address[0]
                    region = Region.get_region(address_value)  # Получаем регион

                    # Обновляем запись в базе
                    self.curr.execute(
                        f"""
                        UPDATE {table_name} 
                        SET region = %s 
                        WHERE address = %s
                        """,
                        (region, address_value)
                    )

                # Фиксируем изменения в БД
                self.conn.commit()
                logger.info(f"Updated regions in {table_name}")

        except Exception as e:
            logger.error(f'db.update_regions :: {e}')
            self.conn.rollback()


if __name__ == '__main__':
    for address in DBHelper().get_all_addresses():
        fr = Region.get_region(address)

