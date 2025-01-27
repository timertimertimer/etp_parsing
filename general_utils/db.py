import logging

from mysql.connector import MySQLConnection

from general_utils.config import format_parse_date
from general_utils.python_mysql_dbconfig import read_db_config

logger = logging.getLogger(__name__)


class DBHelper:

    def __init__(self, table_name: str):
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
